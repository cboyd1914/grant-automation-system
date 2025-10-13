#!/usr/bin/env python3
"""
Grant Data Analysis and Processing Script
Analyzes discovered grants and creates organized reports
"""

import os
import sys
import json
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from collections import Counter

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))
from settings import *

class GrantAnalyzer:
    """Analyzes and processes grant data"""
    
    def __init__(self, data_file: str = None):
        self.setup_logging()
        self.data_file = data_file
        self.grants_data = None
        self.processed_grants = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(LOGS_DIR, f'grant_analyzer_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Grant Analyzer Initialized")
    
    def load_grant_data(self, data_file: str = None) -> bool:
        """
        Load grant data from JSON file
        
        Args:
            data_file: Path to grant data file
            
        Returns:
            True if successful, False otherwise
        """
        if data_file:
            self.data_file = data_file
        
        if not self.data_file:
            # Find the most recent data file
            data_files = [f for f in os.listdir(DATA_DIR) if f.startswith('grants_discovery_') and f.endswith('.json')]
            if not data_files:
                self.logger.error("No grant data files found")
                return False
            
            data_files.sort(reverse=True)
            self.data_file = os.path.join(DATA_DIR, data_files[0])
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.grants_data = json.load(f)
            
            self.logger.info(f"Loaded {len(self.grants_data.get('grants', []))} grants from {self.data_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading grant data: {str(e)}")
            return False
    
    def enrich_grant_data(self) -> List[Dict]:
        """
        Enrich grant data with additional information
        
        Returns:
            List of enriched grant data
        """
        self.logger.info("Enriching grant data with additional information")
        
        enriched_grants = []
        
        for grant in self.grants_data.get('grants', []):
            enriched_grant = grant.copy()
            
            # Calculate days until deadline
            if grant.get('close_date'):
                try:
                    close_date = datetime.fromisoformat(grant['close_date'])
                    days_until_deadline = (close_date - datetime.now()).days
                    enriched_grant['days_until_deadline'] = days_until_deadline
                    enriched_grant['urgency'] = self.calculate_urgency(days_until_deadline)
                except:
                    enriched_grant['days_until_deadline'] = None
                    enriched_grant['urgency'] = 'Unknown'
            else:
                enriched_grant['days_until_deadline'] = None
                enriched_grant['urgency'] = 'No Deadline'
            
            # Categorize by agency
            enriched_grant['agency_category'] = self.categorize_agency(grant.get('agency_code', ''))
            
            # Extract keywords from title
            enriched_grant['title_keywords'] = self.extract_keywords(grant.get('title', ''))
            
            # Estimate funding level
            enriched_grant['funding_level'] = self.estimate_funding_level(grant)
            
            # Add relevance score
            enriched_grant['relevance_score'] = self.calculate_relevance_score(grant)
            
            enriched_grants.append(enriched_grant)
        
        self.processed_grants = enriched_grants
        self.logger.info(f"Enriched {len(enriched_grants)} grants with additional data")
        return enriched_grants
    
    def calculate_urgency(self, days_until_deadline: int) -> str:
        """Calculate urgency level based on days until deadline"""
        if days_until_deadline <= 7:
            return 'Critical'
        elif days_until_deadline <= 14:
            return 'High'
        elif days_until_deadline <= 30:
            return 'Medium'
        else:
            return 'Low'
    
    def categorize_agency(self, agency_code: str) -> str:
        """Categorize agency by type"""
        agency_categories = {
            'DOE': 'Energy',
            'NSF': 'Science Foundation',
            'NIH': 'Health',
            'HHS': 'Health & Human Services',
            'DOD': 'Defense',
            'NASA': 'Space & Aeronautics',
            'USDA': 'Agriculture',
            'EPA': 'Environmental',
            'DOC': 'Commerce',
            'SBA': 'Small Business'
        }
        
        for code, category in agency_categories.items():
            if code in agency_code.upper():
                return category
        
        return 'Other Federal'
    
    def extract_keywords(self, title: str) -> List[str]:
        """Extract relevant keywords from grant title"""
        # Simple keyword extraction - could be enhanced with NLP
        common_words = {'the', 'and', 'or', 'for', 'to', 'in', 'of', 'a', 'an', 'with', 'by', 'from'}
        
        words = title.lower().split()
        keywords = [word.strip('.,()[]') for word in words 
                   if len(word) > 3 and word.lower() not in common_words]
        
        return keywords[:5]  # Return top 5 keywords
    
    def estimate_funding_level(self, grant: Dict) -> str:
        """Estimate funding level based on available information"""
        # This is a placeholder - in reality, you'd need to fetch detailed grant info
        agency_code = grant.get('agency_code', '')
        
        # Some rough estimates based on agency patterns
        if 'SBIR' in grant.get('title', '').upper() or 'STTR' in grant.get('title', '').upper():
            return 'Small ($50K-$500K)'
        elif 'DOE' in agency_code or 'NASA' in agency_code:
            return 'Large ($1M+)'
        elif 'NSF' in agency_code:
            return 'Medium ($100K-$1M)'
        else:
            return 'Unknown'
    
    def calculate_relevance_score(self, grant: Dict) -> float:
        """Calculate relevance score based on search criteria"""
        score = 0.0
        title = grant.get('title', '').lower()
        
        # Check for keyword matches
        for keyword in SEARCH_CRITERIA['keywords']:
            if keyword.lower() in title:
                score += 1.0
        
        # Bonus for recent grants
        if grant.get('open_date'):
            try:
                open_date = datetime.fromisoformat(grant['open_date'])
                days_old = (datetime.now() - open_date).days
                if days_old <= 7:
                    score += 0.5
                elif days_old <= 14:
                    score += 0.3
            except:
                pass
        
        # Bonus for active status
        if grant.get('status') == 'posted':
            score += 0.5
        
        return round(score, 2)
    
    def create_summary_statistics(self) -> Dict:
        """Create summary statistics of the grants"""
        if not self.processed_grants:
            return {}
        
        df = pd.DataFrame(self.processed_grants)
        
        stats = {
            'total_grants': len(self.processed_grants),
            'by_agency': df['agency_code'].value_counts().to_dict(),
            'by_status': df['status'].value_counts().to_dict(),
            'by_urgency': df['urgency'].value_counts().to_dict(),
            'by_agency_category': df['agency_category'].value_counts().to_dict(),
            'by_funding_level': df['funding_level'].value_counts().to_dict(),
            'avg_relevance_score': df['relevance_score'].mean(),
            'grants_with_deadlines': df['close_date'].notna().sum(),
            'grants_closing_soon': len(df[df['urgency'].isin(['Critical', 'High'])]),
        }
        
        return stats
    
    def create_priority_list(self, top_n: int = 10) -> List[Dict]:
        """Create prioritized list of grants"""
        if not self.processed_grants:
            return []
        
        # Sort by relevance score and urgency
        urgency_weights = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'No Deadline': 0, 'Unknown': 0}
        
        for grant in self.processed_grants:
            urgency_score = urgency_weights.get(grant.get('urgency', 'Unknown'), 0)
            relevance_score = grant.get('relevance_score', 0)
            grant['priority_score'] = relevance_score + (urgency_score * 0.5)
        
        sorted_grants = sorted(self.processed_grants, 
                             key=lambda x: x.get('priority_score', 0), 
                             reverse=True)
        
        return sorted_grants[:top_n]
    
    def export_to_excel(self, filename: str = None) -> str:
        """Export grants data to Excel file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"grants_analysis_{timestamp}.xlsx"
        
        filepath = os.path.join(REPORTS_DIR, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # All grants sheet
                df_all = pd.DataFrame(self.processed_grants)
                df_all.to_excel(writer, sheet_name='All Grants', index=False)
                
                # Priority grants sheet
                priority_grants = self.create_priority_list(20)
                df_priority = pd.DataFrame(priority_grants)
                df_priority.to_excel(writer, sheet_name='Priority Grants', index=False)
                
                # Summary statistics sheet
                stats = self.create_summary_statistics()
                df_stats = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
                df_stats.to_excel(writer, sheet_name='Summary', index=False)
                
                # Urgent grants sheet (closing soon)
                urgent_grants = [g for g in self.processed_grants 
                               if g.get('urgency') in ['Critical', 'High']]
                if urgent_grants:
                    df_urgent = pd.DataFrame(urgent_grants)
                    df_urgent.to_excel(writer, sheet_name='Urgent Grants', index=False)
            
            self.logger.info(f"Exported grants analysis to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}")
            raise
    
    def generate_markdown_report(self, filename: str = None) -> str:
        """Generate comprehensive markdown report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"grants_report_{timestamp}.md"
        
        filepath = os.path.join(REPORTS_DIR, filename)
        
        try:
            stats = self.create_summary_statistics()
            priority_grants = self.create_priority_list(10)
            urgent_grants = [g for g in self.processed_grants 
                           if g.get('urgency') in ['Critical', 'High']]
            
            report_content = f"""# Daily Grant Discovery Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Grants Found**: {stats.get('total_grants', 0)}
- **Grants with Deadlines**: {stats.get('grants_with_deadlines', 0)}
- **Urgent Grants (Critical/High)**: {stats.get('grants_closing_soon', 0)}
- **Average Relevance Score**: {stats.get('avg_relevance_score', 0):.2f}

## Top Priority Grants

"""
            
            for i, grant in enumerate(priority_grants, 1):
                report_content += f"""### {i}. {grant.get('title', 'Unknown Title')}
- **Agency**: {grant.get('agency_name', grant.get('agency_code', 'Unknown'))}
- **Grant Number**: {grant.get('number', 'N/A')}
- **Status**: {grant.get('status', 'Unknown')}
- **Close Date**: {grant.get('close_date', 'No deadline')[:10] if grant.get('close_date') else 'No deadline'}
- **Urgency**: {grant.get('urgency', 'Unknown')}
- **Relevance Score**: {grant.get('relevance_score', 0)}
- **Priority Score**: {grant.get('priority_score', 0):.2f}
- **URL**: {grant.get('url', 'N/A')}

"""
            
            if urgent_grants:
                report_content += f"""## Urgent Grants (Closing Soon)

"""
                for grant in urgent_grants:
                    days_left = grant.get('days_until_deadline', 'Unknown')
                    report_content += f"""- **{grant.get('title', 'Unknown')}** - {grant.get('agency_code', 'Unknown')} - {days_left} days left
"""
            
            report_content += f"""
## Statistics by Category

### By Agency
"""
            for agency, count in stats.get('by_agency', {}).items():
                report_content += f"- {agency}: {count}\n"
            
            report_content += f"""
### By Status
"""
            for status, count in stats.get('by_status', {}).items():
                report_content += f"- {status}: {count}\n"
            
            report_content += f"""
### By Urgency Level
"""
            for urgency, count in stats.get('by_urgency', {}).items():
                report_content += f"- {urgency}: {count}\n"
            
            report_content += f"""
### By Funding Level
"""
            for level, count in stats.get('by_funding_level', {}).items():
                report_content += f"- {level}: {count}\n"
            
            report_content += f"""
## Data Sources
- grants.gov API
- Discovery Date: {self.grants_data.get('discovery_date', 'Unknown')[:19]}
- Search Keywords: {', '.join(self.grants_data.get('search_criteria', {}).get('keywords', []))}

## Next Steps
1. Review priority grants for alignment with organizational goals
2. Begin application preparation for urgent grants
3. Set up alerts for grants of interest
4. Research detailed requirements for top-priority opportunities

---
*Report generated by Grant Automation System*
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"Generated markdown report: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating markdown report: {str(e)}")
            raise
    
    def run_analysis(self, data_file: str = None) -> Dict:
        """Run complete grant analysis"""
        self.logger.info("Starting grant analysis")
        
        try:
            # Load data
            if not self.load_grant_data(data_file):
                return {'success': False, 'error': 'Failed to load grant data'}
            
            # Enrich data
            self.enrich_grant_data()
            
            # Generate reports
            excel_file = self.export_to_excel()
            markdown_file = self.generate_markdown_report()
            
            # Create summary
            stats = self.create_summary_statistics()
            
            result = {
                'success': True,
                'total_grants': len(self.processed_grants),
                'excel_report': excel_file,
                'markdown_report': markdown_file,
                'statistics': stats,
                'priority_grants_count': len(self.create_priority_list(10)),
                'urgent_grants_count': stats.get('grants_closing_soon', 0)
            }
            
            self.logger.info("Grant analysis completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in grant analysis: {str(e)}")
            return {'success': False, 'error': str(e)}

def main():
    """Main entry point for the analyzer"""
    print("Grant Data Analysis System")
    print("=" * 30)
    
    try:
        analyzer = GrantAnalyzer()
        results = analyzer.run_analysis()
        
        if results['success']:
            print(f"✅ Analysis completed successfully!")
            print(f"📊 Analyzed {results['total_grants']} grants")
            print(f"🎯 {results['priority_grants_count']} priority grants identified")
            print(f"⚠️  {results['urgent_grants_count']} urgent grants (closing soon)")
            print(f"📄 Excel report: {results['excel_report']}")
            print(f"📝 Markdown report: {results['markdown_report']}")
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

