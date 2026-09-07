"""
AI-Powered ERP Log Analyzer

This tool analyzes ERP system logs using AI and generates a structured
incident report with executive summary, statistics, critical issues,
priority ranking, and actionable recommendations.
"""

import requests
import json
import os
from datetime import datetime
from .config import Config

# ====== LOGGING HELPER ======
def print_header(text, char="=", length=70):
    """Print a formatted header."""
    print("\n" + char * length)
    print(f"📊 {text}")
    print(char * length)

# ====== READ LOG FILE ======
def read_logs(file_path):
    """Read log file content."""
    if not os.path.exists(file_path):
        # Try the default path
        file_path = Config.DEFAULT_LOG_FILE
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Log file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# ====== CALL OPENROUTER API ======
def analyze_logs_with_ai(log_content):
    """Send logs to AI and get structured analysis."""
    
    # Validate configuration
    Config.validate()
    
    headers = {
        "Authorization": f"Bearer {Config.API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""You are a senior ERP system analyst with 15+ years of experience in production support and system operations.

Analyze the following ERP system logs and produce a structured incident report.

Please output in this exact format:

1. EXECUTIVE SUMMARY: (2-3 sentences summarizing the most critical issues in plain English)
2. LOG STATISTICS: (Count of INFO / WARN / ERROR entries)
3. CRITICAL ISSUES: (List each ERROR with timestamp, module, and whether it appears repeatedly)
4. PRIORITY RANKING: (Which issue should be fixed first, and why)
5. ACTIONABLE RECOMMENDATIONS: (Specific troubleshooting steps for the top-priority issue)

Logs:
{log_content}

Output the report directly. Do not add any introductory text."""

    payload = {
        "model": Config.MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2048
    }
    
    print("📡 Sending request to OpenRouter API...")
    response = requests.post(Config.API_URL, headers=headers, json=payload)
    
    print(f"📡 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ JSON Parse Error: {e}\nRaw response: {response.text[:500]}"
    else:
        return f"❌ API Error: {response.status_code}\nResponse: {response.text}"

# ====== SAVE REPORT ======
def save_report(report):
    """Save the analysis report to a file."""
    # Ensure reports directory exists
    os.makedirs(Config.REPORTS_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_report_{timestamp}.txt"
    filepath = os.path.join(Config.REPORTS_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    
    return filepath

# ====== MAIN PROGRAM ======
def main():
    """Main entry point."""
    print("🔍 AI-Powered ERP Log Analyzer")
    print(f"📂 Using model: {Config.MODEL}\n")
    
    try:
        print("📖 Reading log file...")
        log_data = read_logs("sample_logs.txt")
        print(f"✅ Log file loaded ({len(log_data)} characters)")
        
        print("\n🤖 Analyzing logs with AI...")
        report = analyze_logs_with_ai(log_data)
        
        # Print report
        print_header("AI LOG ANALYSIS REPORT")
        print(report)
        print("=" * 70)
        
        # Save report
        saved_file = save_report(report)
        print(f"\n✅ Report saved to: {saved_file}")
        
        print("\n✨ Analysis complete!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure 'sample_logs.txt' is in the 'sample_logs/' folder")
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Create a .env file with your OPENROUTER_API_KEY")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()