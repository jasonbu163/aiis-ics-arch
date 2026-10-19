/** 受控验证构建：不读取真实env，沿用产品Vue/CU解析；端口由验证命令显式覆盖。 */
import { mergeConfig, defineConfig } from 'vite'
import base from './vite.config'
import process from 'node:process'
const flag=process.argv.lastIndexOf('--port')
const port=flag<0?undefined:Number(process.argv[flag+1])
if(port!==undefined&&(!Number.isInteger(port)||port<1024||port>65535))throw new Error('validation_port_invalid')
export default mergeConfig(base, defineConfig({envDir:false,server:port===undefined?{}:{port,strictPort:true},build:{outDir:'/private/tmp/daa-002-validation-dist',emptyOutDir:false}}))
