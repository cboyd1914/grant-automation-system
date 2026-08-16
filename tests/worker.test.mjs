import assert from 'node:assert/strict'
import test from 'node:test'

import worker from '../src/index.mjs'

const expectedRoutes = [
  ['/', 'status', 'Grant Discovery API - Working!'],
  ['/health', 'status', 'healthy'],
  ['/api/status', 'api_status', 'operational'],
  ['/api/grants-info', 'success', true]
]

for (const [pathname, responseKey, expectedValue] of expectedRoutes) {
  test(`GET ${pathname} returns the existing API contract`, async () => {
    const response = await worker.fetch(new Request(`https://grants.theapexresolution.com${pathname}`))
    const body = await response.json()

    assert.equal(response.status, 200)
    assert.equal(body[responseKey], expectedValue)
    assert.match(response.headers.get('content-type'), /^application\/json/)
  })
}

test('unknown paths remain explicit 404 responses', async () => {
  const response = await worker.fetch(new Request('https://grants.theapexresolution.com/missing'))
  const body = await response.json()

  assert.equal(response.status, 404)
  assert.equal(body.error, 'Not found')
})

test('unsupported methods return 405', async () => {
  const response = await worker.fetch(new Request('https://grants.theapexresolution.com/', {
    method: 'POST'
  }))

  assert.equal(response.status, 405)
})

test('HTTP requests redirect directly to HTTPS', async () => {
  const response = await worker.fetch(new Request('http://grants.theapexresolution.com/health'))

  assert.equal(response.status, 301)
  assert.equal(response.headers.get('location'), 'https://grants.theapexresolution.com/health')
})
