#!/usr/bin/env python3
"""
Configuration settings for EdTech Certificate Scraper
"""

import os
from typing import Dict, Any

# Rate limiting settings (requests per second)
RATE_LIMITS = {
    'coursera': 0.5,      # Conservative for major platform
    'udemy': 0.3,         # Very conservative
    'linkedin': 0.2,      # Very conservative due to strict policies  
    'nptel': 0.3,         # Government site - be respectful
    'internshala': 0.5,   # Indian platform
    'skill_india': 0.3,   # Government initiative
    'aicte': 0.2,         # Government body
    'credly': 0.5,        # Digital badge platform
    'default': 1.0        # Default rate limit
}

# Request timeout settings (seconds)
REQUEST_TIMEOUT = 30

# User agent strings for different browsers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# Platform-specific verification URL patterns
VERIFICATION_PATTERNS = {
    'coursera': {
        'pattern': r'coursera\.org/account/accomplishments/verify/[A-Z0-9]+',
        'example': 'https://www.coursera.org/account/accomplishments/verify/ABC123'
    },
    'udemy': {
        'pattern': r'udemy\.com/certificate/[A-Z0-9]+',
        'example': 'https://www.udemy.com/certificate/ABC123'
    },
    'linkedin_learning': {
        'pattern': r'linkedin\.com/learning/certificates/[a-f0-9\-]+',
        'example': 'https://www.linkedin.com/learning/certificates/abc-123-def'
    },
    'nptel': {
        'pattern': r'nptel\.ac\.in/.*certificate.*',
        'example': 'https://nptel.ac.in/certificate/verify'
    },
    'internshala': {
        'pattern': r'internshala\.com/certificate/[A-Z0-9]+',
        'example': 'https://internshala.com/certificate/ABC123'
    },
    'credly': {
        'pattern': r'credly\.com/badges/[a-f0-9\-]+',
        'example': 'https://www.credly.com/badges/abc-123-def'
    }
}

# Data validation rules
VALIDATION_RULES = {
    'min_name_length': 2,
    'max_name_length': 100,
    'min_title_length': 5,
    'max_title_length': 200,
    'required_fields': ['learner_name', 'certificate_title', 'platform'],
    'date_formats': ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%B %d, %Y']
}

# Export settings
EXPORT_SETTINGS = {
    'json_indent': 2,
    'csv_encoding': 'utf-8',
    'include_metadata': True,
    'timestamp_format': '%Y-%m-%d_%H-%M-%S'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'certificate_scraper.log',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Security settings
SECURITY_SETTINGS = {
    'verify_ssl': True,
    'max_redirects': 5,
    'allowed_content_types': ['text/html', 'application/json'],
    'max_content_length': 5 * 1024 * 1024,  # 5MB
}

# Platform-specific extraction rules
EXTRACTION_RULES = {
    'coursera': {
        'name_selectors': [
            'h1.completion-page-title',
            '.accomplishment-name',
            '[data-test="accomplishment-learner-name"]'
        ],
        'title_selectors': [
            'h2.completion-page-subtitle',
            '.accomplishment-course-name',
            '[data-test="accomplishment-course-name"]'
        ],
        'organization_selectors': [
            '.accomplishment-university-name',
            '.partner-name',
            '[data-test="accomplishment-university-name"]'
        ],
        'date_selectors': [
            '.accomplishment-date',
            '[data-test="accomplishment-date"]'
        ]
    },
    'linkedin_learning': {
        'name_selectors': [
            '.profile-topcard__name',
            '.member-name',
            '[data-test="member-name"]'
        ],
        'title_selectors': [
            '.course-title',
            '.completion-certificate-title'
        ],
        'date_selectors': [
            '.completion-date',
            '[data-test="completion-date"]'
        ]
    },
    'nptel': {
        'name_selectors': [
            '.student-name',
            '#studentName'
        ],
        'title_selectors': [
            '.course-title',
            '#courseTitle'
        ],
        'cert_id_selectors': [
            '.certificate-number',
            '#certificateNumber'
        ]
    }
}

def get_platform_config(platform: str) -> Dict[str, Any]:
    """Get configuration for a specific platform"""
    return {
        'rate_limit': RATE_LIMITS.get(platform, RATE_LIMITS['default']),
        'verification_pattern': VERIFICATION_PATTERNS.get(platform, {}),
        'extraction_rules': EXTRACTION_RULES.get(platform, {}),
        'timeout': REQUEST_TIMEOUT
    }

def get_user_agent() -> str:
    """Get a random user agent string"""
    import random
    return random.choice(USER_AGENTS)

# Environment-specific settings
def load_env_config():
    """Load configuration from environment variables"""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        'output_dir': os.getenv('OUTPUT_DIR', './output'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'max_concurrent_requests': int(os.getenv('MAX_CONCURRENT_REQUESTS', '5')),
        'enable_caching': os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    }