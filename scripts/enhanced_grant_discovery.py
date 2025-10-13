#!/usr/bin/env python3
"""
Enhanced Grant Discovery System
Incorporates specific grant strategy for minority-owned business,
financial literacy, tech development, and youth empowerment
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))
from enhanced_settings import *

class EnhancedGrantDiscovery:
    """Enhanced grant discovery with targeted strategy"""
    
    def __init__(self):
        self.setup_logging()
        self.discovered_grants = []
        self.targeted_matches = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(LOGS_DIR, exist_ok=True)
        log_file = os.path.join(LOGS_DIR, f'enhanced_grant_discovery_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced Grant Discovery System Initialized")
    
    def search_grants_gov_targeted(self) -> List[Dict]:
        """Search grants.gov with enhanced targeting"""
        self.logger.info("Starting enhanced grants.gov search")
        grants = []
        
        # Search with business-specific keywords
        for category, keywords in [
            ('minority_business', ['minority-owned', 'black-owned', 'diverse entrepreneurs', 'BIPOC']),
            ('financial_literacy', ['financial literacy', 'economic empowerment', 'student loan', 'financial education']),
            ('technology', ['artificial intelligence', 'AI', 'technology training', 'digital equity']),
            ('youth_empowerment', ['youth development', 'STEM education', 'educational technology'])
        ]:
            
            for keyword in keywords:
                self.logger.info(f"Searching for {category} keyword: {keyword}")
                
                payload = {
                    "rows": 25,
                    "keyword": keyword,
                    "oppStatuses": "forecasted|posted",
                    "startRecordNum": 0
                }
                
                try:
                    response = requests.post(
                        GRANT_SOURCES['grants_gov']['api_url'],
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('errorcode') == 0:
                            hits = data.get('data', {}).get('oppHits', [])
                            self.logger.info(f"Found {len(hits)} opportunities for '{keyword}'")
                            
                            for hit in hits:
                                grant_info = self.process_grants_gov_hit(hit, category, keyword)
                                if grant_info:
                                    grants.append(grant_info)
                        else:
                            self.logger.error(f"API error for '{keyword}': {data.get('msg')}")
                    else:
                        self.logger.error(f"HTTP {response.status_code} for keyword '{keyword}'")
                        
                except Exception as e:
                    self.logger.error(f"Error searching for '{keyword}': {str(e)}")
                
                time.sleep(1)  # Rate limiting
        
        return grants
    
    def process_grants_gov_hit(self, hit: Dict, category: str, keyword: str) -> Optional[Dict]:
        """Process a grants.gov search hit with enhanced scoring"""
        try:
            grant_info = {
                'source': 'grants.gov',
                'category': category,
                'discovery_keyword': keyword,
                'id': hit.get('id'),
                'number': hit.get('number'),
                'title': hit.get('title'),
                'agency_code': hit.get('agencyCode'),
                'agency_name': hit.get('agencyName'),
                'open_date': hit.get('openDate'),
                'close_date': hit.get('closeDate'),
                'status': hit.get('oppStatus'),
                'document_type': hit.get('docType'),
                'aln_list': hit.get('alnist', []),
                'url': f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={hit.get('id')}",
                'discovered_date': datetime.now().isoformat(),
                'relevance_score': self.calculate_enhanced_relevance_score(hit, category, keyword)
            }
            
            return grant_info
            
        except Exception as e:
            self.logger.error(f"Error processing grant hit: {str(e)}")
            return None
    
    def calculate_enhanced_relevance_score(self, hit: Dict, category: str, keyword: str) -> float:
        """Calculate enhanced relevance score based on business profile"""
        score = 0.0
        title = (hit.get('title') or '').lower()
        agency = (hit.get('agencyCode') or '').lower()
        
        # Category-specific scoring
        if category == 'minority_business':
            if any(term in title for term in ['minority', 'black', 'diverse', 'underrepresented', 'bipoc']):
                score += SCORING_WEIGHTS['minority_business_focus']
        
        elif category == 'financial_literacy':
            if any(term in title for term in ['financial', 'economic', 'loan', 'literacy', 'empowerment']):
                score += SCORING_WEIGHTS['financial_literacy_focus']
        
        elif category == 'technology':
            if any(term in title for term in ['technology', 'ai', 'artificial', 'digital', 'innovation']):
                score += SCORING_WEIGHTS['technology_focus']
        
        elif category == 'youth_empowerment':
            if any(term in title for term in ['youth', 'education', 'stem', 'student', 'learning']):
                score += SCORING_WEIGHTS['youth_empowerment_focus']
        
        # Agency scoring
        if any(agency_code in agency for agency_code in ['sba', 'eda', 'doe', 'nsf']):
            score += 1.0
        
        # Keyword match scoring
        if keyword.lower() in title:
            score += SCORING_WEIGHTS['keyword_match']
        
        # Status scoring
        if hit.get('oppStatus') == 'posted':
            score += 0.5
        
        return round(score, 2)
    
    def search_targeted_grants(self) -> List[Dict]:
        """Search for specific targeted grants from our curated list"""
        self.logger.info("Searching targeted grant opportunities")
        targeted_grants = []
        
        for category, grants in TARGETED_GRANTS.items():
            self.logger.info(f"Processing {category} grants")
            
            for grant_name, grant_info in grants.items():
                # Create a targeted grant entry
                targeted_grant = {
                    'source': 'targeted_list',
                    'category': category,
                    'name': grant_name,
                    'amount': grant_info['amount'],
                    'focus': grant_info['focus'],
                    'url': grant_info['url'],
                    'keywords': grant_info['keywords'],
                    'deadline_type': grant_info['deadline_type'],
                    'location': grant_info.get('location', 'National'),
                    'discovered_date': datetime.now().isoformat(),
                    'relevance_score': self.calculate_targeted_grant_score(grant_info, category),
                    'priority': 'HIGH' if any(keyword in grant_info['focus'].lower() 
                                            for keyword in ['black', 'minority', 'ai', 'technology']) else 'MEDIUM'
                }
                
                targeted_grants.append(targeted_grant)
        
        self.logger.info(f"Found {len(targeted_grants)} targeted grant opportunities")
        return targeted_grants
    
    def calculate_targeted_grant_score(self, grant_info: Dict, category: str) -> float:
        """Calculate relevance score for targeted grants"""
        score = 5.0  # Base score for targeted grants
        
        # Category bonus
        if category in ['minority_business', 'technology_workforce']:
            score += 2.0
        elif category in ['financial_literacy', 'youth_ai_empowerment']:
            score += 1.5
        
        # Amount-based scoring
        amount_str = grant_info['amount'].lower()
        if '$50,000' in amount_str or '$100,000' in amount_str:
            score += 1.0
        elif '$1m' in amount_str or '1,000,000' in amount_str:
            score += 2.0
        
        # Deadline type scoring
        if grant_info['deadline_type'] == 'rolling':
            score += 0.5
        
        return round(score, 2)
    
    def search_additional_sources(self) -> List[Dict]:
        """Search additional grant sources"""
        self.logger.info("Searching additional grant sources")
        additional_grants = []
        
        # For now, return placeholder data for additional sources
        # These would be implemented with web scraping or API calls
        
        sources_info = [
            {
                'source': 'foundation_center',
                'note': 'Requires subscription - manual search recommended',
                'url': GRANT_SOURCES['foundation_center']['base_url']
            },
            {
                'source': 'grantwatch',
                'note': 'Subscription service - check for minority business grants',
                'url': GRANT_SOURCES['grantwatch']['base_url']
            },
            {
                'source': 'sba_funding',
                'note': 'Check SBA grants for small business development',
                'url': GRANT_SOURCES['sba_funding']['base_url']
            }
        ]
        
        for source in sources_info:
            additional_grants.append({
                'source': source['source'],
                'type': 'manual_search_required',
                'note': source['note'],
                'url': source['url'],
                'discovered_date': datetime.now().isoformat(),
                'priority': 'MANUAL_REVIEW'
            })
        
        return additional_grants
    
    def deduplicate_grants(self, grants: List[Dict]) -> List[Dict]:
        """Remove duplicate grants with enhanced logic"""
        seen = set()
        unique_grants = []
        
        for grant in grants:
            # Create identifier based on multiple fields
            if grant.get('id'):
                identifier = grant['id']
            elif grant.get('number'):
                identifier = grant['number']
            elif grant.get('name'):
                identifier = grant['name']
            else:
                identifier = grant.get('title', '')[:50]
            
            if identifier not in seen:
                seen.add(identifier)
                unique_grants.append(grant)
        
        self.logger.info(f"Deduplication: {len(grants)} -> {len(unique_grants)} grants")
        return unique_grants
    
    def save_results(self, grants: List[Dict]) -> str:
        """Save discovery results with enhanced metadata"""
        os.makedirs(DATA_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_grants_discovery_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        # Separate grants by type
        federal_grants = [g for g in grants if g.get('source') == 'grants.gov']
        targeted_grants = [g for g in grants if g.get('source') == 'targeted_list']
        additional_sources = [g for g in grants if g.get('source') not in ['grants.gov', 'targeted_list']]
        
        # Create comprehensive results
        results = {
            'discovery_date': datetime.now().isoformat(),
            'business_profile': BUSINESS_PROFILE,
            'search_criteria': SEARCH_CRITERIA,
            'target_locations': TARGET_LOCATIONS,
            'summary': {
                'total_grants': len(grants),
                'federal_grants': len(federal_grants),
                'targeted_grants': len(targeted_grants),
                'additional_sources': len(additional_sources),
                'high_priority_grants': len([g for g in grants if g.get('priority') == 'HIGH' or g.get('relevance_score', 0) >= 7.0])
            },
            'grants_by_category': {
                'minority_business': [g for g in grants if g.get('category') == 'minority_business'],
                'financial_literacy': [g for g in grants if g.get('category') == 'financial_literacy'],
                'technology': [g for g in grants if g.get('category') == 'technology'],
                'youth_empowerment': [g for g in grants if g.get('category') == 'youth_empowerment']
            },
            'all_grants': grants
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Enhanced results saved to {filepath}")
        return filepath
    
    def run_enhanced_discovery(self) -> Dict:
        """Run the complete enhanced grant discovery process"""
        start_time = time.time()
        self.logger.info("Starting enhanced grant discovery process")
        
        try:
            # Search federal grants with targeting
            federal_grants = self.search_grants_gov_targeted()
            
            # Search targeted grants
            targeted_grants = self.search_targeted_grants()
            
            # Search additional sources
            additional_grants = self.search_additional_sources()
            
            # Combine all grants
            all_grants = federal_grants + targeted_grants + additional_grants
            
            # Deduplicate
            unique_grants = self.deduplicate_grants(all_grants)
            
            # Save results
            results_file = self.save_results(unique_grants)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create summary
            summary = {
                'success': True,
                'total_grants': len(unique_grants),
                'federal_grants': len(federal_grants),
                'targeted_grants': len(targeted_grants),
                'additional_sources': len(additional_grants),
                'high_priority_grants': len([g for g in unique_grants if g.get('priority') == 'HIGH' or g.get('relevance_score', 0) >= 7.0]),
                'execution_time': round(execution_time, 2),
                'results_file': results_file
            }
            
            self.logger.info(f"Enhanced discovery completed successfully in {execution_time:.2f} seconds")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in enhanced discovery: {str(e)}")
            return {'success': False, 'error': str(e)}

def main():
    """Main entry point for enhanced grant discovery"""
    print("Enhanced Grant Discovery System")
    print("=" * 40)
    
    try:
        discovery = EnhancedGrantDiscovery()
        results = discovery.run_enhanced_discovery()
        
        if results['success']:
            print(f"✅ Enhanced discovery completed successfully!")
            print(f"📊 Total grants found: {results['total_grants']}")
            print(f"🎯 High priority grants: {results['high_priority_grants']}")
            print(f"🏛️  Federal grants: {results['federal_grants']}")
            print(f"🎯 Targeted grants: {results['targeted_grants']}")
            print(f"⏱️  Duration: {results['execution_time']} seconds")
            print(f"💾 Results saved to: {results['results_file']}")
        else:
            print(f"❌ Discovery failed: {results.get('error', 'Unknown error')}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

