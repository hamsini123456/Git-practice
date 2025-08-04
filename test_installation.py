#!/usr/bin/env python3
"""
Test script for Enhanced Partnership Verification System V4
Verifies that all dependencies are properly installed and basic functionality works.
"""

import sys
import traceback

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        ('requests', 'requests'),
        ('BeautifulSoup', 'bs4'),
        ('GoogleSearch', 'serpapi'),
        ('json', 'json'),
        ('re', 're'),
        ('urlparse', 'urllib.parse'),
        ('datetime', 'datetime'),
        ('logging', 'logging'),
        ('TextBlob', 'textblob'),
        ('numpy', 'numpy'),
        ('defaultdict', 'collections')
    ]
    
    failed_imports = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name} - OK")
        except ImportError as e:
            print(f"  ❌ {package_name} - FAILED: {e}")
            failed_imports.append(package_name)
    
    # Test optional AI packages
    print("\n🤖 Testing AI/ML packages (optional)...")
    
    ai_packages = [
        ('transformers', 'transformers'),
        ('torch', 'torch'),
        ('tokenizers', 'tokenizers')
    ]
    
    ai_available = True
    for package_name, import_name in ai_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name} - OK")
        except ImportError:
            print(f"  ⚠️  {package_name} - Not available (will use fallback methods)")
            ai_available = False
    
    return len(failed_imports) == 0, ai_available

def test_basic_functionality():
    """Test basic functionality without making API calls"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from enhanced_partnership_verifier import EnhancedPartnershipVerifier
        print("  ✅ Enhanced Partnership Verifier import - OK")
        
        # Initialize verifier
        verifier = EnhancedPartnershipVerifier()
        print("  ✅ Verifier initialization - OK")
        
        # Test text analysis without AI models
        test_text = "Microsoft and OpenAI have announced a strategic partnership to develop AI technologies."
        analysis = verifier.analyze_text_sentiment_and_partnership(test_text, "Microsoft", "OpenAI")
        
        if analysis['partnership_strength'] > 0:
            print("  ✅ Text analysis - OK")
            print(f"     Partnership strength: {analysis['partnership_strength']}")
            print(f"     Partnership type: {analysis['partnership_type']}")
        else:
            print("  ⚠️  Text analysis - Weak results (may be normal)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_serpapi_key():
    """Test if SerpAPI key is configured (without making actual calls)"""
    print("\n🔑 Testing SerpAPI configuration...")
    
    try:
        from enhanced_partnership_verifier import SERPAPI_KEY
        
        if SERPAPI_KEY and SERPAPI_KEY != "YOUR_SERPAPI_KEY_HERE":
            if len(SERPAPI_KEY) > 30:  # SerpAPI keys are typically long
                print("  ✅ SerpAPI key appears to be configured")
                return True
            else:
                print("  ⚠️  SerpAPI key seems too short - please verify")
                return False
        else:
            print("  ❌ SerpAPI key not configured")
            print("     Please set your SerpAPI key in the script")
            return False
            
    except Exception as e:
        print(f"  ❌ Error checking SerpAPI key: {e}")
        return False

def test_sample_analysis():
    """Test sample text analysis to verify AI functionality"""
    print("\n📊 Testing sample partnership analysis...")
    
    try:
        from enhanced_partnership_verifier import EnhancedPartnershipVerifier
        
        verifier = EnhancedPartnershipVerifier()
        
        # Sample texts with different partnership strengths
        test_cases = [
            {
                'text': "Apple is the official strategic partner of Google in developing new technologies.",
                'company_a': "Apple",
                'company_b': "Google",
                'expected_strength': "high"
            },
            {
                'text': "Facebook and Twitter sometimes work together on industry standards.",
                'company_a': "Facebook", 
                'company_b': "Twitter",
                'expected_strength': "medium"
            },
            {
                'text': "Microsoft had a dispute with Oracle and ended their partnership last year.",
                'company_a': "Microsoft",
                'company_b': "Oracle", 
                'expected_strength': "negative"
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n  Test Case {i}: {test_case['expected_strength'].title()} partnership")
            
            analysis = verifier.analyze_text_sentiment_and_partnership(
                test_case['text'], 
                test_case['company_a'], 
                test_case['company_b']
            )
            
            strength = analysis['partnership_strength']
            
            if test_case['expected_strength'] == 'high' and strength >= 30:
                print(f"    ✅ Detected strong partnership (score: {strength})")
            elif test_case['expected_strength'] == 'medium' and 10 <= strength < 30:
                print(f"    ✅ Detected medium partnership (score: {strength})")
            elif test_case['expected_strength'] == 'negative' and strength == 0:
                print(f"    ✅ Correctly detected negative/no partnership (score: {strength})")
            else:
                print(f"    ⚠️  Unexpected result for {test_case['expected_strength']} partnership (score: {strength})")
                all_passed = False
            
            if analysis['evidence_snippets']:
                print(f"    💬 Evidence: {analysis['evidence_snippets'][0]}")
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Sample analysis failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Partnership Verification System V4 - Installation Test")
    print("=" * 70)
    
    # Run tests
    imports_ok, ai_available = test_imports()
    basic_ok = test_basic_functionality()
    serpapi_ok = test_serpapi_key()
    analysis_ok = test_sample_analysis()
    
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    print(f"Required Imports: {'✅ PASSED' if imports_ok else '❌ FAILED'}")
    print(f"Basic Functionality: {'✅ PASSED' if basic_ok else '❌ FAILED'}")
    print(f"SerpAPI Configuration: {'✅ PASSED' if serpapi_ok else '⚠️ NEEDS SETUP'}")
    print(f"AI/ML Models: {'✅ AVAILABLE' if ai_available else '⚠️ FALLBACK MODE'}")
    print(f"Sample Analysis: {'✅ PASSED' if analysis_ok else '⚠️ CHECK RESULTS'}")
    
    overall_status = imports_ok and basic_ok
    
    print(f"\nOverall Status: {'🎉 READY TO USE' if overall_status else '🔧 NEEDS ATTENTION'}")
    
    if not serpapi_ok:
        print("\n⚠️ To use the full system, please:")
        print("   1. Get a SerpAPI key from https://serpapi.com/")
        print("   2. Replace SERPAPI_KEY in enhanced_partnership_verifier.py")
    
    if not ai_available:
        print("\n💡 AI models not available - system will use fallback methods")
        print("   For better accuracy, ensure transformers and torch are installed")
    
    if overall_status and serpapi_ok:
        print("\n🚀 System is ready! You can now run:")
        print("   python enhanced_partnership_verifier.py")
    
    return overall_status

if __name__ == "__main__":
    main()