#!/usr/bin/env python3
"""
Simple script to run the certificate scraper and generate datasets
"""

import asyncio
from edtech_certificate_scraper import CertificateDataCollector

async def main():
    """Run the scraper with sample URLs and generate datasets"""
    
    # Sample verification URLs - replace with real ones
    verification_urls = [
        # Coursera verification URLs (examples - replace with real ones)
        "https://www.coursera.org/account/accomplishments/verify/M24E66P6Z4W7",
        "https://www.coursera.org/account/accomplishments/verify/7MN3QS7F7YFF",
        
        # Add more real verification URLs here
        # "https://www.linkedin.com/learning/certificates/your-certificate-id",
        # "https://nptel.ac.in/certificate/verify/your-cert-id",
        # "https://www.credly.com/badges/your-badge-id",
    ]
    
    print("🚀 Starting EdTech Certificate Data Collection...")
    print(f"📋 Processing {len(verification_urls)} URLs")
    
    # Initialize collector
    collector = CertificateDataCollector()
    
    # Collect data
    results = await collector.collect_from_urls(verification_urls)
    
    if results:
        print(f"\n✅ Successfully collected {len(results)} certificate records!")
        
        # Generate datasets
        print("\n📊 Generating datasets...")
        
        # Export to JSON
        collector.export_to_json("certificates_dataset.json")
        print("✓ JSON dataset saved: certificates_dataset.json")
        
        # Export to CSV  
        collector.export_to_csv("certificates_dataset.csv")
        print("✓ CSV dataset saved: certificates_dataset.csv")
        
        # Show statistics
        stats = collector.get_statistics()
        print(f"\n📈 Dataset Statistics:")
        print(f"   Total Records: {stats['total_records']}")
        print(f"   Platforms: {list(stats['platforms'].keys())}")
        print(f"   Organizations: {len(stats.get('organizations', {}))}")
        
        # Show sample record
        if results:
            print(f"\n📋 Sample Record:")
            sample = results[0]
            print(f"   Name: {sample.learner_name}")
            print(f"   Certificate: {sample.certificate_title}")
            print(f"   Organization: {sample.organization_name}")
            print(f"   Platform: {sample.platform}")
            print(f"   Date: {sample.date_issued}")
    else:
        print("\n❌ No certificate data was collected")
        print("💡 Tips:")
        print("   - Ensure URLs are publicly accessible")
        print("   - Check if URLs are valid verification links")
        print("   - Some platforms may block automated requests")

if __name__ == "__main__":
    # Install required packages first:
    # pip install aiohttp beautifulsoup4 lxml
    
    asyncio.run(main())