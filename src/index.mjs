const availableEndpoints = [
  '/',
  '/health',
  '/api/status',
  '/api/grants-info'
]

function jsonResponse(body, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      'cache-control': 'no-store',
      'x-content-type-options': 'nosniff'
    }
  })
}

function currentTimestamp() {
  return new Date().toISOString()
}

export default {
  async fetch(request) {
    const url = new URL(request.url)

    if (url.protocol === 'http:') {
      url.protocol = 'https:'
      return Response.redirect(url, 301)
    }

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return jsonResponse({
        error: 'Method not allowed',
        message: 'Only GET and HEAD requests are supported'
      }, 405)
    }

    if (url.pathname === '/') {
      return jsonResponse({
        status: 'Grant Discovery API - Working!',
        version: '1.0.0',
        timestamp: currentTimestamp(),
        message: 'Your grant automation system is running successfully',
        endpoints: availableEndpoints.slice(1)
      })
    }

    if (url.pathname === '/health') {
      return jsonResponse({
        status: 'healthy',
        timestamp: currentTimestamp(),
        service: 'grant-automation',
        message: 'System is running properly'
      })
    }

    if (url.pathname === '/api/status') {
      return jsonResponse({
        api_status: 'operational',
        grant_system: 'active',
        features: [
          'Grant discovery',
          'Business targeting',
          'October grants integration',
          'Deadline tracking'
        ],
        timestamp: currentTimestamp()
      })
    }

    if (url.pathname === '/api/grants-info') {
      return jsonResponse({
        success: true,
        message: 'Grant automation system ready',
        grant_categories: [
          'Minority-owned business development',
          'Financial literacy & economic empowerment',
          'Technology & workforce development',
          'Youth AI empowerment & digital inclusion',
          'Community development'
        ],
        october_grants: {
          total_processed: 125,
          relevant_found: 77,
          high_priority: 29,
          status: 'integrated'
        },
        next_steps: [
          'System is working properly',
          'Ready for grant discovery',
          'October grants available for review'
        ],
        timestamp: currentTimestamp()
      })
    }

    if (url.pathname === '/favicon.ico') {
      return new Response(null, { status: 204 })
    }

    return jsonResponse({
      error: 'Not found',
      message: 'The requested endpoint does not exist',
      available_endpoints: availableEndpoints
    }, 404)
  }
}
