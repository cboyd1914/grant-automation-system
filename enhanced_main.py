#!/usr/bin/env python3
"""
Enhanced Grant Application for Google App Engine
Business-focused grant discovery with minority-owned business targeting
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, jsonify, request
import requests

# Configure logging for App Engine
if os.getenv('GAE_ENV', '').startswith('standard'):
    # Production on App Engine
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
    logging.getLogger().setLevel(logging.INFO)
else:
    # Local development
    logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)
logger = logging.getLogger(__name__)

# Enhanced configuration for business-specific targeting
GRANTS_API_URL = "https://api.grants.gov/v1/api/search2"

# Business-specific search keywords
BUSINESS_KEYWORDS = {
    'minority_business': ['minority-owned', 'black-owned', 'diverse entrepreneurs', 'BIPOC'],
    'financial_literacy': ['financial literacy', 'economic empowerment', 'student loan', 'financial education'],
    'technology': ['artificial intelligence', 'AI', 'technology training', 'digital equity'],
    'youth_empowerment': ['youth development', 'STEM education', 'educational technology']
}

# Targeted grant opportunities
TARGETED_GRANTS = {
    'NAACP Power Forward Grant': {
        'amount': 'Up to $50,000',
        'focus': 'Black-owned businesses scaling impactful solutions',
        'url': 'https://www.naacp.org/powerforward',
        'category': 'minority_business'
    },
    'Google for Startups Black Founders Fund': {
        'amount': '$50,000-$150,000, no equity required',
        'focus': 'Black-led startups in tech',
        'url': 'https://startup.google.com/programs/black-founders-fund',
        'category': 'technology'
    },
    'Black Ambition Prize': {
        'amount': 'Up to $1M',
        'focus': 'Black and Latinx founders with scalable solutions',
        'url': 'https://blackambition.org',
        'category': 'youth_empowerment'
    },
    'Comcast RISE Investment Fund': {
        'amount': '$10,000-$20,000 + marketing support',
        'focus': 'Small businesses owned by people of color',
        'url': 'https://www.comcastrise.com',
        'category': 'minority_business'
    }
}

@app.route('/')
def home():
    """Enhanced home page with business focus"""
    return jsonify({
        "status": "Enhanced Grant Discovery API",
        "version": "2.0.0",
        "business_focus": [
            "Minority-owned business development",
            "Financial literacy & economic empowerment",
            "Technology & workforce development", 
            "Youth AI empowerment & digital inclusion"
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv('GAE_ENV', 'local'),
        "endpoints": [
            "/health",
            "/api/grants",
            "/api/discover",
            "/api/targeted-grants",
            "/api/business-analysis"
        ]
    })

@app.route('/health')
def health():
    """Health check endpoint for App Engine"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "enhanced-grant-application",
            "environment": os.getenv('GAE_ENV', 'local'),
            "business_targeting": "active"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204

@app.route('/api/grants')
def api_grants():
    """Enhanced grants API with business-specific targeting"""
    try:
        # Get query parameters
        category = request.args.get('category', 'minority_business')
        limit = min(int(request.args.get('limit', 10)), 25)
        
        logger.info(f"Enhanced grants API called with category: {category}, limit: {limit}")
        
        # Get keywords for the specified category
        keywords = BUSINESS_KEYWORDS.get(category, BUSINESS_KEYWORDS['minority_business'])
        
        all_grants = []
        
        # Search for each keyword in the category
        for keyword in keywords[:2]:  # Limit to 2 keywords to avoid timeout
            payload = {
                "rows": limit,
                "keyword": keyword,
                "oppStatuses": "forecasted|posted",
                "startRecordNum": 0
            }
            
            try:
                response = requests.post(
                    GRANTS_API_URL,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('errorcode') == 0:
                        grants = data.get('data', {}).get('oppHits', [])
                        
                        for grant in grants:
                            # Enhanced grant processing with business scoring
                            enhanced_grant = {
                                'id': grant.get('id'),
                                'title': grant.get('title'),
                                'agency': grant.get('agencyName') or grant.get('agencyCode'),
                                'status': grant.get('oppStatus'),
                                'open_date': grant.get('openDate'),
                                'close_date': grant.get('closeDate'),
                                'category': category,
                                'discovery_keyword': keyword,
                                'business_alignment_score': calculate_business_alignment(grant, category),
                                'strategic_priority': calculate_strategic_priority(grant, category),
                                'url': f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={grant.get('id')}"
                            }
                            all_grants.append(enhanced_grant)
                
            except Exception as e:
                logger.error(f"Error searching for keyword '{keyword}': {str(e)}")
        
        # Remove duplicates and sort by business alignment
        unique_grants = []
        seen_ids = set()
        
        for grant in all_grants:
            if grant['id'] not in seen_ids:
                seen_ids.add(grant['id'])
                unique_grants.append(grant)
        
        # Sort by business alignment score
        unique_grants.sort(key=lambda x: x['business_alignment_score'], reverse=True)
        
        return jsonify({
            "success": True,
            "category": category,
            "count": len(unique_grants),
            "grants": unique_grants[:limit],
            "business_focus": BUSINESS_KEYWORDS[category],
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced grants API: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/targeted-grants')
def api_targeted_grants():
    """API endpoint for curated targeted grants"""
    try:
        category_filter = request.args.get('category')
        
        filtered_grants = []
        for name, info in TARGETED_GRANTS.items():
            if not category_filter or info['category'] == category_filter:
                grant_info = {
                    'name': name,
                    'amount': info['amount'],
                    'focus': info['focus'],
                    'url': info['url'],
                    'category': info['category'],
                    'priority': 'HIGH',
                    'source': 'curated_list',
                    'business_alignment_score': 8.0  # High score for targeted grants
                }
                filtered_grants.append(grant_info)
        
        return jsonify({
            "success": True,
            "count": len(filtered_grants),
            "targeted_grants": filtered_grants,
            "categories": list(BUSINESS_KEYWORDS.keys()),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in targeted grants API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/business-analysis')
def api_business_analysis():
    """Business-specific grant analysis endpoint"""
    try:
        analysis = {
            "business_profile": {
                "type": "Minority-owned LLC",
                "focus_areas": [
                    "Financial literacy and student loan coaching",
                    "AI consulting and technology services",
                    "Youth empowerment and STEM education",
                    "Community economic development"
                ],
                "target_locations": ["St. Louis, MO", "Kansas City, MO", "Dallas, TX", "Chicago, IL"]
            },
            "grant_categories": {
                "minority_business": {
                    "description": "Grants specifically for Black-owned and minority-led businesses",
                    "keywords": BUSINESS_KEYWORDS['minority_business'],
                    "priority": "CRITICAL"
                },
                "financial_literacy": {
                    "description": "Funding for financial education and economic empowerment",
                    "keywords": BUSINESS_KEYWORDS['financial_literacy'],
                    "priority": "HIGH"
                },
                "technology": {
                    "description": "Tech development and AI consulting opportunities",
                    "keywords": BUSINESS_KEYWORDS['technology'],
                    "priority": "HIGH"
                },
                "youth_empowerment": {
                    "description": "Youth development and STEM education funding",
                    "keywords": BUSINESS_KEYWORDS['youth_empowerment'],
                    "priority": "MEDIUM"
                }
            },
            "targeted_opportunities": len(TARGETED_GRANTS),
            "recommendation": "Focus on minority business and technology grants for highest alignment",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify({
            "success": True,
            "business_analysis": analysis
        })
        
    except Exception as e:
        logger.error(f"Error in business analysis API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/discover')
def api_discover():
    """Enhanced discovery API with business targeting"""
    try:
        logger.info("Enhanced discovery API called")
        
        discovery_results = {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "business_targeting": {
                "minority_business_sources": ["NAACP", "Comcast RISE", "Wells Fargo"],
                "financial_literacy_sources": ["Bank of America Foundation", "CDFIs", "United Way"],
                "technology_sources": ["Google for Startups", "SBA", "EDA"],
                "youth_empowerment_sources": ["Black Ambition", "Chan Zuckerberg", "Best Buy"]
            },
            "sources": [
                {
                    "name": "grants.gov",
                    "status": "active",
                    "business_targeting": "enabled",
                    "last_updated": datetime.utcnow().isoformat()
                },
                {
                    "name": "targeted_grants",
                    "status": "active", 
                    "count": len(TARGETED_GRANTS),
                    "last_updated": datetime.utcnow().isoformat()
                }
            ],
            "summary": {
                "total_sources": 2,
                "active_sources": 2,
                "business_categories": len(BUSINESS_KEYWORDS),
                "targeted_grants": len(TARGETED_GRANTS),
                "last_discovery": datetime.utcnow().isoformat()
            }
        }
        
        return jsonify(discovery_results)
        
    except Exception as e:
        logger.error(f"Error in enhanced discovery: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def calculate_business_alignment(grant, category):
    """Calculate business alignment score for a grant"""
    score = 0.0
    title = (grant.get('title') or '').lower()
    
    # Category-specific scoring
    if category == 'minority_business':
        if any(term in title for term in ['minority', 'black', 'diverse', 'underrepresented']):
            score += 3.0
    elif category == 'financial_literacy':
        if any(term in title for term in ['financial', 'economic', 'loan', 'literacy']):
            score += 2.5
    elif category == 'technology':
        if any(term in title for term in ['technology', 'ai', 'artificial', 'digital']):
            score += 2.5
    elif category == 'youth_empowerment':
        if any(term in title for term in ['youth', 'education', 'stem', 'student']):
            score += 2.0
    
    # Agency bonus
    agency = (grant.get('agencyCode') or '').lower()
    if any(code in agency for code in ['sba', 'eda', 'doe']):
        score += 1.0
    
    return round(score, 2)

def calculate_strategic_priority(grant, category):
    """Calculate strategic priority level"""
    alignment_score = calculate_business_alignment(grant, category)
    
    if alignment_score >= 3.0:
        return "HIGH"
    elif alignment_score >= 2.0:
        return "MEDIUM"
    else:
        return "LOW"

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/health", "/api/grants", "/api/discover", "/api/targeted-grants", "/api/business-analysis"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

@app.before_request
def log_request():
    """Log all requests"""
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

