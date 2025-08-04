"""
ENHANCED PARTNERSHIP VERIFICATION SYSTEM V4
With AI Integration, Sentiment Analysis, and Comprehensive Scoring
"""

import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import json
import time
import re
from urllib.parse import urlparse
from datetime import datetime
import logging
from textblob import TextBlob
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Optional AI imports
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API KEY ---
SERPAPI_KEY = "f6def46c9232527e8bf9c37d6acf95e932f8ce13a63145e8c9e7d5d9950f4031"  # Replace with your SerpAPI key

class EnhancedPartnershipVerifier:
    def __init__(self):
        # Initialize AI models for sentiment analysis and text classification
        self.sentiment_analyzer = None
        self.partnership_classifier = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
                self.partnership_classifier = pipeline("text-classification", model="microsoft/DialoGPT-medium")
                logger.info("AI models loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load advanced models, using fallback: {e}")
        else:
            logger.info("Transformers not available, using fallback methods")
        
        # Enhanced search patterns for different types of relationships
        self.partnership_keywords = {
            'strong': ['official partner', 'strategic partnership', 'exclusive partnership', 'certified partner', 'premier partner'],
            'medium': ['collaboration', 'alliance', 'joint venture', 'working together', 'partnering with'],
            'weak': ['associates with', 'works with', 'connected to', 'relationship with']
        }
        
        self.negative_indicators = ['former partner', 'ended partnership', 'dispute', 'lawsuit', 'terminated', 'cancelled']
        
        # Alternative search sources for small companies
        self.alternative_sources = [
            'crunchbase.com',
            'linkedin.com/company',
            'facebook.com',
            'twitter.com',
            'instagram.com',
            'youtube.com',
            'medium.com',
            'github.com',
            'angel.co'
        ]

    def serp_search(self, query, num_results=5):
        """Enhanced search with better error handling and retry logic"""
        try:
            params = {
                "engine": "google", 
                "q": query, 
                "api_key": SERPAPI_KEY, 
                "num": num_results,
                "hl": "en",
                "gl": "us"
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            
            organic_results = results.get("organic_results", [])
            return [result.get("link") for result in organic_results[:num_results] if result.get("link")]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def get_company_domains(self, company_name):
        """Find multiple domains and social media presence for a company"""
        logger.info(f"Finding domains and online presence for '{company_name}'...")
        
        domains = []
        social_profiles = {}
        
        try:
            # Primary website search
            query = f'"{company_name}" official website'
            links = self.serp_search(query, 3)
            
            for link in links:
                if link:
                    domain = urlparse(link).netloc.replace('www.', '')
                    if domain and not any(social in domain for social in ['linkedin', 'facebook', 'twitter', 'instagram']):
                        domains.append(domain)
            
            # Social media and alternative platform search
            for platform in self.alternative_sources:
                query = f'site:{platform} "{company_name}"'
                platform_links = self.serp_search(query, 2)
                if platform_links:
                    social_profiles[platform] = platform_links[0]
            
            # Fallback domain generation
            if not domains:
                fallback_domain = company_name.lower().replace(' ', '').replace('-', '') + '.com'
                domains.append(fallback_domain)
                
        except Exception as e:
            logger.error(f"Error finding domains for {company_name}: {e}")
            
        return domains, social_profiles

    def analyze_text_sentiment_and_partnership(self, text, company_a, company_b):
        """Advanced text analysis using AI models"""
        results = {
            'partnership_strength': 0,
            'sentiment_score': 0,
            'partnership_type': 'none',
            'confidence': 0,
            'evidence_snippets': []
        }
        
        text_lower = text.lower()
        company_a_lower = company_a.lower()
        company_b_lower = company_b.lower()
        
        # Check if both companies are mentioned
        if company_a_lower not in text_lower or company_b_lower not in text_lower:
            return results
            
        # Extract relevant sentences
        sentences = re.split(r'[.!?]+', text)
        relevant_sentences = [s for s in sentences if company_a_lower in s.lower() and company_b_lower in s.lower()]
        
        if not relevant_sentences:
            return results
            
        # Analyze partnership strength based on keywords
        partnership_strength = 0
        partnership_type = 'none'
        evidence_snippets = []
        
        for sentence in relevant_sentences[:3]:  # Analyze top 3 relevant sentences
            sentence_lower = sentence.lower()
            
            # Check for negative indicators first
            if any(neg in sentence_lower for neg in self.negative_indicators):
                partnership_strength -= 30
                evidence_snippets.append(f"NEGATIVE: {sentence.strip()}")
                continue
                
            # Check partnership strength
            for strength, keywords in self.partnership_keywords.items():
                for keyword in keywords:
                    if keyword in sentence_lower:
                        if strength == 'strong':
                            partnership_strength += 40
                            partnership_type = 'strategic'
                        elif strength == 'medium':
                            partnership_strength += 25
                            partnership_type = 'collaborative'
                        elif strength == 'weak':
                            partnership_strength += 10
                            partnership_type = 'informal'
                        evidence_snippets.append(f"{strength.upper()}: {sentence.strip()}")
                        break
        
        # Sentiment analysis
        sentiment_score = 0
        if self.sentiment_analyzer and relevant_sentences:
            try:
                for sentence in relevant_sentences[:2]:
                    sentiment = self.sentiment_analyzer(sentence[:512])  # Limit length
                    if sentiment[0]['label'] == 'POSITIVE':
                        sentiment_score += sentiment[0]['score'] * 50
                    elif sentiment[0]['label'] == 'NEGATIVE':
                        sentiment_score -= sentiment[0]['score'] * 50
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
                # Fallback to TextBlob
                try:
                    blob = TextBlob(' '.join(relevant_sentences))
                    sentiment_score = blob.sentiment.polarity * 50
                except:
                    sentiment_score = 0
        
        results.update({
            'partnership_strength': max(0, min(100, partnership_strength)),
            'sentiment_score': max(-50, min(50, sentiment_score)),
            'partnership_type': partnership_type,
            'confidence': min(100, len(evidence_snippets) * 20),
            'evidence_snippets': evidence_snippets
        })
        
        return results

    def scrape_and_analyze_url(self, url, company_a, company_b):
        """Enhanced URL scraping with AI analysis"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Analyze the text
            analysis = self.analyze_text_sentiment_and_partnership(text, company_a, company_b)
            analysis['source_url'] = url
            analysis['source_domain'] = urlparse(url).netloc
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def check_official_websites(self, company_a, company_b, domains_a, domains_b):
        """Check official websites with enhanced search strategies"""
        logger.info(f"Checking official websites for partnership claims...")
        
        evidence = []
        
        # Check Company A's domains for Company B mentions
        for domain in domains_a[:2]:  # Check top 2 domains
            queries = [
                f'site:{domain} "{company_b}" partner',
                f'site:{domain} "{company_b}" collaboration',
                f'site:{domain} "{company_b}" alliance'
            ]
            
            for query in queries:
                urls = self.serp_search(query, 2)
                for url in urls:
                    if url:
                        analysis = self.scrape_and_analyze_url(url, company_a, company_b)
                        if analysis and analysis['partnership_strength'] > 0:
                            analysis['evidence_type'] = f'official_website_{company_a.lower()}'
                            analysis['credibility_multiplier'] = 1.5  # Higher credibility for official sites
                            evidence.append(analysis)
        
        # Check Company B's domains for Company A mentions
        for domain in domains_b[:2]:
            queries = [
                f'site:{domain} "{company_a}" partner',
                f'site:{domain} "{company_a}" collaboration',
                f'site:{domain} "{company_a}" alliance'
            ]
            
            for query in queries:
                urls = self.serp_search(query, 2)
                for url in urls:
                    if url:
                        analysis = self.scrape_and_analyze_url(url, company_a, company_b)
                        if analysis and analysis['partnership_strength'] > 0:
                            analysis['evidence_type'] = f'official_website_{company_b.lower()}'
                            analysis['credibility_multiplier'] = 1.5
                            evidence.append(analysis)
        
        return evidence

    def check_news_and_press(self, company_a, company_b):
        """Enhanced news and press release checking"""
        logger.info(f"Checking news sources for partnership information...")
        
        evidence = []
        
        news_queries = [
            f'"{company_a}" AND "{company_b}" partnership news',
            f'"{company_a}" AND "{company_b}" collaboration announcement',
            f'"{company_a}" AND "{company_b}" joint venture',
            f'"{company_a}" partners with "{company_b}"',
            f'"{company_b}" partners with "{company_a}"'
        ]
        
        for query in news_queries:
            urls = self.serp_search(query, 3)
            for url in urls:
                if url and any(news_site in url for news_site in ['news', 'press', 'reuters', 'bloomberg', 'techcrunch', 'venturebeat']):
                    analysis = self.scrape_and_analyze_url(url, company_a, company_b)
                    if analysis and analysis['partnership_strength'] > 0:
                        analysis['evidence_type'] = 'news_media'
                        analysis['credibility_multiplier'] = 1.3
                        evidence.append(analysis)
        
        return evidence

    def check_social_media_and_alternatives(self, company_a, company_b, social_profiles_a, social_profiles_b):
        """Check social media and alternative platforms"""
        logger.info(f"Checking social media and alternative platforms...")
        
        evidence = []
        
        # Check specific social profiles
        all_profiles = {**social_profiles_a, **social_profiles_b}
        
        for platform, profile_url in all_profiles.items():
            if profile_url:
                analysis = self.scrape_and_analyze_url(profile_url, company_a, company_b)
                if analysis and analysis['partnership_strength'] > 0:
                    analysis['evidence_type'] = f'social_media_{platform}'
                    analysis['credibility_multiplier'] = 0.7  # Lower credibility for social media
                    evidence.append(analysis)
        
        # General social media search
        social_queries = [
            f'site:linkedin.com "{company_a}" "{company_b}" partner',
            f'site:twitter.com "{company_a}" "{company_b}" collaboration',
            f'site:facebook.com "{company_a}" "{company_b}" partnership'
        ]
        
        for query in social_queries:
            urls = self.serp_search(query, 2)
            for url in urls:
                if url:
                    analysis = self.scrape_and_analyze_url(url, company_a, company_b)
                    if analysis and analysis['partnership_strength'] > 0:
                        analysis['evidence_type'] = 'social_media_general'
                        analysis['credibility_multiplier'] = 0.6
                        evidence.append(analysis)
        
        return evidence

    def check_industry_databases(self, company_a, company_b):
        """Check industry-specific databases and platforms"""
        logger.info(f"Checking industry databases...")
        
        evidence = []
        
        database_queries = [
            f'site:crunchbase.com "{company_a}" "{company_b}"',
            f'site:angel.co "{company_a}" "{company_b}" partner',
            f'site:github.com "{company_a}" "{company_b}" collaboration'
        ]
        
        for query in database_queries:
            urls = self.serp_search(query, 2)
            for url in urls:
                if url:
                    analysis = self.scrape_and_analyze_url(url, company_a, company_b)
                    if analysis and analysis['partnership_strength'] > 0:
                        analysis['evidence_type'] = 'industry_database'
                        analysis['credibility_multiplier'] = 1.1
                        evidence.append(analysis)
        
        return evidence

    def calculate_comprehensive_trust_score(self, all_evidence):
        """Calculate comprehensive trust score with AI-enhanced analysis"""
        if not all_evidence:
            return {
                'trust_score': 0,
                'confidence_level': 'Very Low',
                'verdict': '⚠️ No Evidence Found',
                'partnership_likelihood': 'Unlikely',
                'evidence_summary': {},
                'recommendations': ['No evidence of partnership found', 'Consider alternative verification methods']
            }
        
        # Aggregate scores by evidence type
        evidence_summary = defaultdict(list)
        total_weighted_score = 0
        total_weight = 0
        positive_evidence = 0
        negative_evidence = 0
        
        for evidence in all_evidence:
            evidence_type = evidence.get('evidence_type', 'unknown')
            partnership_strength = evidence.get('partnership_strength', 0)
            credibility_multiplier = evidence.get('credibility_multiplier', 1.0)
            sentiment_score = evidence.get('sentiment_score', 0)
            confidence = evidence.get('confidence', 0)
            
            # Calculate weighted score
            weighted_score = partnership_strength * credibility_multiplier
            weight = confidence / 100
            
            total_weighted_score += weighted_score * weight
            total_weight += weight
            
            # Count positive and negative evidence
            if partnership_strength > 0:
                positive_evidence += 1
            if sentiment_score < -10:
                negative_evidence += 1
            
            evidence_summary[evidence_type].append({
                'score': partnership_strength,
                'sentiment': sentiment_score,
                'confidence': confidence,
                'source': evidence.get('source_url', 'Unknown'),
                'snippets': evidence.get('evidence_snippets', [])
            })
        
        # Calculate final trust score
        if total_weight > 0:
            base_score = total_weighted_score / total_weight
        else:
            base_score = 0
        
        # Apply bonuses and penalties
        if len(evidence_summary) >= 3:  # Multiple source types
            base_score *= 1.2
        
        if negative_evidence > positive_evidence:
            base_score *= 0.5
        
        trust_score = max(0, min(100, base_score))
        
        # Determine confidence level and verdict
        if trust_score >= 80:
            confidence_level = 'Very High'
            verdict = '✅ Strong Partnership Evidence'
            partnership_likelihood = 'Very Likely'
        elif trust_score >= 60:
            confidence_level = 'High'
            verdict = '✅ Solid Partnership Evidence'
            partnership_likelihood = 'Likely'
        elif trust_score >= 40:
            confidence_level = 'Medium'
            verdict = '🔄 Moderate Partnership Evidence'
            partnership_likelihood = 'Possible'
        elif trust_score >= 20:
            confidence_level = 'Low'
            verdict = '⚠️ Weak Partnership Evidence'
            partnership_likelihood = 'Unlikely'
        else:
            confidence_level = 'Very Low'
            verdict = '❌ Insufficient Partnership Evidence'
            partnership_likelihood = 'Very Unlikely'
        
        # Generate recommendations
        recommendations = []
        if trust_score < 40:
            recommendations.append('Consider direct verification with companies')
            recommendations.append('Look for additional public announcements')
        if negative_evidence > 0:
            recommendations.append('Investigate negative indicators further')
        if len(evidence_summary) < 2:
            recommendations.append('Seek additional verification sources')
        
        return {
            'trust_score': round(trust_score, 2),
            'confidence_level': confidence_level,
            'verdict': verdict,
            'partnership_likelihood': partnership_likelihood,
            'positive_evidence_count': positive_evidence,
            'negative_evidence_count': negative_evidence,
            'evidence_types_found': len(evidence_summary),
            'evidence_summary': dict(evidence_summary),
            'recommendations': recommendations
        }

    def verify_partnership(self, company_a, company_b):
        """Main verification pipeline with comprehensive analysis"""
        logger.info(f"Starting comprehensive verification for '{company_a}' and '{company_b}'")
        
        start_time = datetime.now()
        
        # Get company domains and social profiles
        domains_a, social_profiles_a = self.get_company_domains(company_a)
        domains_b, social_profiles_b = self.get_company_domains(company_b)
        
        all_evidence = []
        
        # Run all verification checks
        try:
            # 1. Official websites
            website_evidence = self.check_official_websites(company_a, company_b, domains_a, domains_b)
            all_evidence.extend(website_evidence)
            
            # 2. News and press
            news_evidence = self.check_news_and_press(company_a, company_b)
            all_evidence.extend(news_evidence)
            
            # 3. Social media and alternatives
            social_evidence = self.check_social_media_and_alternatives(company_a, company_b, social_profiles_a, social_profiles_b)
            all_evidence.extend(social_evidence)
            
            # 4. Industry databases
            database_evidence = self.check_industry_databases(company_a, company_b)
            all_evidence.extend(database_evidence)
            
        except Exception as e:
            logger.error(f"Error during verification: {e}")
        
        # Calculate comprehensive trust score
        final_result = self.calculate_comprehensive_trust_score(all_evidence)
        
        # Add metadata
        final_result.update({
            'companies_verified': [company_a, company_b],
            'verification_timestamp': datetime.now().isoformat(),
            'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
            'domains_found': {
                company_a: domains_a,
                company_b: domains_b
            },
            'social_profiles_found': {
                company_a: social_profiles_a,
                company_b: social_profiles_b
            }
        })
        
        return final_result

def main():
    """Interactive main function with enhanced user experience"""
    print("="*60)
    print("🔍 ENHANCED PARTNERSHIP VERIFICATION SYSTEM V4")
    print("   With AI Integration & Comprehensive Analysis")
    print("="*60)
    
    verifier = EnhancedPartnershipVerifier()
    
    while True:
        print("\n" + "="*50)
        company_a = input("Enter Company A's name (or type 'exit' to quit): ").strip()
        if company_a.lower() == 'exit':
            break
            
        company_b = input(f"Enter Company B's name to verify against '{company_a}': ").strip()
        if company_b.lower() == 'exit':
            break

        print(f"\n🔎 Verifying partnership between '{company_a}' and '{company_b}'...")
        print("⏳ This may take 30-60 seconds for comprehensive analysis...")
        
        try:
            result = verifier.verify_partnership(company_a, company_b)
            
            print("\n" + "="*60)
            print("📊 VERIFICATION RESULTS")
            print("="*60)
            
            print(f"🏢 Companies: {result['companies_verified'][0]} ↔ {result['companies_verified'][1]}")
            print(f"🎯 Trust Score: {result['trust_score']}/100")
            print(f"📈 Confidence Level: {result['confidence_level']}")
            print(f"🎭 Partnership Likelihood: {result['partnership_likelihood']}")
            print(f"✅ Positive Evidence: {result['positive_evidence_count']} sources")
            print(f"❌ Negative Evidence: {result['negative_evidence_count']} sources")
            print(f"📁 Evidence Types Found: {result['evidence_types_found']}")
            print(f"⏱ Processing Time: {result['processing_time_seconds']:.2f} seconds")
            print(f"\n{result['verdict']}")
            
            if result['recommendations']:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"   {i}. {rec}")
            
            # Show detailed evidence if available
            if result['evidence_summary']:
                print(f"\n📋 Evidence Summary:")
                for evidence_type, evidence_list in result['evidence_summary'].items():
                    print(f"\n  📌 {evidence_type.replace('_', ' ').title()}:")
                    for evidence in evidence_list:
                        print(f"     Score: {evidence['score']}, Confidence: {evidence['confidence']}%")
                        if evidence['snippets']:
                            for snippet in evidence['snippets'][:2]:  # Show first 2 snippets
                                print(f"     💬 {snippet}")
            
            # Ask if user wants full JSON output
            show_json = input("\n🔍 Show detailed JSON output? (y/n): ").lower().strip()
            if show_json == 'y':
                print("\n" + "="*60)
                print("📄 DETAILED JSON OUTPUT")
                print("="*60)
                print(json.dumps(result, indent=2))
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            print(f"❌ Error during verification: {e}")
            print("Please try again with different company names.")

if __name__ == "__main__":
    main()