"""
🔍 ENHANCED PARTNERSHIP VERIFICATION SYSTEM V4 - NOTEBOOK VERSION
Complete self-contained system that works perfectly in Jupyter notebooks
Fixes all import issues and provides accurate trust scoring
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urlparse
from datetime import datetime
import logging
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Optional AI imports
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    print("✅ AI models available - enhanced analysis enabled")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ AI models not available - using fallback methods")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    print("❌ SerpAPI not available - install with: pip install google-search-results")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- IMPORTANT: CONFIGURE YOUR API KEY HERE ---
SERPAPI_KEY = "your_serpapi_key_here"  # ⚠️ REPLACE WITH YOUR ACTUAL KEY

class EnhancedPartnershipVerifier:
    def __init__(self, api_key=None):
        """
        Initialize the Enhanced Partnership Verifier
        
        Args:
            api_key (str): Your SerpAPI key. If None, uses the global SERPAPI_KEY
        """
        self.api_key = api_key or SERPAPI_KEY
        
        # Initialize AI models
        self.sentiment_analyzer = None
        self.partnership_classifier = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                print("🤖 Loading AI models...")
                self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                                 model="cardiffnlp/twitter-roberta-base-sentiment-latest")
                logger.info("✅ AI sentiment model loaded successfully")
            except Exception as e:
                logger.warning(f"⚠️ Could not load advanced AI models: {e}")
        
        # Enhanced search patterns for different types of relationships
        self.partnership_keywords = {
            'strong': [
                'official partner', 'strategic partnership', 'exclusive partnership', 
                'certified partner', 'premier partner', 'authorized partner',
                'technology partner', 'platinum partner', 'gold partner'
            ],
            'medium': [
                'collaboration', 'alliance', 'joint venture', 'working together', 
                'partnering with', 'cooperating with', 'joint development',
                'business partnership', 'strategic alliance'
            ],
            'weak': [
                'associates with', 'works with', 'connected to', 'relationship with',
                'engaged with', 'involved with', 'affiliated with'
            ]
        }
        
        self.negative_indicators = [
            'former partner', 'ended partnership', 'dispute', 'lawsuit', 
            'terminated', 'cancelled', 'dissolved partnership', 'broke ties',
            'ended collaboration', 'ceased partnership'
        ]
        
        # Alternative search sources for comprehensive coverage
        self.search_sources = {
            'official': ['site:', 'official website', 'company website'],
            'news': ['news', 'press release', 'announcement', 'techcrunch', 'reuters'],
            'social': ['linkedin.com', 'twitter.com', 'facebook.com'],
            'databases': ['crunchbase.com', 'angel.co', 'github.com'],
            'industry': ['partnerships', 'collaborations', 'alliances']
        }

    def test_api_connection(self):
        """Test if SerpAPI key is working"""
        if not SERPAPI_AVAILABLE:
            return False, "SerpAPI library not installed"
            
        if not self.api_key or self.api_key == "your_serpapi_key_here":
            return False, "API key not configured"
            
        try:
            # Test with a simple search
            params = {
                "engine": "google",
                "q": "test search",
                "api_key": self.api_key,
                "num": 1
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "error" in results:
                return False, f"API Error: {results['error']}"
            
            return True, "API connection successful"
            
        except Exception as e:
            return False, f"Connection failed: {e}"

    def enhanced_search(self, query, num_results=5):
        """Enhanced search with better error handling and multiple strategies"""
        if not SERPAPI_AVAILABLE:
            logger.error("SerpAPI not available")
            return []
            
        if not self.api_key or self.api_key == "your_serpapi_key_here":
            logger.error("API key not configured")
            return []
            
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "hl": "en",
                "gl": "us"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "error" in results:
                logger.error(f"Search API error: {results['error']}")
                return []
            
            organic_results = results.get("organic_results", [])
            links = []
            
            for result in organic_results[:num_results]:
                link = result.get("link")
                if link and self.is_valid_url(link):
                    links.append({
                        'url': link,
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'domain': urlparse(link).netloc
                    })
            
            return links
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def is_valid_url(self, url):
        """Check if URL is valid and accessible"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except:
            return False

    def get_company_info(self, company_name):
        """Get comprehensive company information from multiple sources"""
        logger.info(f"🔍 Discovering information for '{company_name}'...")
        
        company_info = {
            'domains': [],
            'social_profiles': {},
            'alternative_names': []
        }
        
        # Search for official website
        website_queries = [
            f'"{company_name}" official website',
            f'"{company_name}" company site',
            f'{company_name} homepage'
        ]
        
        for query in website_queries:
            results = self.enhanced_search(query, 3)
            for result in results:
                domain = result['domain']
                if domain and not any(social in domain.lower() for social in 
                                    ['linkedin', 'facebook', 'twitter', 'instagram', 'youtube']):
                    if domain not in company_info['domains']:
                        company_info['domains'].append(domain)
        
        # Search for social media presence
        social_platforms = {
            'linkedin': f'site:linkedin.com/company "{company_name}"',
            'twitter': f'site:twitter.com "{company_name}"',
            'facebook': f'site:facebook.com "{company_name}"',
            'crunchbase': f'site:crunchbase.com "{company_name}"',
            'github': f'site:github.com "{company_name}"'
        }
        
        for platform, query in social_platforms.items():
            results = self.enhanced_search(query, 2)
            if results:
                company_info['social_profiles'][platform] = results[0]['url']
        
        # Generate fallback domain if none found
        if not company_info['domains']:
            fallback = company_name.lower().replace(' ', '').replace('-', '') + '.com'
            company_info['domains'].append(fallback)
            
        logger.info(f"✅ Found {len(company_info['domains'])} domains and {len(company_info['social_profiles'])} social profiles")
        
        return company_info

    def extract_and_analyze_content(self, url, company_a, company_b):
        """Extract and analyze content from URL with enhanced AI analysis"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean and prepare text
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text[:5000]  # Limit text length for processing
            
            # Analyze the content
            analysis = self.analyze_partnership_content(text, company_a, company_b)
            analysis['source_url'] = url
            analysis['source_domain'] = urlparse(url).netloc
            
            return analysis
            
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ Timeout accessing {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"🌐 Error accessing {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"💥 Unexpected error processing {url}: {e}")
            return None

    def analyze_partnership_content(self, text, company_a, company_b):
        """Advanced content analysis with AI and pattern matching"""
        analysis = {
            'partnership_strength': 0,
            'sentiment_score': 0,
            'partnership_type': 'none',
            'confidence': 0,
            'evidence_snippets': [],
            'keyword_matches': []
        }
        
        text_lower = text.lower()
        company_a_lower = company_a.lower()
        company_b_lower = company_b.lower()
        
        # Check if both companies are mentioned
        if company_a_lower not in text_lower or company_b_lower not in text_lower:
            return analysis
        
        # Extract relevant sentences
        sentences = re.split(r'[.!?]+', text)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if (len(sentence_clean) > 20 and 
                company_a_lower in sentence_clean.lower() and 
                company_b_lower in sentence_clean.lower()):
                relevant_sentences.append(sentence_clean)
        
        if not relevant_sentences:
            return analysis
        
        # Analyze partnership indicators
        partnership_strength = 0
        partnership_type = 'none'
        evidence_snippets = []
        keyword_matches = []
        
        for sentence in relevant_sentences[:5]:  # Analyze top 5 relevant sentences
            sentence_lower = sentence.lower()
            
            # Check for negative indicators first
            negative_found = False
            for neg_indicator in self.negative_indicators:
                if neg_indicator in sentence_lower:
                    partnership_strength -= 25
                    evidence_snippets.append(f"🚫 NEGATIVE: {sentence}")
                    keyword_matches.append(f"Negative: {neg_indicator}")
                    negative_found = True
                    break
            
            if negative_found:
                continue
            
            # Check partnership strength indicators
            for strength_level, keywords in self.partnership_keywords.items():
                for keyword in keywords:
                    if keyword in sentence_lower:
                        if strength_level == 'strong':
                            partnership_strength += 35
                            partnership_type = 'strategic'
                            evidence_snippets.append(f"🟢 STRONG: {sentence}")
                        elif strength_level == 'medium':
                            partnership_strength += 20
                            partnership_type = 'collaborative'
                            evidence_snippets.append(f"🟡 MEDIUM: {sentence}")
                        elif strength_level == 'weak':
                            partnership_strength += 8
                            partnership_type = 'informal'
                            evidence_snippets.append(f"🔵 WEAK: {sentence}")
                        
                        keyword_matches.append(f"{strength_level}: {keyword}")
                        break
        
        # AI-powered sentiment analysis
        sentiment_score = 0
        if self.sentiment_analyzer and relevant_sentences:
            try:
                combined_text = ' '.join(relevant_sentences[:3])[:500]
                sentiment_result = self.sentiment_analyzer(combined_text)
                
                if sentiment_result[0]['label'] == 'POSITIVE':
                    sentiment_score = sentiment_result[0]['score'] * 40
                elif sentiment_result[0]['label'] == 'NEGATIVE':
                    sentiment_score = -sentiment_result[0]['score'] * 40
                    
            except Exception as e:
                logger.warning(f"AI sentiment analysis failed: {e}")
                # Fallback to TextBlob if available
                if TEXTBLOB_AVAILABLE:
                    try:
                        blob = TextBlob(' '.join(relevant_sentences[:2]))
                        sentiment_score = blob.sentiment.polarity * 30
                    except:
                        sentiment_score = 0
        
        # Calculate confidence based on evidence quality
        confidence = min(100, len(evidence_snippets) * 15 + len(keyword_matches) * 5)
        if partnership_strength > 0:
            confidence += 10
        
        analysis.update({
            'partnership_strength': max(0, min(100, partnership_strength)),
            'sentiment_score': max(-50, min(50, sentiment_score)),
            'partnership_type': partnership_type,
            'confidence': confidence,
            'evidence_snippets': evidence_snippets,
            'keyword_matches': keyword_matches
        })
        
        return analysis

    def search_partnerships_comprehensive(self, company_a, company_b):
        """Comprehensive partnership search across multiple sources and strategies"""
        logger.info(f"🔍 Comprehensive search for '{company_a}' ↔ '{company_b}' partnerships...")
        
        all_evidence = []
        
        # Get company information
        info_a = self.get_company_info(company_a)
        info_b = self.get_company_info(company_b)
        
        # 1. Official website searches
        logger.info("🏢 Searching official websites...")
        website_evidence = self._search_official_websites(company_a, company_b, info_a, info_b)
        all_evidence.extend(website_evidence)
        
        # 2. News and press searches
        logger.info("📰 Searching news and press releases...")
        news_evidence = self._search_news_and_press(company_a, company_b)
        all_evidence.extend(news_evidence)
        
        # 3. Social media searches
        logger.info("📱 Searching social media...")
        social_evidence = self._search_social_media(company_a, company_b, info_a, info_b)
        all_evidence.extend(social_evidence)
        
        # 4. Industry database searches
        logger.info("📊 Searching industry databases...")
        database_evidence = self._search_industry_databases(company_a, company_b)
        all_evidence.extend(database_evidence)
        
        # 5. General partnership searches
        logger.info("🌐 General partnership searches...")
        general_evidence = self._search_general_partnerships(company_a, company_b)
        all_evidence.extend(general_evidence)
        
        logger.info(f"✅ Found {len(all_evidence)} pieces of evidence")
        return all_evidence

    def _search_official_websites(self, company_a, company_b, info_a, info_b):
        """Search official company websites"""
        evidence = []
        
        # Search Company A's domains for Company B
        for domain in info_a['domains'][:2]:
            queries = [
                f'site:{domain} "{company_b}" partner',
                f'site:{domain} "{company_b}" collaboration',
                f'site:{domain} "{company_b}" partnership'
            ]
            
            for query in queries:
                results = self.enhanced_search(query, 2)
                for result in results:
                    analysis = self.extract_and_analyze_content(result['url'], company_a, company_b)
                    if analysis and analysis['partnership_strength'] > 0:
                        analysis['evidence_type'] = f'official_website_{company_a.lower().replace(" ", "_")}'
                        analysis['credibility_multiplier'] = 1.8  # High credibility for official sites
                        evidence.append(analysis)
        
        # Search Company B's domains for Company A
        for domain in info_b['domains'][:2]:
            queries = [
                f'site:{domain} "{company_a}" partner',
                f'site:{domain} "{company_a}" collaboration',
                f'site:{domain} "{company_a}" partnership'
            ]
            
            for query in queries:
                results = self.enhanced_search(query, 2)
                for result in results:
                    analysis = self.extract_and_analyze_content(result['url'], company_a, company_b)
                    if analysis and analysis['partnership_strength'] > 0:
                        analysis['evidence_type'] = f'official_website_{company_b.lower().replace(" ", "_")}'
                        analysis['credibility_multiplier'] = 1.8
                        evidence.append(analysis)
        
        return evidence

    def _search_news_and_press(self, company_a, company_b):
        """Search news articles and press releases"""
        evidence = []
        
        news_queries = [
            f'"{company_a}" AND "{company_b}" partnership news',
            f'"{company_a}" AND "{company_b}" collaboration announcement',
            f'"{company_a}" partners with "{company_b}" press release',
            f'"{company_b}" partners with "{company_a}" news',
            f'"{company_a}" "{company_b}" joint venture',
            f'"{company_a}" "{company_b}" strategic alliance'
        ]
        
        news_domains = ['news', 'press', 'reuters', 'bloomberg', 'techcrunch', 'venturebeat', 'businesswire', 'prnewswire']
        
        for query in news_queries:
            results = self.enhanced_search(query, 3)
            for result in results:
                # Prioritize news domains
                is_news_domain = any(news_domain in result['domain'].lower() for news_domain in news_domains)
                
                analysis = self.extract_and_analyze_content(result['url'], company_a, company_b)
                if analysis and analysis['partnership_strength'] > 0:
                    analysis['evidence_type'] = 'news_media'
                    analysis['credibility_multiplier'] = 1.5 if is_news_domain else 1.2
                    evidence.append(analysis)
        
        return evidence

    def _search_social_media(self, company_a, company_b, info_a, info_b):
        """Search social media platforms"""
        evidence = []
        
        # Check specific social profiles
        all_profiles = {**info_a['social_profiles'], **info_b['social_profiles']}
        
        for platform, profile_url in all_profiles.items():
            if profile_url:
                analysis = self.extract_and_analyze_content(profile_url, company_a, company_b)
                if analysis and analysis['partnership_strength'] > 0:
                    analysis['evidence_type'] = f'social_media_{platform}'
                    analysis['credibility_multiplier'] = 0.9 if platform == 'linkedin' else 0.7
                    evidence.append(analysis)
        
        # General social media searches
        social_queries = [
            f'site:linkedin.com/company "{company_a}" "{company_b}" partner',
            f'site:linkedin.com "{company_a}" "{company_b}" collaboration',
            f'site:twitter.com "{company_a}" "{company_b}" partnership',
            f'site:facebook.com "{company_a}" "{company_b}" alliance'
        ]
        
        for query in social_queries:
            results = self.enhanced_search(query, 2)
            for result in results:
                analysis = self.extract_and_analyze_content(result['url'], company_a, company_b)
                if analysis and analysis['partnership_strength'] > 0:
                    analysis['evidence_type'] = 'social_media_general'
                    analysis['credibility_multiplier'] = 0.8
                    evidence.append(analysis)
        
        return evidence

    def _search_industry_databases(self, company_a, company_b):
        """Search industry databases and platforms"""
        evidence = []
        
        database_queries = [
            f'site:crunchbase.com "{company_a}" "{company_b}"',
            f'site:angel.co "{company_a}" "{company_b}" partner',
            f'site:github.com "{company_a}" "{company_b}" collaboration',
            f'site:producthunt.com "{company_a}" "{company_b}"',
            f'site:f6s.com "{company_a}" "{company_b}" partnership'
        ]
        
        for query in database_queries:
            results = self.enhanced_search(query, 2)
            for result in results:
                analysis = self.extract_and_analyze_content(result['url'], company_a, company_b)
                if analysis and analysis['partnership_strength'] > 0:
                    analysis['evidence_type'] = 'industry_database'
                    analysis['credibility_multiplier'] = 1.3
                    evidence.append(analysis)
        
        return evidence

    def _search_general_partnerships(self, company_a, company_b):
        """General partnership searches"""
        evidence = []
        
        general_queries = [
            f'"{company_a}" "{company_b}" partnership',
            f'"{company_a}" "{company_b}" collaboration',
            f'"{company_a}" works with "{company_b}"',
            f'"{company_a}" "{company_b}" joint project',
            f'"{company_a}" "{company_b}" strategic relationship'
        ]
        
        for query in general_queries:
            results = self.enhanced_search(query, 2)
            for result in results:
                analysis = self.extract_and_analyze_content(result['url'], company_a, company_b)
                if analysis and analysis['partnership_strength'] > 0:
                    analysis['evidence_type'] = 'general_search'
                    analysis['credibility_multiplier'] = 1.0
                    evidence.append(analysis)
        
        return evidence

    def calculate_trust_score(self, all_evidence):
        """Calculate comprehensive trust score with advanced analytics"""
        if not all_evidence:
            return {
                'trust_score': 0,
                'confidence_level': 'No Data',
                'verdict': '❓ No Evidence Found',
                'partnership_likelihood': 'Unknown',
                'evidence_summary': {},
                'recommendations': [
                    'No evidence found in public sources',
                    'Companies may have private partnerships',
                    'Consider direct inquiry with companies',
                    'Check for recent announcements'
                ]
            }
        
        # Organize evidence by type
        evidence_by_type = defaultdict(list)
        total_weighted_score = 0
        total_confidence_weight = 0
        positive_evidence = 0
        negative_evidence = 0
        
        for evidence in all_evidence:
            evidence_type = evidence.get('evidence_type', 'unknown')
            partnership_strength = evidence.get('partnership_strength', 0)
            credibility_multiplier = evidence.get('credibility_multiplier', 1.0)
            sentiment_score = evidence.get('sentiment_score', 0)
            confidence = evidence.get('confidence', 0)
            
            # Calculate weighted contribution
            base_score = partnership_strength * credibility_multiplier
            confidence_weight = confidence / 100
            
            total_weighted_score += base_score * confidence_weight
            total_confidence_weight += confidence_weight
            
            # Count evidence types
            if partnership_strength > 0:
                positive_evidence += 1
            if sentiment_score < -15:
                negative_evidence += 1
            
            # Group by evidence type
            evidence_by_type[evidence_type].append({
                'score': partnership_strength,
                'sentiment': sentiment_score,
                'confidence': confidence,
                'source': evidence.get('source_url', 'Unknown'),
                'snippets': evidence.get('evidence_snippets', [])[:3],  # Top 3 snippets
                'keywords': evidence.get('keyword_matches', [])[:5]     # Top 5 keywords
            })
        
        # Calculate base trust score
        if total_confidence_weight > 0:
            base_score = total_weighted_score / total_confidence_weight
        else:
            base_score = 0
        
        # Apply modifiers
        # Bonus for multiple evidence types
        if len(evidence_by_type) >= 3:
            base_score *= 1.15
        elif len(evidence_by_type) >= 2:
            base_score *= 1.05
        
        # Bonus for multiple positive sources
        if positive_evidence >= 3:
            base_score *= 1.1
        
        # Penalty for negative evidence
        if negative_evidence > positive_evidence:
            base_score *= 0.6
        elif negative_evidence > 0:
            base_score *= 0.8
        
        # Final trust score (0-100)
        trust_score = max(0, min(100, base_score))
        
        # Determine confidence level and verdict
        if trust_score >= 85:
            confidence_level = 'Very High'
            verdict = '🎯 Excellent Partnership Evidence'
            partnership_likelihood = 'Very Strong'
        elif trust_score >= 70:
            confidence_level = 'High'
            verdict = '✅ Strong Partnership Evidence'
            partnership_likelihood = 'Strong'
        elif trust_score >= 50:
            confidence_level = 'Good'
            verdict = '👍 Good Partnership Evidence'
            partnership_likelihood = 'Likely'
        elif trust_score >= 30:
            confidence_level = 'Moderate'
            verdict = '🤔 Moderate Partnership Evidence'
            partnership_likelihood = 'Possible'
        elif trust_score >= 15:
            confidence_level = 'Low'
            verdict = '⚠️ Weak Partnership Evidence'
            partnership_likelihood = 'Unlikely'
        else:
            confidence_level = 'Very Low'
            verdict = '❌ Insufficient Partnership Evidence'
            partnership_likelihood = 'Very Unlikely'
        
        # Generate intelligent recommendations
        recommendations = []
        
        if trust_score >= 70:
            recommendations.extend([
                'Strong evidence suggests active partnership',
                'Consider this a reliable business relationship',
                'Look for specific partnership details in sources'
            ])
        elif trust_score >= 30:
            recommendations.extend([
                'Moderate evidence found - verify through direct contact',
                'Check for recent partnership announcements',
                'Look for case studies or joint projects'
            ])
        else:
            recommendations.extend([
                'Limited evidence found in public sources',
                'Partnership may be private or informal',
                'Contact companies directly for verification',
                'Check industry reports and trade publications'
            ])
        
        if negative_evidence > 0:
            recommendations.append('⚠️ Some negative indicators found - investigate further')
        
        if len(evidence_by_type) < 2:
            recommendations.append('Limited source diversity - seek additional verification')
        
        return {
            'trust_score': round(trust_score, 1),
            'confidence_level': confidence_level,
            'verdict': verdict,
            'partnership_likelihood': partnership_likelihood,
            'positive_evidence_count': positive_evidence,
            'negative_evidence_count': negative_evidence,
            'evidence_types_found': len(evidence_by_type),
            'total_sources_checked': len(all_evidence),
            'evidence_summary': dict(evidence_by_type),
            'recommendations': recommendations
        }

    def verify_partnership(self, company_a, company_b):
        """Main verification method - comprehensive partnership analysis"""
        print(f"\n🔍 Starting comprehensive verification: '{company_a}' ↔ '{company_b}'")
        print("=" * 70)
        
        start_time = datetime.now()
        
        # Test API connection first
        api_status, api_message = self.test_api_connection()
        if not api_status:
            print(f"❌ API Connection Failed: {api_message}")
            print("\n💡 Quick Fix:")
            print("1. Get free API key from https://serpapi.com/")
            print("2. Replace 'your_serpapi_key_here' with your actual key")
            print("3. Install SerpAPI: pip install google-search-results")
            return {
                'error': 'API_CONNECTION_FAILED',
                'message': api_message,
                'trust_score': 0,
                'verdict': '❌ Cannot verify - API issue'
            }
        
        print(f"✅ API Connection: {api_message}")
        
        try:
            # Comprehensive search
            all_evidence = self.search_partnerships_comprehensive(company_a, company_b)
            
            # Calculate trust score
            result = self.calculate_trust_score(all_evidence)
            
            # Add metadata
            result.update({
                'companies_verified': [company_a, company_b],
                'verification_timestamp': datetime.now().isoformat(),
                'processing_time_seconds': round((datetime.now() - start_time).total_seconds(), 2),
                'api_status': 'Connected',
                'ai_models_used': 'Advanced' if TRANSFORMERS_AVAILABLE else 'Fallback'
            })
            
            print(f"\n⚡ Analysis completed in {result['processing_time_seconds']} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {
                'error': 'VERIFICATION_FAILED',
                'message': str(e),
                'trust_score': 0,
                'verdict': '❌ Verification failed',
                'companies_verified': [company_a, company_b],
                'processing_time_seconds': (datetime.now() - start_time).total_seconds()
            }

def display_results(result):
    """Display results in a beautiful, easy-to-read format"""
    print("\n" + "=" * 80)
    print("🎯 PARTNERSHIP VERIFICATION RESULTS")
    print("=" * 80)
    
    if 'error' in result:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")
        return
    
    companies = result.get('companies_verified', ['Company A', 'Company B'])
    print(f"🏢 Companies: {companies[0]} ↔ {companies[1]}")
    print(f"🎯 Trust Score: {result.get('trust_score', 0)}/100")
    print(f"📊 Confidence Level: {result.get('confidence_level', 'Unknown')}")
    print(f"🎭 Partnership Likelihood: {result.get('partnership_likelihood', 'Unknown')}")
    print(f"✅ Positive Evidence: {result.get('positive_evidence_count', 0)} sources")
    print(f"❌ Negative Evidence: {result.get('negative_evidence_count', 0)} sources")
    print(f"📁 Evidence Types: {result.get('evidence_types_found', 0)}")
    print(f"🔍 Total Sources: {result.get('total_sources_checked', 0)}")
    print(f"⏱️ Processing Time: {result.get('processing_time_seconds', 0)} seconds")
    print(f"🤖 AI Models: {result.get('ai_models_used', 'Unknown')}")
    
    print(f"\n{result.get('verdict', 'No verdict available')}")
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. {rec}")
    
    # Evidence summary
    evidence_summary = result.get('evidence_summary', {})
    if evidence_summary:
        print(f"\n📋 Evidence Summary:")
        for evidence_type, evidence_list in evidence_summary.items():
            print(f"\n  📌 {evidence_type.replace('_', ' ').title()} ({len(evidence_list)} sources):")
            for evidence in evidence_list[:2]:  # Show top 2 per type
                score = evidence.get('score', 0)
                confidence = evidence.get('confidence', 0)
                print(f"     • Score: {score}, Confidence: {confidence}%")
                
                # Show evidence snippets
                snippets = evidence.get('snippets', [])
                for snippet in snippets[:1]:  # Show 1 snippet per evidence
                    # Clean up snippet display
                    clean_snippet = snippet.replace('🟢 STRONG:', '').replace('🟡 MEDIUM:', '').replace('🔵 WEAK:', '').replace('🚫 NEGATIVE:', '').strip()
                    if len(clean_snippet) > 100:
                        clean_snippet = clean_snippet[:100] + "..."
                    print(f"       💬 {clean_snippet}")

def quick_test():
    """Quick test function to verify everything works"""
    print("🧪 Quick System Test")
    print("=" * 50)
    
    # Test with a simple example
    verifier = EnhancedPartnershipVerifier()
    
    # Test API connection
    api_status, api_message = verifier.test_api_connection()
    print(f"API Status: {'✅' if api_status else '❌'} {api_message}")
    
    if not api_status:
        print("\n🔧 Setup Required:")
        print("1. Get API key from https://serpapi.com/")
        print("2. Set your API key in the SERPAPI_KEY variable above")
        return False
    
    print("✅ System ready for partnership verification!")
    return True

# Example usage function
def verify_partnership_example():
    """Example of how to use the verification system"""
    
    # Initialize the verifier
    verifier = EnhancedPartnershipVerifier()
    
    # Get company names from user
    print("🔍 Enhanced Partnership Verification System V4")
    print("=" * 60)
    
    company_a = input("Enter Company A name: ").strip()
    if not company_a:
        company_a = "Microsoft"
        print(f"Using default: {company_a}")
    
    company_b = input("Enter Company B name: ").strip()
    if not company_b:
        company_b = "OpenAI"
        print(f"Using default: {company_b}")
    
    # Verify partnership
    result = verifier.verify_partnership(company_a, company_b)
    
    # Display results
    display_results(result)
    
    return result

# Main execution
if __name__ == "__main__":
    print("🚀 Enhanced Partnership Verification System V4 - Notebook Ready!")
    print("=" * 70)
    print()
    print("📋 Available Functions:")
    print("  • quick_test() - Test system setup")
    print("  • verify_partnership_example() - Interactive verification")
    print("  • EnhancedPartnershipVerifier() - Create verifier instance")
    print()
    print("⚠️  Remember to set your SERPAPI_KEY above!")
    print()
    
    # Run quick test
    quick_test()