"""
Grant Automation Configuration Settings
"""

import os
from datetime import datetime

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# Grant sources configuration
GRANT_SOURCES = {
    'grants_gov': {
        'base_url': 'https://www.grants.gov/web/grants/search-grants.html',
        'api_url': 'https://api.grants.gov/v1/api/search2',
        'enabled': True
    },
    'grantwatch': {
        'base_url': 'https://www.grantwatch.com',
        'enabled': True
    },
    'foundation_directory': {
        'base_url': 'https://fconline.foundationcenter.org',
        'enabled': False  # Requires subscription
    }
}

# Search criteria
SEARCH_CRITERIA = {
    'keywords': ['technology', 'innovation', 'research', 'development', 'startup', 'small business'],
    'min_amount': 10000,  # Minimum grant amount
    'max_days_old': 30,   # Only grants posted in last 30 days
    'categories': ['Science & Technology', 'Business Development', 'Research']
}

# Output settings
OUTPUT_FORMATS = ['json', 'csv', 'excel']
REPORT_TEMPLATE = 'daily_grant_report'

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Email notification settings (optional)
EMAIL_NOTIFICATIONS = {
    'enabled': False,
    'smtp_server': '',
    'smtp_port': 587,
    'username': '',
    'password': '',
    'recipients': []
}

