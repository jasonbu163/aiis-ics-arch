// ARCH-AW-009 r2：互斥分支汇合后的字段选择和连线规则。
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { canConnect, createNode, fresh, outputs } from '../../src/app/flow-editor/model.ts'

const edge = (from_node_id, from_port, to_node_id) => ({from_node_id, from_port, to_node_id})
function draft() {
  const doc = fresh()
  doc.flow.entry_node_id = 'read'
  doc.flow.nodes = [
    createNode('read', 'read'),
    createNode('condition', 'branch'),
    createNode('get', 'get'),
    createNode('get', 'branch_only'),
    createNode('end', 'end')
  ]
  doc.flow.edges = [edge('read', 'next', 'branch'), edge('branch', 'true', 'get'), edge('get', 'next', 'end')]
  return doc
}

test('selects outputs from the same parent reached via two exclusive ports', () => {
  const doc = draft()
  const merge = edge('branch', 'false', 'get')
  assert.equal(canConnect(doc, merge), true)
  doc.flow.edges.push(merge)
  assert.equal(canConnect(doc, merge), false)
  assert.deepEqual(outputs(doc, 'get'), [
    { id: 'branch', field: 'matched', type: 'boolean', kind: 'condition' },
    { id: 'read', field: 'value', type: 'int16', kind: 'read' }
  ])
})

test('excludes a field produced exclusively on one path into a reconvergence', () => {
  const doc = draft()
  doc.flow.edges.push(edge('branch', 'false', 'branch_only'))
  const merge = edge('branch_only', 'next', 'get')
  assert.equal(canConnect(doc, merge), true)
  doc.flow.edges.push(merge)
  assert.deepEqual(outputs(doc, 'get').map(option => option.id), ['branch', 'read'])
  assert.deepEqual(outputs(doc, 'read'), [])
  assert.equal(canConnect(doc, edge('end', 'next', 'branch')), false)
  assert.equal(canConnect(doc, edge('get', 'next', 'read')), false)
})
