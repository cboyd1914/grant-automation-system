#!/usr/bin/env python3
"""
Updated Enhanced Grant Configuration
Incorporates October grants and original targeted grants for comprehensive coverage
"""

import os

# Base configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Enhanced search criteria based on business strategy
SEARCH_CRITERIA = {
    'keywords': [
        # Minority-owned business keywords
        'minority-owned', 'black-owned', 'minority business', 'diverse entrepreneurs',
        'underrepresented founders', 'BIPOC', 'economic equity',
        
        # Financial literacy & empowerment
        'financial literacy', 'financial education', 'student loan', 'economic empowerment',
        'financial coaching', 'economic mobility', 'community development',
        
        # Technology & workforce development
        'AI consulting', 'artificial intelligence', 'technology training', 'digital equity',
        'workforce development', 'tech training', 'startup', 'innovation',
        
        # Youth empowerment & STEM
        'youth empowerment', 'STEM education', 'digital inclusion', 'tech education',
        'youth development', 'educational technology', 'coding', 'computer science'
    ],
    'min_amount': 5000,  # Lowered to catch smaller grants
    'max_days_old': 60,  # Extended to catch more opportunities
    'categories': [
        'Business Development',
        'Economic Development', 
        'Education',
        'Science & Technology',
        'Community Development',
        'Workforce Development',
        'Youth Development',
        'Financial Services',
        'Innovation'
    ]
}

# Original targeted grants plus October grants integration
TARGETED_GRANTS = {
    # Original strategic grants
    'minority_business': {
        'NAACP Power Forward Grant': {
            'amount': 'Up to $50,000',
            'focus': 'Black-owned businesses scaling impactful solutions',
            'url': 'https://www.naacp.org/powerforward',
            'keywords': ['black-owned', 'minority business', 'social impact'],
            'deadline_type': 'rolling'
        },
        'Comcast RISE Investment Fund': {
            'amount': '$10,000-$20,000 + marketing support',
            'focus': 'Small businesses owned by people of color',
            'url': 'https://www.comcastrise.com',
            'keywords': ['minority-owned', 'small business', 'marketing'],
            'deadline_type': 'quarterly'
        },
        'Wells Fargo Open for Business Fund': {
            'amount': 'Varies, often $25,000+',
            'focus': 'Small business development in underserved communities',
            'url': 'https://www.wellsfargo.com/about/corporate-responsibility/community-giving',
            'keywords': ['small business', 'community development'],
            'deadline_type': 'annual'
        },
        # October grants - Community Development (High Priority)
        'Georgia Department of Community Affairs': {
            'amount': '$250,000 - $2,500,000',
            'focus': 'Community development and economic empowerment',
            'url': 'Website',
            'keywords': ['community development', 'economic development', 'georgia'],
            'deadline_type': 'specific_date',
            'deadline': '10/11/2024',
            'source': 'october_grants'
        },
        'National Association Of Realtors': {
            'amount': 'Up to $15,000',
            'focus': 'Community development and housing initiatives',
            'url': 'Website',
            'keywords': ['community development', 'housing', 'real estate'],
            'deadline_type': 'specific_date',
            'deadline': '10/15/2024',
            'source': 'october_grants'
        }
    },
    
    'financial_literacy': {
        'Bank of America Foundation Economic Mobility': {
            'amount': 'Varies',
            'focus': 'Economic mobility and financial education',
            'url': 'https://about.bankofamerica.com/en/making-an-impact/community-development-finance',
            'keywords': ['economic mobility', 'financial education', 'workforce development'],
            'deadline_type': 'rolling'
        },
        'St. Louis CDBG Program': {
            'amount': 'Varies',
            'focus': 'Community Development Block Grants',
            'url': 'https://www.stlouis-mo.gov/government/departments/sldc/community-development',
            'keywords': ['community development', 'economic development'],
            'deadline_type': 'annual',
            'location': 'St. Louis'
        },
        # October grants - Financial Education
        'United Way of the CSRA Grants': {
            'amount': 'Unspecified amount',
            'focus': 'Economic empowerment and financial education',
            'url': 'Website',
            'keywords': ['financial education', 'economic empowerment', 'united way'],
            'deadline_type': 'specific_date',
            'deadline': '11/30/2024',
            'source': 'october_grants'
        },
        'Truist Foundation Grants': {
            'amount': 'Unspecified amount',
            'focus': 'Financial literacy and economic development',
            'url': 'Website',
            'keywords': ['financial literacy', 'economic development', 'education'],
            'deadline_type': 'specific_date',
            'deadline': '11/30/2024',
            'source': 'october_grants'
        }
    },
    
    'technology_workforce': {
        'Google for Startups Black Founders Fund': {
            'amount': '$50,000-$150,000, no equity required',
            'focus': 'Black-led startups in tech',
            'url': 'https://startup.google.com/programs/black-founders-fund',
            'keywords': ['black founders', 'technology', 'startup', 'AI'],
            'deadline_type': 'cohort-based'
        },
        'SBA Community Navigator Pilot Program': {
            'amount': 'Varies',
            'focus': 'Business advisory and training services',
            'url': 'https://www.sba.gov/partners/counselors/community-navigator-pilot-program',
            'keywords': ['business advisory', 'training', 'community navigator'],
            'deadline_type': 'rolling'
        },
        'EDA Build to Scale Grant': {
            'amount': 'Up to $500,000',
            'focus': 'Tech-based community growth and entrepreneurship',
            'url': 'https://www.eda.gov/funding/programs/build-to-scale',
            'keywords': ['technology', 'entrepreneurship', 'economic development'],
            'deadline_type': 'annual'
        },
        # October grants - Technology Focus
        'IBM Corporation': {
            'amount': '$10,000 - $50,000',
            'focus': 'Technology innovation and digital advancement',
            'url': 'Website',
            'keywords': ['technology', 'innovation', 'digital', 'IBM'],
            'deadline_type': 'specific_date',
            'deadline': '10/18/2024',
            'source': 'october_grants'
        },
        'Delta Analytics Data Service Grant': {
            'amount': 'In-kind support',
            'focus': 'Data analytics and technology services',
            'url': 'Website',
            'keywords': ['data analytics', 'technology', 'AI', 'data science'],
            'deadline_type': 'specific_date',
            'deadline': '11/15/2024',
            'source': 'october_grants'
        },
        'Mitigating Proliferation Risks Posed by AI': {
            'amount': 'Up to $4,000,000',
            'focus': 'AI research and development with social impact',
            'url': 'Website',
            'keywords': ['artificial intelligence', 'AI', 'technology', 'research'],
            'deadline_type': 'specific_date',
            'deadline': '11/13/2024',
            'source': 'october_grants'
        }
    },
    
    'youth_ai_empowerment': {
        'Black Ambition Prize': {
            'amount': 'Up to $1M',
            'focus': 'Black and Latinx founders with scalable solutions',
            'url': 'https://blackambition.org',
            'keywords': ['black founders', 'latinx', 'scalable solutions', 'innovation'],
            'deadline_type': 'annual'
        },
        'Chan Zuckerberg Initiative Education Grants': {
            'amount': 'Varies',
            'focus': 'Education equity and personalized learning',
            'url': 'https://chanzuckerberg.com/education',
            'keywords': ['education equity', 'personalized learning', 'technology'],
            'deadline_type': 'rolling'
        },
        'Best Buy Foundation Teen Tech Centers': {
            'amount': 'Varies',
            'focus': 'Teen tech training and digital skills',
            'url': 'https://corporate.bestbuy.com/community-grants',
            'keywords': ['teen tech', 'digital skills', 'youth development'],
            'deadline_type': 'rolling'
        },
        # October grants - Youth & Education Focus
        'Equity in Mathematics Grant (PK-6)': {
            'amount': 'Up to $8,000',
            'focus': 'Youth development and educational support - Mathematics equity',
            'url': 'Website',
            'keywords': ['education', 'youth development', 'mathematics', 'equity'],
            'deadline_type': 'specific_date',
            'deadline': '11/1/2024',
            'source': 'october_grants'
        },
        'Equity in Mathematics Grants (6-12)': {
            'amount': 'Up to $8,000',
            'focus': 'Youth development and educational support - Mathematics equity',
            'url': 'Website',
            'keywords': ['education', 'youth development', 'mathematics', 'STEM'],
            'deadline_type': 'specific_date',
            'deadline': '11/1/2024',
            'source': 'october_grants'
        },
        'Every Kid Outdoors Small Grants Program': {
            'amount': 'Up to $5,000',
            'focus': 'Youth outdoor education and development',
            'url': 'Website',
            'keywords': ['youth development', 'education', 'outdoor education'],
            'deadline_type': 'specific_date',
            'deadline': '12/1/2024',
            'source': 'october_grants'
        },
        'Research Grants on Education Small': {
            'amount': 'Up to $50,000',
            'focus': 'Educational research and youth development',
            'url': 'Website',
            'keywords': ['education', 'research', 'youth development', 'learning'],
            'deadline_type': 'specific_date',
            'deadline': 'N/A',
            'source': 'october_grants'
        },
        'Sony CREATE ACTION Grants': {
            'amount': 'Up to $50,000',
            'focus': 'Youth creative development and technology',
            'url': 'Website',
            'keywords': ['youth development', 'creativity', 'technology', 'education'],
            'deadline_type': 'specific_date',
            'deadline': '10/1/2024',
            'source': 'october_grants'
        }
    }
}

# Enhanced grant sources with specific platforms
GRANT_SOURCES = {
    'grants_gov': {
        'base_url': 'https://www.grants.gov/web/grants/search-grants.html',
        'api_url': 'https://api.grants.gov/v1/api/search2',
        'enabled': True,
        'priority': 1
    },
    'foundation_center': {
        'base_url': 'https://candid.org/find-funding',
        'enabled': True,
        'priority': 2,
        'note': 'Requires subscription for full access'
    },
    'grantwatch': {
        'base_url': 'https://www.grantwatch.com',
        'enabled': True,
        'priority': 3,
        'note': 'Subscription-based service'
    },
    'sba_funding': {
        'base_url': 'https://www.sba.gov/funding-programs/grants',
        'enabled': True,
        'priority': 2
    },
    'minority_business_grants': {
        'base_url': 'https://www.mbda.gov/grants-and-contracts',
        'enabled': True,
        'priority': 1,
        'note': 'Minority Business Development Agency'
    },
    'october_grants_csv': {
        'base_url': 'Nonprofit Guy National Grant List',
        'enabled': True,
        'priority': 2,
        'note': 'October 2024 curated grant opportunities'
    }
}

# Geographic focus areas
TARGET_LOCATIONS = [
    'St. Louis, MO',
    'Kansas City, MO', 
    'Dallas, TX',
    'Chicago, IL',
    'Missouri',
    'Texas', 
    'Illinois',
    'Georgia',  # Added due to October grants
    'National'
]

# Business profile for matching
BUSINESS_PROFILE = {
    'business_type': 'Minority-owned LLC',
    'focus_areas': [
        'Financial literacy and student loan coaching',
        'AI consulting and technology services',
        'Youth empowerment and STEM education',
        'Community economic development'
    ],
    'target_demographics': [
        'Underserved communities',
        'Students and young professionals',
        'Small businesses',
        'Youth interested in technology'
    ],
    'revenue_stage': 'Early-stage/Growing',
    'employee_count': '1-10',
    'certifications': ['Minority-owned', 'Small business']
}

# Enhanced scoring weights for grant relevance
SCORING_WEIGHTS = {
    'minority_business_focus': 3.0,
    'financial_literacy_focus': 2.5,
    'technology_focus': 2.5,
    'youth_empowerment_focus': 2.0,
    'community_development_focus': 2.0,  # Added for October grants
    'geographic_match': 1.5,
    'funding_amount_fit': 1.0,
    'deadline_urgency': 1.0,
    'keyword_match': 1.0,
    'october_grants_bonus': 0.5  # Bonus for curated October grants
}

# Alert thresholds
ALERT_CRITERIA = {
    'high_priority_amount': 25000,  # Grants above this amount get high priority
    'urgent_deadline_days': 14,     # Grants closing within this timeframe
    'relevance_score_threshold': 7.0,  # Minimum score for alerts
    'october_grants_priority': True  # Prioritize October grants due to specific deadlines
}

# Email notification settings (if configured)
EMAIL_NOTIFICATIONS = {
    'enabled': False,  # Set to True when email is configured
    'smtp_server': '',
    'smtp_port': 587,
    'username': '',
    'password': '',
    'recipients': [],
    'send_daily_summary': True,
    'send_urgent_alerts': True,
    'send_october_grants_alerts': True  # Special alerts for October grants
}

# Report generation settings
REPORT_SETTINGS = {
    'include_targeted_grants': True,
    'include_october_grants': True,  # Include October grants in reports
    'include_geographic_analysis': True,
    'include_business_profile_matching': True,
    'include_deadline_analysis': True,  # Added for October grants with specific deadlines
    'max_grants_in_summary': 25,  # Increased to accommodate October grants
    'generate_excel': True,
    'generate_markdown': True,
    'generate_pdf': False,
    'october_grants_priority_section': True  # Special section for October grants
}

# October grants metadata
OCTOBER_GRANTS_METADATA = {
    'total_processed': 125,
    'relevant_found': 77,
    'high_priority': 29,
    'categories_covered': ['Education', 'Community Development', 'Technology', 'Health and Human Services'],
    'integration_date': '2024-10-03',
    'source': 'Nonprofit Guy National Grant List - October 2024',
    'deadline_range': '10/1/2024 - 12/31/2024',
    'special_focus': [
        'Community development grants with large funding amounts',
        'Education and youth development opportunities',
        'Technology and AI-related grants',
        'Health and human services with community impact'
    ]
}

