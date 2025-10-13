#!/usr/bin/env python3
"""
Process October Grants CSV and Integrate into Enhanced System
Analyzes the uploaded grants and adds relevant ones to the targeted grants database
"""

import os
import sys
import csv
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))

class OctoberGrantsProcessor:
    """Process and integrate October grants into the enhanced system"""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.raw_grants = []
        self.relevant_grants = []
        self.business_categories = {
            'minority_business': [],
            'financial_literacy': [],
            'technology': [],
            'youth_empowerment': [],
            'community_development': []
        }
        
    def load_csv_data(self) -> bool:
        """Load grants from CSV file"""
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.raw_grants = list(reader)
            
            print(f"✅ Loaded {len(self.raw_grants)} grants from CSV")
            return True
            
        except Exception as e:
            print(f"❌ Error loading CSV: {str(e)}")
            return False
    
    def clean_amount(self, amount_str: str) -> str:
        """Clean and standardize grant amount strings"""
        if not amount_str or amount_str.lower() in ['unspecified amount', 'n/a', '']:
            return 'Varies'
        
        # Handle ranges like "US $10,000 - US $15,000"
        if ' - ' in amount_str:
            return amount_str.replace('US ', '$').replace('£', '£')
        
        # Handle "Up to" amounts
        if 'Up to' in amount_str:
            return amount_str.replace('US ', '$').replace('£', '£')
        
        # Handle "More than" amounts
        if 'More than' in amount_str:
            return amount_str.replace('US ', '$').replace('£', '£')
        
        # Handle "Approximately" amounts
        if 'Approximately' in amount_str:
            return amount_str.replace('US ', '$').replace('£', '£')
        
        # Handle numeric amounts
        try:
            amount = float(amount_str)
            if amount >= 1000000:
                return f"${amount:,.0f} (${amount/1000000:.1f}M)"
            elif amount >= 1000:
                return f"${amount:,.0f}"
            else:
                return f"${amount:.0f}"
        except:
            return amount_str.replace('US ', '$').replace('£', '£')
    
    def calculate_business_relevance(self, grant: Dict) -> Dict:
        """Calculate relevance to business focus areas"""
        relevance = {
            'minority_business': 0,
            'financial_literacy': 0,
            'technology': 0,
            'youth_empowerment': 0,
            'community_development': 0,
            'overall_score': 0
        }
        
        # Get text fields for analysis
        grant_name = (grant.get('Grant Name (Industries)', '') or '').lower()
        category = (grant.get('Catergory', '') or '').lower()
        
        text_to_analyze = f"{grant_name} {category}"
        
        # Minority business keywords
        minority_keywords = ['minority', 'black', 'diverse', 'equity', 'inclusion', 'underrepresented', 'bipoc']
        relevance['minority_business'] = sum(1 for keyword in minority_keywords if keyword in text_to_analyze)
        
        # Financial literacy keywords
        financial_keywords = ['financial', 'economic', 'loan', 'literacy', 'empowerment', 'development', 'community development']
        relevance['financial_literacy'] = sum(1 for keyword in financial_keywords if keyword in text_to_analyze)
        
        # Technology keywords
        tech_keywords = ['technology', 'ai', 'artificial intelligence', 'digital', 'innovation', 'data', 'tech']
        relevance['technology'] = sum(1 for keyword in tech_keywords if keyword in text_to_analyze)
        
        # Youth empowerment keywords
        youth_keywords = ['youth', 'education', 'stem', 'student', 'learning', 'school', 'children', 'family services']
        relevance['youth_empowerment'] = sum(1 for keyword in youth_keywords if keyword in text_to_analyze)
        
        # Community development keywords
        community_keywords = ['community', 'development', 'housing', 'neighborhood', 'local']
        relevance['community_development'] = sum(1 for keyword in community_keywords if keyword in text_to_analyze)
        
        # Category-based scoring
        if 'education' in category:
            relevance['youth_empowerment'] += 2
            relevance['financial_literacy'] += 1  # Financial literacy often involves education
        
        if 'community development' in category:
            relevance['community_development'] += 3
            relevance['minority_business'] += 1  # Community development often helps minority businesses
        
        if 'youth' in category or 'family' in category:
            relevance['youth_empowerment'] += 2
        
        if 'health' in category:
            relevance['community_development'] += 1
        
        # Calculate overall score
        relevance['overall_score'] = sum(relevance[key] for key in relevance if key != 'overall_score')
        
        return relevance
    
    def categorize_grant(self, grant: Dict, relevance: Dict) -> str:
        """Determine the primary category for a grant"""
        # Find the category with the highest relevance score
        max_score = 0
        primary_category = 'general'
        
        for category, score in relevance.items():
            if category != 'overall_score' and score > max_score:
                max_score = score
                primary_category = category
        
        # If no clear category, use the CSV category to make a best guess
        csv_category = (grant.get('Catergory', '') or '').lower()
        
        if max_score == 0:
            if 'education' in csv_category:
                return 'youth_empowerment'
            elif 'community' in csv_category:
                return 'community_development'
            elif 'health' in csv_category:
                return 'community_development'
            else:
                return 'general'
        
        return primary_category
    
    def process_grants(self) -> List[Dict]:
        """Process all grants and identify relevant ones"""
        relevant_grants = []
        
        for grant in self.raw_grants:
            # Calculate business relevance
            relevance = self.calculate_business_relevance(grant)
            
            # Only include grants with some relevance (score > 0)
            if relevance['overall_score'] > 0:
                # Determine primary category
                primary_category = self.categorize_grant(grant, relevance)
                
                # Create enhanced grant entry
                enhanced_grant = {
                    'name': grant.get('Grant Name (Industries)', 'Unknown Grant'),
                    'original_category': grant.get('Catergory', ''),
                    'business_category': primary_category,
                    'amount': self.clean_amount(grant.get('Grant Amount', '')),
                    'grant_type': grant.get('Grant Type', 'Monetary'),
                    'deadline': grant.get('Grant Deadline', ''),
                    'website': grant.get('Grantor Website', ''),
                    'business_relevance': relevance,
                    'relevance_score': relevance['overall_score'],
                    'source': 'october_grants_csv',
                    'added_date': datetime.now().isoformat(),
                    'priority': self.calculate_priority(relevance['overall_score']),
                    'focus': self.generate_focus_description(grant, primary_category),
                    'keywords': self.extract_keywords(grant, primary_category)
                }
                
                relevant_grants.append(enhanced_grant)
                
                # Add to category lists
                if primary_category in self.business_categories:
                    self.business_categories[primary_category].append(enhanced_grant)
        
        self.relevant_grants = relevant_grants
        print(f"✅ Identified {len(relevant_grants)} relevant grants from {len(self.raw_grants)} total grants")
        
        return relevant_grants
    
    def calculate_priority(self, relevance_score: int) -> str:
        """Calculate priority level based on relevance score"""
        if relevance_score >= 4:
            return 'HIGH'
        elif relevance_score >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_focus_description(self, grant: Dict, category: str) -> str:
        """Generate a focus description based on the grant and category"""
        grant_name = grant.get('Grant Name (Industries)', '')
        original_category = grant.get('Catergory', '')
        
        focus_templates = {
            'minority_business': f"Business development and community support - {original_category}",
            'financial_literacy': f"Economic empowerment and financial education - {original_category}",
            'technology': f"Technology innovation and digital advancement - {original_category}",
            'youth_empowerment': f"Youth development and educational support - {original_category}",
            'community_development': f"Community development and local impact - {original_category}",
            'general': f"General support - {original_category}"
        }
        
        return focus_templates.get(category, f"Support for {original_category}")
    
    def extract_keywords(self, grant: Dict, category: str) -> List[str]:
        """Extract relevant keywords for the grant"""
        keywords = []
        
        grant_name = (grant.get('Grant Name (Industries)', '') or '').lower()
        original_category = (grant.get('Catergory', '') or '').lower()
        
        # Category-specific keywords
        category_keywords = {
            'minority_business': ['business development', 'entrepreneurship', 'economic development'],
            'financial_literacy': ['financial education', 'economic empowerment', 'financial literacy'],
            'technology': ['technology', 'innovation', 'digital'],
            'youth_empowerment': ['education', 'youth development', 'learning'],
            'community_development': ['community development', 'local impact', 'neighborhood']
        }
        
        keywords.extend(category_keywords.get(category, []))
        
        # Add original category as keyword
        if original_category:
            keywords.append(original_category)
        
        # Extract key terms from grant name
        key_terms = ['education', 'community', 'youth', 'technology', 'development', 'support', 'program']
        for term in key_terms:
            if term in grant_name:
                keywords.append(term)
        
        return list(set(keywords))  # Remove duplicates
    
    def generate_summary_report(self) -> Dict:
        """Generate a summary report of the processing"""
        summary = {
            'total_grants_processed': len(self.raw_grants),
            'relevant_grants_found': len(self.relevant_grants),
            'by_business_category': {
                category: len(grants) for category, grants in self.business_categories.items()
            },
            'by_priority': {
                'HIGH': len([g for g in self.relevant_grants if g['priority'] == 'HIGH']),
                'MEDIUM': len([g for g in self.relevant_grants if g['priority'] == 'MEDIUM']),
                'LOW': len([g for g in self.relevant_grants if g['priority'] == 'LOW'])
            },
            'top_grants': sorted(self.relevant_grants, key=lambda x: x['relevance_score'], reverse=True)[:10],
            'processing_date': datetime.now().isoformat()
        }
        
        return summary
    
    def save_processed_grants(self, output_file: str = None) -> str:
        """Save processed grants to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"/home/ubuntu/grant_automation/data/october_grants_processed_{timestamp}.json"
        
        # Create comprehensive output
        output_data = {
            'processing_summary': self.generate_summary_report(),
            'relevant_grants': self.relevant_grants,
            'grants_by_category': self.business_categories,
            'metadata': {
                'source_file': self.csv_file_path,
                'processed_date': datetime.now().isoformat(),
                'total_processed': len(self.raw_grants),
                'relevant_found': len(self.relevant_grants)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Processed grants saved to: {output_file}")
        return output_file
    
    def update_enhanced_settings(self) -> bool:
        """Update the enhanced settings with new targeted grants"""
        try:
            # Read current enhanced settings
            settings_file = "/home/ubuntu/grant_automation/config/enhanced_settings.py"
            
            # Create new targeted grants entries
            new_targeted_grants = {}
            
            # Add top grants from each category
            for category, grants in self.business_categories.items():
                if grants:
                    # Sort by relevance score and take top 3 from each category
                    top_grants = sorted(grants, key=lambda x: x['relevance_score'], reverse=True)[:3]
                    
                    for grant in top_grants:
                        grant_key = grant['name'].replace(' ', '_').replace(',', '').replace('(', '').replace(')', '')[:50]
                        new_targeted_grants[grant_key] = {
                            'amount': grant['amount'],
                            'focus': grant['focus'],
                            'url': grant.get('website', ''),
                            'keywords': grant['keywords'],
                            'deadline_type': 'specific_date',
                            'deadline': grant.get('deadline', ''),
                            'category': category,
                            'priority': grant['priority'],
                            'source': 'october_grants_csv'
                        }
            
            # Save new targeted grants to a separate file for manual integration
            new_grants_file = "/home/ubuntu/grant_automation/config/october_targeted_grants.py"
            
            with open(new_grants_file, 'w', encoding='utf-8') as f:
                f.write("#!/usr/bin/env python3\n")
                f.write('"""\n')
                f.write("October Grants - Targeted Grants for Integration\n")
                f.write("Generated from October grants CSV processing\n")
                f.write('"""\n\n')
                f.write("# Additional targeted grants from October grants list\n")
                f.write("OCTOBER_TARGETED_GRANTS = {\n")
                
                for grant_name, grant_info in new_targeted_grants.items():
                    f.write(f"    '{grant_name}': {{\n")
                    for key, value in grant_info.items():
                        if isinstance(value, str):
                            f.write(f"        '{key}': '{value}',\n")
                        elif isinstance(value, list):
                            f.write(f"        '{key}': {value},\n")
                        else:
                            f.write(f"        '{key}': {value},\n")
                    f.write("    },\n")
                
                f.write("}\n")
            
            print(f"✅ New targeted grants saved to: {new_grants_file}")
            print(f"📊 Added {len(new_targeted_grants)} high-priority grants to targeted list")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating enhanced settings: {str(e)}")
            return False

def main():
    """Main processing function"""
    print("October Grants CSV Processor")
    print("=" * 30)
    
    csv_file = "/home/ubuntu/upload/CopyofNonprofitGuyNationalGrantList-OctoberGrants.csv"
    
    try:
        processor = OctoberGrantsProcessor(csv_file)
        
        # Load CSV data
        if not processor.load_csv_data():
            return 1
        
        # Process grants
        relevant_grants = processor.process_grants()
        
        # Generate summary
        summary = processor.generate_summary_report()
        
        # Save processed data
        output_file = processor.save_processed_grants()
        
        # Update enhanced settings
        processor.update_enhanced_settings()
        
        # Display results
        print("\n📊 Processing Summary:")
        print(f"   Total grants processed: {summary['total_grants_processed']}")
        print(f"   Relevant grants found: {summary['relevant_grants_found']}")
        print(f"   High priority grants: {summary['by_priority']['HIGH']}")
        print(f"   Medium priority grants: {summary['by_priority']['MEDIUM']}")
        print(f"   Low priority grants: {summary['by_priority']['LOW']}")
        
        print("\n🎯 Grants by Business Category:")
        for category, count in summary['by_business_category'].items():
            if count > 0:
                print(f"   {category.replace('_', ' ').title()}: {count} grants")
        
        print("\n🏆 Top 5 Most Relevant Grants:")
        for i, grant in enumerate(summary['top_grants'][:5], 1):
            print(f"   {i}. {grant['name']} (Score: {grant['relevance_score']}, Priority: {grant['priority']})")
        
        print(f"\n✅ Processing complete! Results saved to: {output_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error processing grants: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

