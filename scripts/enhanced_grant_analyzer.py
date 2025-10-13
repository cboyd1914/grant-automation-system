#!/usr/bin/env python3
"""
Enhanced Grant Analysis and Processing Script
Analyzes discovered grants with business-specific targeting and scoring
"""

import os
import sys
import json
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))
from enhanced_settings import *

class EnhancedGrantAnalyzer:
    """Enhanced grant analyzer with business-specific targeting"""
    
    def __init__(self, data_file: str = None):
        self.setup_logging()
        self.data_file = data_file
        self.grants_data = None
        self.processed_grants = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(LOGS_DIR, f'enhanced_grant_analyzer_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced Grant Analyzer Initialized")
    
    def load_grant_data(self, data_file: str = None) -> bool:
        """Load grant data from JSON file"""
        if data_file:
            self.data_file = data_file
        
        if not self.data_file:
            # Find the most recent enhanced data file
            data_files = [f for f in os.listdir(DATA_DIR) if f.startswith('enhanced_grants_discovery_') and f.endswith('.json')]
            if not data_files:
                # Fall back to regular discovery files
                data_files = [f for f in os.listdir(DATA_DIR) if f.startswith('grants_discovery_') and f.endswith('.json')]
            
            if not data_files:
                self.logger.error("No grant data files found")
                return False
            
            data_files.sort(reverse=True)
            self.data_file = os.path.join(DATA_DIR, data_files[0])
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.grants_data = json.load(f)
            
            # Handle both enhanced and regular data formats
            if 'all_grants' in self.grants_data:
                grants_count = len(self.grants_data['all_grants'])
            else:
                grants_count = len(self.grants_data.get('grants', []))
            
            self.logger.info(f"Loaded {grants_count} grants from {self.data_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading grant data: {str(e)}")
            return False
    
    def enrich_grant_data(self) -> List[Dict]:
        """Enrich grant data with business-specific analysis"""
        self.logger.info("Enriching grant data with business-specific analysis")
        
        # Get grants from data structure
        if 'all_grants' in self.grants_data:
            grants = self.grants_data['all_grants']
        else:
            grants = self.grants_data.get('grants', [])
        
        enriched_grants = []
        
        for grant in grants:
            enriched_grant = grant.copy()
            
            # Business alignment scoring
            enriched_grant['business_alignment'] = self.calculate_business_alignment(grant)
            
            # Geographic relevance
            enriched_grant['geographic_relevance'] = self.calculate_geographic_relevance(grant)
            
            # Funding tier classification
            enriched_grant['funding_tier'] = self.classify_funding_tier(grant)
            
            # Application complexity assessment
            enriched_grant['application_complexity'] = self.assess_application_complexity(grant)
            
            # Strategic priority
            enriched_grant['strategic_priority'] = self.calculate_strategic_priority(grant)
            
            # Days until deadline (if applicable)
            if grant.get('close_date'):
                try:
                    close_date = datetime.fromisoformat(grant['close_date'].replace('Z', '+00:00'))
                    days_until_deadline = (close_date - datetime.now()).days
                    enriched_grant['days_until_deadline'] = days_until_deadline
                    enriched_grant['urgency'] = self.calculate_urgency(days_until_deadline)
                except:
                    enriched_grant['days_until_deadline'] = None
                    enriched_grant['urgency'] = 'Unknown'
            else:
                enriched_grant['days_until_deadline'] = None
                enriched_grant['urgency'] = 'No Deadline'
            
            # Enhanced relevance score
            if 'relevance_score' not in enriched_grant:
                enriched_grant['relevance_score'] = self.calculate_enhanced_relevance_score(grant)
            
            enriched_grants.append(enriched_grant)
        
        self.processed_grants = enriched_grants
        self.logger.info(f"Enriched {len(enriched_grants)} grants with business-specific data")
        return enriched_grants
    
    def calculate_business_alignment(self, grant: Dict) -> Dict:
        """Calculate how well the grant aligns with business focus areas"""
        alignment = {
            'minority_business': 0,
            'financial_literacy': 0,
            'technology': 0,
            'youth_empowerment': 0,
            'overall_score': 0
        }
        
        # Get text fields for analysis
        text_fields = [
            grant.get('title', ''),
            grant.get('focus', ''),
            grant.get('name', ''),
            ' '.join(grant.get('keywords', []))
        ]
        text = ' '.join(text_fields).lower()
        
        # Minority business alignment
        minority_keywords = ['minority', 'black', 'diverse', 'underrepresented', 'bipoc', 'equity']
        alignment['minority_business'] = sum(1 for keyword in minority_keywords if keyword in text)
        
        # Financial literacy alignment
        financial_keywords = ['financial', 'economic', 'loan', 'literacy', 'empowerment', 'coaching']
        alignment['financial_literacy'] = sum(1 for keyword in financial_keywords if keyword in text)
        
        # Technology alignment
        tech_keywords = ['technology', 'ai', 'artificial', 'digital', 'innovation', 'tech', 'consulting']
        alignment['technology'] = sum(1 for keyword in tech_keywords if keyword in text)
        
        # Youth empowerment alignment
        youth_keywords = ['youth', 'education', 'stem', 'student', 'learning', 'teen']
        alignment['youth_empowerment'] = sum(1 for keyword in youth_keywords if keyword in text)
        
        # Calculate overall score
        alignment['overall_score'] = sum(alignment[key] for key in alignment if key != 'overall_score')
        
        return alignment
    
    def calculate_geographic_relevance(self, grant: Dict) -> str:
        """Calculate geographic relevance to target locations"""
        grant_location = grant.get('location', '').lower()
        
        # Check for specific target locations
        for location in TARGET_LOCATIONS:
            if location.lower() in grant_location:
                return f"High - {location}"
        
        # Check for state matches
        target_states = ['missouri', 'texas', 'illinois', 'mo', 'tx', 'il']
        for state in target_states:
            if state in grant_location:
                return f"Medium - {state.upper()}"
        
        # Check if it's national
        if 'national' in grant_location or grant_location == '':
            return "Medium - National"
        
        return "Low - Other location"
    
    def classify_funding_tier(self, grant: Dict) -> str:
        """Classify grant into funding tiers"""
        amount_str = grant.get('amount', '').lower()
        
        if any(indicator in amount_str for indicator in ['$1m', '1,000,000', '$500,000']):
            return "Large ($500K+)"
        elif any(indicator in amount_str for indicator in ['$100,000', '$150,000', '$200,000']):
            return "Medium ($100K-$500K)"
        elif any(indicator in amount_str for indicator in ['$50,000', '$25,000']):
            return "Small ($25K-$100K)"
        elif any(indicator in amount_str for indicator in ['$10,000', '$20,000']):
            return "Micro ($10K-$25K)"
        else:
            return "Unknown"
    
    def assess_application_complexity(self, grant: Dict) -> str:
        """Assess the likely complexity of the grant application"""
        # Federal grants are typically more complex
        if grant.get('source') == 'grants.gov':
            if grant.get('agency_code') in ['DOE', 'NSF', 'NIH']:
                return "High - Federal research grant"
            else:
                return "Medium - Federal grant"
        
        # Targeted grants from our list
        elif grant.get('source') == 'targeted_list':
            if 'Black Ambition' in grant.get('name', ''):
                return "High - Competitive prize"
            elif any(name in grant.get('name', '') for name in ['Google', 'Chan Zuckerberg']):
                return "Medium - Corporate/Foundation"
            else:
                return "Low - Application-based"
        
        return "Unknown"
    
    def calculate_strategic_priority(self, grant: Dict) -> str:
        """Calculate strategic priority based on business goals"""
        score = 0
        
        # Business alignment bonus
        alignment = self.calculate_business_alignment(grant)
        score += alignment['overall_score']
        
        # Category-specific bonuses
        category = grant.get('category', '')
        if category in ['minority_business', 'technology']:
            score += 3
        elif category in ['financial_literacy', 'youth_empowerment']:
            score += 2
        
        # Amount-based priority
        funding_tier = self.classify_funding_tier(grant)
        if 'Large' in funding_tier:
            score += 2
        elif 'Medium' in funding_tier:
            score += 1
        
        # Source-based priority
        if grant.get('source') == 'targeted_list':
            score += 2
        
        # Determine priority level
        if score >= 8:
            return "CRITICAL"
        elif score >= 5:
            return "HIGH"
        elif score >= 3:
            return "MEDIUM"
        else:
            return "LOW"
    
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
    
    def calculate_enhanced_relevance_score(self, grant: Dict) -> float:
        """Calculate enhanced relevance score"""
        score = grant.get('relevance_score', 0)
        
        # Add business alignment bonus
        alignment = self.calculate_business_alignment(grant)
        score += alignment['overall_score'] * 0.5
        
        # Add strategic priority bonus
        priority = self.calculate_strategic_priority(grant)
        if priority == 'CRITICAL':
            score += 2.0
        elif priority == 'HIGH':
            score += 1.5
        elif priority == 'MEDIUM':
            score += 1.0
        
        return round(score, 2)
    
    def create_business_specific_analysis(self) -> Dict:
        """Create business-specific analysis and insights"""
        if not self.processed_grants:
            return {}
        
        df = pd.DataFrame(self.processed_grants)
        
        analysis = {
            'total_grants': len(self.processed_grants),
            'by_strategic_priority': df['strategic_priority'].value_counts().to_dict(),
            'by_funding_tier': df['funding_tier'].value_counts().to_dict(),
            'by_business_category': df.get('category', pd.Series()).value_counts().to_dict(),
            'by_urgency': df['urgency'].value_counts().to_dict(),
            'by_application_complexity': df['application_complexity'].value_counts().to_dict(),
            'geographic_distribution': df['geographic_relevance'].value_counts().to_dict(),
            'high_alignment_grants': len(df[df.apply(lambda x: x.get('business_alignment', {}).get('overall_score', 0) >= 3, axis=1)]),
            'critical_priority_grants': len(df[df['strategic_priority'] == 'CRITICAL']),
            'urgent_deadlines': len(df[df['urgency'].isin(['Critical', 'High'])]),
            'avg_relevance_score': df['relevance_score'].mean() if 'relevance_score' in df.columns else 0
        }
        
        return analysis
    
    def create_action_plan(self) -> List[Dict]:
        """Create prioritized action plan for grant applications"""
        if not self.processed_grants:
            return []
        
        # Sort grants by strategic priority and relevance score
        priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        
        sorted_grants = sorted(
            self.processed_grants,
            key=lambda x: (
                priority_order.get(x.get('strategic_priority', 'LOW'), 0),
                x.get('relevance_score', 0),
                -x.get('days_until_deadline', 999) if x.get('days_until_deadline') else 0
            ),
            reverse=True
        )
        
        action_plan = []
        for i, grant in enumerate(sorted_grants[:10], 1):  # Top 10 grants
            action_item = {
                'rank': i,
                'grant_name': grant.get('title') or grant.get('name', 'Unknown'),
                'strategic_priority': grant.get('strategic_priority', 'Unknown'),
                'funding_tier': grant.get('funding_tier', 'Unknown'),
                'urgency': grant.get('urgency', 'Unknown'),
                'days_until_deadline': grant.get('days_until_deadline'),
                'application_complexity': grant.get('application_complexity', 'Unknown'),
                'business_alignment_score': grant.get('business_alignment', {}).get('overall_score', 0),
                'recommended_action': self.get_recommended_action(grant),
                'url': grant.get('url', ''),
                'notes': self.generate_grant_notes(grant)
            }
            action_plan.append(action_item)
        
        return action_plan
    
    def get_recommended_action(self, grant: Dict) -> str:
        """Get recommended action for a grant"""
        priority = grant.get('strategic_priority', 'LOW')
        urgency = grant.get('urgency', 'Unknown')
        complexity = grant.get('application_complexity', 'Unknown')
        
        if priority == 'CRITICAL' and urgency in ['Critical', 'High']:
            return "IMMEDIATE APPLICATION - Start today"
        elif priority == 'CRITICAL':
            return "HIGH PRIORITY - Begin application within 1 week"
        elif priority == 'HIGH' and urgency in ['Critical', 'High']:
            return "URGENT - Review and apply within 3 days"
        elif priority == 'HIGH':
            return "PRIORITY - Begin application within 2 weeks"
        elif urgency in ['Critical', 'High']:
            return "TIME SENSITIVE - Review for quick application"
        else:
            return "RESEARCH - Gather more information and prepare"
    
    def generate_grant_notes(self, grant: Dict) -> str:
        """Generate specific notes for each grant"""
        notes = []
        
        # Business alignment notes
        alignment = grant.get('business_alignment', {})
        if alignment.get('minority_business', 0) > 0:
            notes.append("Strong minority business focus")
        if alignment.get('financial_literacy', 0) > 0:
            notes.append("Aligns with financial literacy services")
        if alignment.get('technology', 0) > 0:
            notes.append("Good fit for AI consulting services")
        if alignment.get('youth_empowerment', 0) > 0:
            notes.append("Matches youth empowerment mission")
        
        # Geographic notes
        geo_relevance = grant.get('geographic_relevance', '')
        if 'High' in geo_relevance:
            notes.append(f"Local opportunity: {geo_relevance}")
        
        # Deadline notes
        days_left = grant.get('days_until_deadline')
        if days_left and days_left <= 14:
            notes.append(f"Deadline in {days_left} days")
        
        return "; ".join(notes) if notes else "Review grant details for alignment"
    
    def export_enhanced_excel(self, filename: str = None) -> str:
        """Export enhanced analysis to Excel"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_grants_analysis_{timestamp}.xlsx"
        
        filepath = os.path.join(REPORTS_DIR, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Action Plan sheet
                action_plan = self.create_action_plan()
                df_action = pd.DataFrame(action_plan)
                df_action.to_excel(writer, sheet_name='Action Plan', index=False)
                
                # All grants with enhanced data
                df_all = pd.DataFrame(self.processed_grants)
                df_all.to_excel(writer, sheet_name='All Grants Enhanced', index=False)
                
                # Business analysis
                analysis = self.create_business_specific_analysis()
                df_analysis = pd.DataFrame(list(analysis.items()), columns=['Metric', 'Value'])
                df_analysis.to_excel(writer, sheet_name='Business Analysis', index=False)
                
                # Critical priority grants
                critical_grants = [g for g in self.processed_grants if g.get('strategic_priority') == 'CRITICAL']
                if critical_grants:
                    df_critical = pd.DataFrame(critical_grants)
                    df_critical.to_excel(writer, sheet_name='Critical Priority', index=False)
                
                # Grants by category
                for category in ['minority_business', 'financial_literacy', 'technology', 'youth_empowerment']:
                    category_grants = [g for g in self.processed_grants if g.get('category') == category]
                    if category_grants:
                        df_category = pd.DataFrame(category_grants)
                        sheet_name = category.replace('_', ' ').title()[:31]  # Excel sheet name limit
                        df_category.to_excel(writer, sheet_name=sheet_name, index=False)
            
            self.logger.info(f"Enhanced Excel analysis exported to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error exporting enhanced Excel: {str(e)}")
            raise
    
    def generate_enhanced_markdown_report(self, filename: str = None) -> str:
        """Generate enhanced markdown report with business insights"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_grants_report_{timestamp}.md"
        
        filepath = os.path.join(REPORTS_DIR, filename)
        
        try:
            analysis = self.create_business_specific_analysis()
            action_plan = self.create_action_plan()
            
            report_content = f"""# Enhanced Grant Discovery Report
*Business-Focused Analysis for Minority-Owned Tech & Financial Literacy Services*

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Executive Summary

- **Total Grants Analyzed**: {analysis.get('total_grants', 0)}
- **Critical Priority Grants**: {analysis.get('critical_priority_grants', 0)}
- **High Business Alignment**: {analysis.get('high_alignment_grants', 0)}
- **Urgent Deadlines**: {analysis.get('urgent_deadlines', 0)}
- **Average Relevance Score**: {analysis.get('avg_relevance_score', 0):.2f}

## 🚀 Top Priority Action Plan

"""
            
            for item in action_plan[:5]:  # Top 5 action items
                report_content += f"""### {item['rank']}. {item['grant_name']}
- **Strategic Priority**: {item['strategic_priority']}
- **Funding Tier**: {item['funding_tier']}
- **Urgency**: {item['urgency']}
- **Application Complexity**: {item['application_complexity']}
- **Business Alignment Score**: {item['business_alignment_score']}/10
- **Recommended Action**: {item['recommended_action']}
- **Notes**: {item['notes']}
- **URL**: {item['url']}

"""
            
            report_content += f"""## 📊 Business-Specific Analysis

### Strategic Priority Distribution
"""
            for priority, count in analysis.get('by_strategic_priority', {}).items():
                report_content += f"- {priority}: {count} grants\n"
            
            report_content += f"""
### Funding Tier Analysis
"""
            for tier, count in analysis.get('by_funding_tier', {}).items():
                report_content += f"- {tier}: {count} grants\n"
            
            report_content += f"""
### Business Category Focus
"""
            for category, count in analysis.get('by_business_category', {}).items():
                if category:
                    report_content += f"- {category.replace('_', ' ').title()}: {count} grants\n"
            
            report_content += f"""
### Geographic Distribution
"""
            for location, count in analysis.get('geographic_distribution', {}).items():
                report_content += f"- {location}: {count} grants\n"
            
            report_content += f"""
## 🎯 Business Alignment Insights

### Minority-Owned Business Opportunities
Focus on grants specifically targeting Black-owned and minority-led businesses. These typically offer:
- Direct funding without equity requirements
- Additional support services (marketing, mentoring)
- Network access and partnership opportunities

### Financial Literacy & Economic Empowerment
Leverage your student loan coaching and financial education expertise for:
- Community development grants
- Financial literacy program funding
- Economic mobility initiatives

### Technology & AI Consulting
Position your AI consulting services for:
- Digital equity initiatives
- Workforce development programs
- Innovation and entrepreneurship grants

### Youth Empowerment & STEM
Your youth AI empowerment vision aligns with:
- Educational technology grants
- STEM education funding
- Youth development programs

## 📋 Next Steps & Recommendations

### Immediate Actions (Next 7 Days)
1. **Apply to Critical Priority grants** with approaching deadlines
2. **Research application requirements** for top 3 strategic matches
3. **Prepare standard application materials** (business plan, financial statements)

### Short-term Actions (Next 30 Days)
1. **Submit applications** for high-priority grants
2. **Network with grant administrators** and previous recipients
3. **Develop partnerships** to strengthen applications

### Long-term Strategy (Next 90 Days)
1. **Build track record** with smaller grants first
2. **Document impact metrics** for future applications
3. **Expand service offerings** to match grant opportunities

## 📞 Resources & Support

### Grant Writing Support
- Consider hiring grant writing consultant for large applications
- Join minority business entrepreneur networks
- Attend grant writing workshops

### Application Materials Needed
- Updated business plan with impact metrics
- Financial statements and projections
- Letters of support from community partners
- Detailed program descriptions

---

*This report was generated by the Enhanced Grant Automation System*
*For questions or support, review the grant details and application requirements*
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"Enhanced markdown report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating enhanced markdown report: {str(e)}")
            raise
    
    def run_enhanced_analysis(self, data_file: str = None) -> Dict:
        """Run complete enhanced grant analysis"""
        self.logger.info("Starting enhanced grant analysis")
        
        try:
            # Load data
            if not self.load_grant_data(data_file):
                return {'success': False, 'error': 'Failed to load grant data'}
            
            # Enrich data with business-specific analysis
            self.enrich_grant_data()
            
            # Generate enhanced reports
            excel_file = self.export_enhanced_excel()
            markdown_file = self.generate_enhanced_markdown_report()
            
            # Create business analysis
            analysis = self.create_business_specific_analysis()
            action_plan = self.create_action_plan()
            
            result = {
                'success': True,
                'total_grants': len(self.processed_grants),
                'excel_report': excel_file,
                'markdown_report': markdown_file,
                'business_analysis': analysis,
                'action_plan_count': len(action_plan),
                'critical_priority_grants': analysis.get('critical_priority_grants', 0),
                'urgent_grants_count': analysis.get('urgent_deadlines', 0)
            }
            
            self.logger.info("Enhanced grant analysis completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in enhanced grant analysis: {str(e)}")
            return {'success': False, 'error': str(e)}

def main():
    """Main entry point for enhanced analyzer"""
    print("Enhanced Grant Analysis System")
    print("=" * 35)
    
    try:
        analyzer = EnhancedGrantAnalyzer()
        results = analyzer.run_enhanced_analysis()
        
        if results['success']:
            print(f"✅ Enhanced analysis completed successfully!")
            print(f"📊 Analyzed {results['total_grants']} grants")
            print(f"🎯 {results['critical_priority_grants']} critical priority grants identified")
            print(f"⚠️  {results['urgent_grants_count']} urgent grants (closing soon)")
            print(f"📋 {results['action_plan_count']} items in action plan")
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

