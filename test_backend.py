#!/usr/bin/env python3
"""
Backend test script to diagnose issues
Run this to check if your backend is configured correctly
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("🔍 BACKEND DIAGNOSTICS")
print("=" * 60)

# 1. Check if we're in the right directory
print("\n1. Checking directory structure...")
current_dir = Path.cwd()
print(f"   Current directory: {current_dir}")

backend_dir = current_dir / "backend"
if backend_dir.exists():
    print("   ✅ backend/ directory found")
else:
    print("   ❌ backend/ directory NOT found")
    print("   💡 Make sure you're in the project root directory")

# 2. Check if .env file exists
print("\n2. Checking .env file...")
env_file = current_dir / ".env"
if env_file.exists():
    print("   ✅ .env file found")
    
    # Read and check contents
    with open(env_file) as f:
        content = f.read()
        
    if "FREE_LLM_API_URL" in content:
        print("   ✅ FREE_LLM_API_URL is set")
        
        # Check if it's the correct URL
        for line in content.split('\n'):
            if line.startswith('FREE_LLM_API_URL'):
                url = line.split('=')[1].strip()
                print(f"      Value: {url}")
                
                if "api.groq.com" in url:
                    print("      ✅ Using Groq API (correct)")
                elif "console.groq.com" in url:
                    print("      ❌ WRONG URL - this is the console, not the API!")
                    print("      💡 Change to: https://api.groq.com/openai/v1/chat/completions")
    else:
        print("   ❌ FREE_LLM_API_URL not found in .env")
    
    if "FREE_LLM_API_KEY" in content:
        print("   ✅ FREE_LLM_API_KEY is set")
        
        # Check if it looks like a key
        for line in content.split('\n'):
            if line.startswith('FREE_LLM_API_KEY'):
                key = line.split('=')[1].strip()
                if key.startswith('gsk_'):
                    print(f"      ✅ Key format looks correct (gsk_...)")
                else:
                    print(f"      ⚠️  Key doesn't start with 'gsk_' - is this correct?")
    else:
        print("   ❌ FREE_LLM_API_KEY not found in .env")
else:
    print("   ❌ .env file NOT found")
    print("   💡 Create a .env file in the project root")

# 3. Check if CSV file exists
print("\n3. Checking test data...")
csv_path = current_dir / "data" / "test_leads_30.csv"
if csv_path.exists():
    print(f"   ✅ CSV file found: {csv_path}")
    
    # Count lines
    with open(csv_path) as f:
        lines = f.readlines()
    print(f"      Rows: {len(lines) - 1} leads (excluding header)")
else:
    print(f"   ❌ CSV file NOT found: {csv_path}")
    print("   💡 Make sure the data/ directory exists with test_leads_30.csv")

# 4. Check Python dependencies
print("\n4. Checking Python dependencies...")
required_packages = [
    "fastapi",
    "uvicorn",
    "pandas",
    "requests",
    "python-dotenv",
    "jinja2"
]

for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} NOT installed")
        print(f"      💡 Run: pip install {package}")

# 5. Check if backend modules can be imported
print("\n5. Checking backend modules...")
sys.path.insert(0, str(current_dir))

try:
    from backend import app
    print("   ✅ backend.app can be imported")
except Exception as e:
    print(f"   ❌ backend.app import failed: {e}")

try:
    from backend import scoring
    print("   ✅ backend.scoring can be imported")
except Exception as e:
    print(f"   ❌ backend.scoring import failed: {e}")

try:
    from backend import llm_client
    print("   ✅ backend.llm_client can be imported")
except Exception as e:
    print(f"   ❌ backend.llm_client import failed: {e}")

try:
    from backend import constants
    print("   ✅ backend.constants can be imported")
except Exception as e:
    print(f"   ❌ backend.constants import failed: {e}")

# 6. Test API connectivity
print("\n6. Testing Groq API connectivity...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    api_url = os.getenv("FREE_LLM_API_URL", "").strip()
    api_key = os.getenv("FREE_LLM_API_KEY", "").strip()
    
    if not api_url or not api_key:
        print("   ⚠️  API credentials not set - skipping test")
    else:
        import requests
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": "Say 'test successful' if you can read this"}
            ],
            "max_tokens": 10
        }
        
        print(f"   Testing API: {api_url}")
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ API is reachable and working!")
            data = response.json()
            if "choices" in data:
                print(f"      Response: {data['choices'][0]['message']['content']}")
        else:
            print(f"   ❌ API returned error: {response.status_code}")
            print(f"      {response.text[:200]}")
            
except Exception as e:
    print(f"   ❌ API test failed: {e}")

# 7. Summary
print("\n" + "=" * 60)
print("📋 SUMMARY")
print("=" * 60)

print("\nTo start the server, run:")
print("  python -m uvicorn backend.app:app --reload --port 8000")
print("\nThen open: http://localhost:8000")
print("\nIf button still doesn't work:")
print("  1. Open browser console (F12) and check for errors")
print("  2. Check terminal logs for backend errors")
print("  3. Try: curl -X POST http://localhost:8000/api/load_and_process")
print("=" * 60)