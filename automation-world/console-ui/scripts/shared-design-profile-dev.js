/** CU 私有 Vite 开发通道：loopback/同源/会话保护，固定公共文件版本检查与进程内串行应用。 */
import { randomBytes } from 'node:crypto'
import { normalizeProfile } from '../src/ui/design-profile.js'
import { readSharedRevision, writeSharedProfile } from './shared-design-profile.js'

const endpoint = '/__cu/design-profile'
const hosts = new Set(['localhost:15193', '127.0.0.1:15193', '[::1]:15193'])
const limit = 64 * 1024
const failure = (status, code) => Object.assign(new Error(code), { status, code })
function loopback(address = '') {
  return address === '::1' || /^127(?:\.\d{1,3}){3}$/.test(address) || /^::ffff:127(?:\.\d{1,3}){3}$/i.test(address)
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0
    let rejected = false
    const chunks = []
    req.on('data', chunk => {
      size += chunk.length
      if (rejected) return
      if (size > limit) { rejected = true; chunks.length = 0; reject(failure(413, 'invalid_request')); return }
      chunks.push(chunk)
    })
    req.on('end', () => { if (!rejected) resolve(Buffer.concat(chunks).toString('utf8')) })
    req.on('error', () => reject(failure(400, 'invalid_request')))
    req.on('aborted', () => reject(failure(400, 'invalid_request')))
  })
}
export function sharedDesignProfileDev() {
  return {
    name: 'cu-shared-design-profile',
    apply: 'serve',
    configureServer(server) {
      const token = randomBytes(32).toString('hex')
      let queue = Promise.resolve()
      // configureServer 前置注册，私有端点拒绝请求不得透传到通用 CORS/static。
      server.middlewares.use((req, res, next) => {
        if (req.url?.split('?')[0] !== endpoint) { next(); return }
        res.setHeader('Content-Type', 'application/json; charset=utf-8')
        res.setHeader('Cache-Control', 'no-store')
        const reply = (status, body) => { res.statusCode = status; res.end(JSON.stringify(body)) }
        void (async () => {
          const host = req.headers.host
          const origin = req.headers.origin
          if (!loopback(req.socket.remoteAddress) || !hosts.has(host)) throw failure(403, 'protected')
          if (origin !== undefined && origin !== `http://${host}`) throw failure(403, 'protected')
          if (req.method === 'GET') {
            if (req.headers['x-cu-request'] !== 'design-profile') throw failure(403, 'protected')
            await queue.catch(() => {})
            reply(200, { revision: await readSharedRevision(), token }); return
          }
          if (req.method !== 'POST') throw failure(405, 'protected')
          if (origin !== `http://${host}` || req.headers['x-cu-session'] !== token) throw failure(403, 'protected')
          if (req.headers['content-type']?.split(';')[0].trim().toLowerCase() !== 'application/json') throw failure(415, 'invalid_request')
          let body
          try {
            body = JSON.parse(await readBody(req))
          } catch (error) { throw error.status ? error : failure(400, 'invalid_request') }
          if (!body || typeof body !== 'object' || Array.isArray(body) || Object.keys(body).length !== 2 || !Object.hasOwn(body, 'profile') || !Object.hasOwn(body, 'expectedRevision') || typeof body.expectedRevision !== 'string' || !/^[a-f0-9]{64}$/.test(body.expectedRevision)) throw failure(400, 'invalid_request')
          let profile
          try { profile = normalizeProfile(body.profile) }
          catch { throw failure(400, 'invalid_profile') }
          const operation = queue.catch(() => {}).then(() => writeSharedProfile(profile, body.expectedRevision))
          queue = operation
          const revision = await operation
          reply(200, { revision })
        })().catch(error => reply(error.status || (error.code === 'conflict' ? 409 : 500), { code: error.code === 'conflict' ? 'conflict' : error.status ? error.code : 'io_failed' }))
      })
    }
  }
}
