#!/usr/bin/env python3
"""
Daily Grant Automation Script
Discovers and processes new grant opportunities from multiple sources
"""

import os
import sys
import json
import requests
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))
from settings import *

class GrantDiscovery:
    """Main class for grant discovery and processing"""
    
    def __init__(self):
        self.setup_logging()
        self.session = requests.Session()
        self.grants_found = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(LOGS_DIR, f'grant_discovery_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Grant Discovery System Initialized")
    
    def search_grants_gov(self, keywords: List[str] = None, max_results: int = 100) -> List[Dict]:
        """
        Search grants.gov using their API
        
        Args:
            keywords: List of keywords to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of grant opportunities
        """
        self.logger.info("Starting grants.gov API search")
        
        if not keywords:
            keywords = SEARCH_CRITERIA['keywords']
        
        grants = []
        
        try:
            # Search for each keyword combination
            for keyword in keywords:
                self.logger.info(f"Searching for keyword: {keyword}")
                
                # Prepare search payload
                payload = {
                    "rows": min(max_results, 25),  # API limit per request
                    "keyword": keyword,
                    "oppStatuses": "forecasted|posted",
                    "startRecordNum": 0
                }
                
                # Add category filters if specified
                if SEARCH_CRITERIA.get('categories'):
                    # Note: Would need to map category names to API codes
                    pass
                
                response = self.session.post(
                    GRANT_SOURCES['grants_gov']['api_url'],
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('errorcode') == 0:
                        opportunities = data.get('data', {}).get('oppHits', [])
                        self.logger.info(f"Found {len(opportunities)} opportunities for '{keyword}'")
                        
                        for opp in opportunities:
                            # Filter by minimum amount if specified
                            grant_info = self.process_grants_gov_opportunity(opp)
                            if grant_info and self.meets_criteria(grant_info):
                                grants.append(grant_info)
                    else:
                        self.logger.error(f"API error: {data.get('msg', 'Unknown error')}")
                else:
                    self.logger.error(f"HTTP error {response.status_code}: {response.text}")
                
                # Rate limiting - be respectful
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error searching grants.gov: {str(e)}")
        
        self.logger.info(f"Total grants found from grants.gov: {len(grants)}")
        return grants
    
    def process_grants_gov_opportunity(self, opp: Dict) -> Optional[Dict]:
        """
        Process a single opportunity from grants.gov API
        
        Args:
            opp: Raw opportunity data from API
            
        Returns:
            Processed grant information or None
        """
        try:
            # Parse dates
            open_date = None
            close_date = None
            
            if opp.get('openDate'):
                try:
                    open_date = datetime.strptime(opp['openDate'], '%m/%d/%Y')
                except:
                    pass
            
            if opp.get('closeDate'):
                try:
                    close_date = datetime.strptime(opp['closeDate'], '%m/%d/%Y')
                except:
                    pass
            
            # Check if grant is too old
            if open_date and (datetime.now() - open_date).days > SEARCH_CRITERIA['max_days_old']:
                return None
            
            grant_info = {
                'source': 'grants.gov',
                'id': opp.get('id'),
                'number': opp.get('number'),
                'title': opp.get('title'),
                'agency_code': opp.get('agencyCode'),
                'agency_name': opp.get('agencyName'),
                'open_date': open_date.isoformat() if open_date else None,
                'close_date': close_date.isoformat() if close_date else None,
                'status': opp.get('oppStatus'),
                'document_type': opp.get('docType'),
                'aln_list': opp.get('alnist', []),
                'url': f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={opp.get('id')}",
                'discovered_date': datetime.now().isoformat(),
                'estimated_amount': None,  # Not available in search results
                'eligibility': None,  # Would need detailed fetch
                'description': None  # Would need detailed fetch
            }
            
            return grant_info
            
        except Exception as e:
            self.logger.error(f"Error processing opportunity {opp.get('id', 'unknown')}: {str(e)}")
            return None
    
    def meets_criteria(self, grant_info: Dict) -> bool:
        """
        Check if grant meets search criteria
        
        Args:
            grant_info: Processed grant information
            
        Returns:
            True if grant meets criteria
        """
        # Check minimum amount (if available)
        if grant_info.get('estimated_amount'):
            try:
                amount = float(grant_info['estimated_amount'])
                if amount < SEARCH_CRITERIA['min_amount']:
                    return False
            except:
                pass
        
        # Check if grant is still open
        if grant_info.get('close_date'):
            try:
                close_date = datetime.fromisoformat(grant_info['close_date'])
                if close_date < datetime.now():
                    return False
            except:
                pass
        
        return True
    
    def fetch_grant_details(self, grant_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific grant
        
        Args:
            grant_id: Grant ID to fetch details for
            
        Returns:
            Detailed grant information or None
        """
        # This would use the fetchOpportunity API endpoint
        # Implementation would be similar to search but for individual grants
        self.logger.info(f"Fetching details for grant {grant_id}")
        
        try:
            # Placeholder for fetchOpportunity API call
            # The actual endpoint would be different
            pass
        except Exception as e:
            self.logger.error(f"Error fetching grant details for {grant_id}: {str(e)}")
            return None
    
    def search_additional_sources(self) -> List[Dict]:
        """
        Search additional grant sources (placeholder for future expansion)
        
        Returns:
            List of grants from additional sources
        """
        self.logger.info("Searching additional grant sources")
        additional_grants = []
        
        # Placeholder for GrantWatch scraping (if subscription available)
        # Placeholder for Foundation Directory API (if available)
        # Placeholder for other grant databases
        
        return additional_grants
    
    def deduplicate_grants(self, grants: List[Dict]) -> List[Dict]:
        """
        Remove duplicate grants based on ID or title similarity
        
        Args:
            grants: List of grant opportunities
            
        Returns:
            Deduplicated list of grants
        """
        self.logger.info(f"Deduplicating {len(grants)} grants")
        
        seen_ids = set()
        seen_titles = set()
        unique_grants = []
        
        for grant in grants:
            # Check by ID first
            grant_id = grant.get('id') or grant.get('number')
            if grant_id and grant_id in seen_ids:
                continue
            
            # Check by title similarity (basic)
            title = grant.get('title', '').lower().strip()
            if title in seen_titles:
                continue
            
            if grant_id:
                seen_ids.add(grant_id)
            if title:
                seen_titles.add(title)
            
            unique_grants.append(grant)
        
        self.logger.info(f"After deduplication: {len(unique_grants)} unique grants")
        return unique_grants
    
    def save_grants_data(self, grants: List[Dict], filename: str = None) -> str:
        """
        Save grants data to JSON file
        
        Args:
            grants: List of grant opportunities
            filename: Optional filename, defaults to timestamped file
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"grants_discovery_{timestamp}.json"
        
        filepath = os.path.join(DATA_DIR, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'discovery_date': datetime.now().isoformat(),
                    'total_grants': len(grants),
                    'search_criteria': SEARCH_CRITERIA,
                    'grants': grants
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(grants)} grants to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving grants data: {str(e)}")
            raise
    
    def run_daily_discovery(self) -> Dict:
        """
        Run the complete daily grant discovery process
        
        Returns:
            Summary of discovery results
        """
        self.logger.info("Starting daily grant discovery process")
        start_time = datetime.now()
        
        try:
            # Search grants.gov
            grants_gov_results = self.search_grants_gov()
            
            # Search additional sources
            additional_results = self.search_additional_sources()
            
            # Combine all results
            all_grants = grants_gov_results + additional_results
            
            # Deduplicate
            unique_grants = self.deduplicate_grants(all_grants)
            
            # Save results
            data_file = self.save_grants_data(unique_grants)
            
            # Generate summary
            end_time = datetime.now()
            duration = end_time - start_time
            
            summary = {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'total_grants_found': len(unique_grants),
                'grants_gov_count': len(grants_gov_results),
                'additional_sources_count': len(additional_results),
                'data_file': data_file,
                'success': True
            }
            
            self.logger.info(f"Discovery completed successfully in {duration.total_seconds():.2f} seconds")
            self.logger.info(f"Found {len(unique_grants)} unique grants")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in daily discovery process: {str(e)}")
            return {
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }

def main():
    """Main entry point for the script"""
    print("Grant Discovery Automation System")
    print("=" * 40)
    
    try:
        # Create necessary directories
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
        # Initialize and run discovery
        discovery = GrantDiscovery()
        results = discovery.run_daily_discovery()
        
        # Print summary
        if results['success']:
            print(f"✅ Discovery completed successfully!")
            print(f"📊 Found {results['total_grants_found']} grants")
            print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
            print(f"💾 Data saved to: {results['data_file']}")
        else:
            print(f"❌ Discovery failed: {results.get('error', 'Unknown error')}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

