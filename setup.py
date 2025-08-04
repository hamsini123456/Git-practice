#!/usr/bin/env python3
"""
Setup script for Enhanced Partnership Verification System V4
Automates installation and basic configuration.
"""

import subprocess
import sys
import os
import platform

def print_header():
    """Print setup header"""
    print("🔧 Enhanced Partnership Verification System V4 - Setup")
    print("=" * 60)
    print("This script will help you install and configure the system.")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} - Incompatible")
        print("     Requires Python 3.8 or higher")
        return False

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    try:
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print("  ❌ requirements.txt not found!")
            return False
        
        # Install packages
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ All packages installed successfully")
            return True
        else:
            print(f"  ❌ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error during installation: {e}")
        return False

def download_ai_models():
    """Download and cache AI models"""
    print("\n🤖 Setting up AI models...")
    
    try:
        # Try to import and initialize models
        import transformers
        
        print("  📥 Downloading sentiment analysis model...")
        try:
            transformers.pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            print("  ✅ Sentiment analysis model ready")
        except Exception as e:
            print(f"  ⚠️  Could not download advanced model, will use fallback: {e}")
        
        return True
        
    except ImportError:
        print("  ⚠️  Transformers not available - will use fallback methods")
        return False
    except Exception as e:
        print(f"  ⚠️  Error setting up AI models: {e}")
        return False

def configure_serpapi():
    """Help user configure SerpAPI key"""
    print("\n🔑 SerpAPI Configuration")
    print("-" * 30)
    
    # Check current key
    try:
        with open('enhanced_partnership_verifier.py', 'r') as f:
            content = f.read()
            
        if 'SERPAPI_KEY = "f6def46c9232527e8bf9c37d6acf95e932f8ce13a63145e8c9e7d5d9950f4031"' in content:
            print("⚠️  Default API key detected. You need to configure your own SerpAPI key.")
            print()
            print("📋 To get your SerpAPI key:")
            print("   1. Go to https://serpapi.com/")
            print("   2. Sign up for a free account")
            print("   3. Get your API key from the dashboard")
            print("   4. Replace SERPAPI_KEY in enhanced_partnership_verifier.py")
            print()
            
            configure_now = input("Do you want to configure your API key now? (y/n): ").lower().strip()
            
            if configure_now == 'y':
                api_key = input("Enter your SerpAPI key: ").strip()
                
                if api_key and len(api_key) > 30:
                    try:
                        # Replace the API key in the file
                        new_content = content.replace(
                            'SERPAPI_KEY = "f6def46c9232527e8bf9c37d6acf95e932f8ce13a63145e8c9e7d5d9950f4031"',
                            f'SERPAPI_KEY = "{api_key}"'
                        )
                        
                        with open('enhanced_partnership_verifier.py', 'w') as f:
                            f.write(new_content)
                            
                        print("  ✅ API key configured successfully!")
                        return True
                        
                    except Exception as e:
                        print(f"  ❌ Error configuring API key: {e}")
                        return False
                else:
                    print("  ⚠️  Invalid API key format")
                    return False
            else:
                print("  ⚠️  API key not configured - you'll need to set it manually")
                return False
        else:
            print("  ✅ Custom API key appears to be configured")
            return True
            
    except Exception as e:
        print(f"  ❌ Error checking API key configuration: {e}")
        return False

def run_test():
    """Run the test script to verify installation"""
    print("\n🧪 Running installation test...")
    
    try:
        result = subprocess.run([sys.executable, 'test_installation.py'], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"  ❌ Error running test: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("🚀 To start using the system:")
    print("   python enhanced_partnership_verifier.py")
    print()
    print("🧪 To run tests anytime:")
    print("   python test_installation.py")
    print()
    print("📖 For detailed documentation:")
    print("   Read README.md")
    print()
    print("💡 Tips:")
    print("   - The first run may take longer while AI models download")
    print("   - For better accuracy, ensure you have a valid SerpAPI key")
    print("   - Check your internet connection for best results")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Incompatible Python version")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed: Could not install requirements")
        print("💡 Try running manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Download AI models
    download_ai_models()
    
    # Configure SerpAPI
    serpapi_configured = configure_serpapi()
    
    # Run test
    test_passed = run_test()
    
    # Print results
    print("\n" + "=" * 60)
    print("🏁 SETUP SUMMARY")
    print("=" * 60)
    
    print(f"Python Version: ✅ Compatible")
    print(f"Package Installation: ✅ Complete")
    print(f"AI Models: {'✅ Ready' if 'transformers' in sys.modules else '⚠️ Fallback'}")
    print(f"SerpAPI Configuration: {'✅ Configured' if serpapi_configured else '⚠️ Needs Setup'}")
    print(f"System Test: {'✅ Passed' if test_passed else '⚠️ Check Results'}")
    
    if test_passed and serpapi_configured:
        print(f"\nStatus: 🎉 READY TO USE!")
    elif test_passed:
        print(f"\nStatus: ⚠️ MOSTLY READY (Configure SerpAPI for full functionality)")
    else:
        print(f"\nStatus: 🔧 NEEDS ATTENTION")
    
    print_next_steps()

if __name__ == "__main__":
    main()