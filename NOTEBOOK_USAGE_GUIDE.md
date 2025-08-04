# 📓 Notebook Usage Guide - Partnership Verification System V4

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Dependencies
```bash
pip install requests beautifulsoup4 google-search-results lxml textblob numpy transformers torch
```

### Step 2: Get API Key
1. Go to https://serpapi.com/
2. Sign up for free account (100 searches/month free)
3. Copy your API key

### Step 3: Configure & Run
```python
# Copy the entire partnership_verifier_notebook.py into a Jupyter cell
# Replace this line:
SERPAPI_KEY = "your_serpapi_key_here"  # ⚠️ REPLACE WITH YOUR ACTUAL KEY

# With your actual key:
SERPAPI_KEY = "your_actual_api_key_from_serpapi"

# Run the cell to initialize the system
```

## 🔍 Using the System

### Method 1: Interactive Mode
```python
# Run this in a new cell after setup
verify_partnership_example()
```

### Method 2: Direct Usage
```python
# Create verifier instance
verifier = EnhancedPartnershipVerifier()

# Verify specific companies
result = verifier.verify_partnership("Microsoft", "OpenAI")

# Display beautiful results
display_results(result)
```

### Method 3: Custom API Key
```python
# If you want to use a different API key
verifier = EnhancedPartnershipVerifier(api_key="your_other_api_key")
result = verifier.verify_partnership("Company A", "Company B")
display_results(result)
```

## 📊 Sample Output

When you run the verification, you'll get output like this:

```
🔍 Starting comprehensive verification: 'Microsoft' ↔ 'OpenAI'
======================================================================
✅ API Connection: API connection successful
2023-XX-XX XX:XX:XX - INFO - 🔍 Discovering information for 'Microsoft'...
2023-XX-XX XX:XX:XX - INFO - ✅ Found 3 domains and 4 social profiles
2023-XX-XX XX:XX:XX - INFO - 🔍 Comprehensive search for 'Microsoft' ↔ 'OpenAI' partnerships...
2023-XX-XX XX:XX:XX - INFO - 🏢 Searching official websites...
2023-XX-XX XX:XX:XX - INFO - 📰 Searching news and press releases...
2023-XX-XX XX:XX:XX - INFO - 📱 Searching social media...
2023-XX-XX XX:XX:XX - INFO - 📊 Searching industry databases...
2023-XX-XX XX:XX:XX - INFO - 🌐 General partnership searches...
2023-XX-XX XX:XX:XX - INFO - ✅ Found 6 pieces of evidence

⚡ Analysis completed in 45.2 seconds

================================================================================
🎯 PARTNERSHIP VERIFICATION RESULTS
================================================================================
🏢 Companies: Microsoft ↔ OpenAI
🎯 Trust Score: 87.3/100
📊 Confidence Level: Very High
🎭 Partnership Likelihood: Very Strong
✅ Positive Evidence: 6 sources
❌ Negative Evidence: 0 sources
📁 Evidence Types: 4
🔍 Total Sources: 6
⏱️ Processing Time: 45.2 seconds
🤖 AI Models: Advanced

🎯 Excellent Partnership Evidence

💡 Recommendations:
   1. Strong evidence suggests active partnership
   2. Consider this a reliable business relationship
   3. Look for specific partnership details in sources

📋 Evidence Summary:

  📌 Official Website Microsoft (2 sources):
     • Score: 95, Confidence: 85%
       💬 Microsoft announces strategic partnership with OpenAI for AI development

  📌 News Media (3 sources):
     • Score: 88, Confidence: 80%
       💬 Microsoft invests $10 billion in OpenAI partnership to advance AI
```

## 🛠️ Troubleshooting

### Problem: "API Connection Failed"
**Solution:**
```python
# Check your API key
verifier = EnhancedPartnershipVerifier()
api_status, message = verifier.test_api_connection()
print(f"Status: {api_status}, Message: {message}")

# If failed, check:
# 1. API key is correct (no extra spaces)
# 2. You have remaining API credits
# 3. SerpAPI library is installed: pip install google-search-results
```

### Problem: "Trust Score Always 0"
**Possible causes & solutions:**
1. **API key issue** - Verify with `quick_test()`
2. **Companies not found** - Try well-known companies first (Microsoft, Google, Apple)
3. **No public partnerships** - Some partnerships are private
4. **Network issues** - Check internet connection

### Problem: "AI models not loading"
**Solution:**
```python
# Install transformers if you want AI features
# pip install transformers torch

# Or use without AI (fallback mode works fine)
# The system will automatically use TextBlob for sentiment analysis
```

## 💡 Pro Tips

### 1. Test with Known Partnerships First
```python
# Try these known partnerships to verify system works:
result = verifier.verify_partnership("Microsoft", "OpenAI")
result = verifier.verify_partnership("Google", "YouTube")
result = verifier.verify_partnership("Facebook", "Instagram")
```

### 2. Small Company Optimization
```python
# For small companies, the system searches:
# - LinkedIn company pages
# - GitHub repositories
# - Crunchbase profiles
# - Angel.co listings
# - Industry databases

# Example with smaller companies:
result = verifier.verify_partnership("Stripe", "Shopify")
```

### 3. Batch Processing
```python
# Verify multiple partnerships
companies_to_check = [
    ("Microsoft", "OpenAI"),
    ("Google", "DeepMind"),
    ("Amazon", "Alexa"),
]

results = []
for company_a, company_b in companies_to_check:
    result = verifier.verify_partnership(company_a, company_b)
    results.append(result)
    display_results(result)
    time.sleep(2)  # Rate limiting
```

### 4. Save Results
```python
import json

# Save detailed results
result = verifier.verify_partnership("Company A", "Company B")
with open('partnership_results.json', 'w') as f:
    json.dump(result, f, indent=2)

# Load and display later
with open('partnership_results.json', 'r') as f:
    saved_result = json.load(f)
display_results(saved_result)
```

## 🎯 Trust Score Guide

| Score | Meaning | Action |
|-------|---------|---------|
| 85-100 | Excellent Evidence | High confidence partnership |
| 70-84 | Strong Evidence | Likely active partnership |
| 50-69 | Good Evidence | Probable partnership |
| 30-49 | Moderate Evidence | Possible partnership, verify |
| 15-29 | Weak Evidence | Unlikely, needs investigation |
| 0-14 | Insufficient Evidence | No clear partnership found |

## ⚡ Quick Commands

```python
# Quick test
quick_test()

# Interactive mode
verify_partnership_example()

# Direct verification
result = verifier.verify_partnership("Company A", "Company B")
display_results(result)

# Check specific aspects
print(f"Trust Score: {result['trust_score']}")
print(f"Evidence Count: {result['positive_evidence_count']}")
print(f"Partnership Likelihood: {result['partnership_likelihood']}")
```

## 🔧 Advanced Configuration

```python
# Custom verifier with settings
verifier = EnhancedPartnershipVerifier(api_key="your_key")

# Modify search keywords for specific industries
verifier.partnership_keywords['fintech'] = [
    'payment partner', 'financial partnership', 'banking alliance'
]

# Add industry-specific sources
verifier.search_sources['fintech'] = [
    'finextra.com', 'americanbanker.com', 'paymentssource.com'
]
```

Ready to verify partnerships with confidence! 🚀