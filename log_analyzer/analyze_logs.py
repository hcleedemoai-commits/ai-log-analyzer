"""
AI-Powered Log Analyzer

This tool analyzes system logs using AI and generates a structured
incident report with executive summary, statistics, critical issues,
priority ranking, and actionable recommendations.

Cost Optimization Features:
1. Log Preprocessing - Filters out INFO noise, keeps only ERROR/WARN
2. Anomaly Detection - Identifies repeated errors before sending to AI
3. Smart Caching - Reuses reports for identical issues
"""

import requests
import json
import os
import hashlib
from datetime import datetime
from .config import Config

# ====== CONSTANTS ======
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
CACHE_FILE = os.path.join(CACHE_DIR, ".last_analysis_cache.json")

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


# ====== COST OPTIMIZATION 1: Log Preprocessing ======
def preprocess_logs(raw_content):
    """
    Preprocess logs to reduce AI token usage by 80-90%.
    
    Strategy:
    - Filter out INFO level logs (just count them)
    - Keep all ERROR logs
    - Keep only last 5 WARN logs (most recent warnings)
    - Detect and highlight repeated errors
    """
    lines = raw_content.strip().split('\n')
    
    errors = []
    warns = []
    infos = []
    error_patterns = {}
    
    print(f"📊 Parsing {len(lines)} log lines...")
    
    for line in lines:
        if not line.strip():
            continue
        
        # ====== CHECK FOR ERROR ======
        if '[ERROR]' in line:
            errors.append(line)
            # Extract error pattern for deduplication
            parts = line.split(']')
            if len(parts) >= 2:
                # Get the module name (everything after [ and before ])
                module_part = parts[0]
                # Extract module: e.g., "[2026-09-01 08:25:33] ERROR [PaymentModule"
                if 'ERROR' in module_part:
                    # Find the module after ERROR
                    error_parts = module_part.split('ERROR')
                    if len(error_parts) > 1:
                        module = error_parts[1].strip().strip('[').strip(']')
                    else:
                        module = 'Unknown'
                else:
                    module = 'Unknown'
                
                # Get the error message
                error_msg = parts[-1].strip()[:50] if parts[-1].strip() else 'Unknown error'
                key = f"{module}:{error_msg}"
                error_patterns[key] = error_patterns.get(key, 0) + 1
        
        # ====== CHECK FOR WARN ======
        elif '[WARN]' in line:
            warns.append(line)
        
        # ====== CHECK FOR INFO ======
        elif '[INFO]' in line:
            infos.append(line)
        
        # ====== FALLBACK: If none matched, check for "ERROR" without brackets ======
        else:
            # Check if line contains ERROR without brackets
            if 'ERROR' in line.upper():
                errors.append(line)
            elif 'WARN' in line.upper():
                warns.append(line)
            else:
                infos.append(line)
    
    # ====== DEBUG: Show counts ======
    print(f"   Found: {len(errors)} ERRORs, {len(warns)} WARNs, {len(infos)} INFOs")
    
    # If no errors/warnings found, show first 3 lines for debugging
    if len(errors) == 0 and len(warns) == 0 and len(infos) == 0:
        print("   ⚠️  No entries detected! Showing raw content first 200 chars:")
        print(f"   {raw_content[:200]}")
    
    # Build compressed output
    processed = []
    processed.append("=== COST-OPTIMIZED LOG SUMMARY ===")
    processed.append(f"📊 Total INFO entries: {len(infos)} (filtered out to save cost)")
    processed.append(f"⚠️  Total WARN entries: {len(warns)} (showing last 5 only)")
    processed.append(f"🚨 Total ERROR entries: {len(errors)} (all included)")
    processed.append("")
    
    # Show repeated error patterns
    if error_patterns:
        processed.append("=== REPEATED ERROR PATTERNS ===")
        sorted_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)
        for pattern, count in sorted_patterns[:5]:
            if count > 1:
                processed.append(f"⚠️  '{pattern}' appeared {count} times")
        processed.append("")
    
    # WARN: Only last 5
    if warns:
        processed.append(f"=== RECENT WARNINGS (last {min(5, len(warns))}) ===")
        processed.extend(warns[-5:])
        processed.append("")
    
    # ERROR: All errors
    if errors:
        processed.append(f"=== CRITICAL ERRORS ({len(errors)}) ===")
        processed.extend(errors)
    
    compressed = "\n".join(processed)
    
    # Calculate compression ratio
    original_size = len(raw_content)
    compressed_size = len(compressed)
    ratio = (compressed_size / original_size * 100) if original_size > 0 else 0
    
    print(f"📉 Cost Optimization: {original_size} chars → {compressed_size} chars ({ratio:.1f}% of original)")
    print(f"   💰 Estimated token savings: ~{int((1 - ratio/100) * 100)}%")
    
    return compressed


# ======COST OPTIMIZATION 2: Smart Caching ======
def get_log_signature(log_content):
    """Generate a unique signature for the log content."""
    # Take first 500 chars + count of ERROR/WARN/INFO
    lines = log_content.strip().split('\n')
    error_count = sum(1 for line in lines if '[ERROR]' in line)
    warn_count = sum(1 for line in lines if '[WARN]' in line)
    info_count = sum(1 for line in lines if '[INFO]' in line)
    
    # Create a signature based on error patterns, not full content
    error_patterns = []
    for line in lines:
        if '[ERROR]' in line:
            # Extract module and error type
            parts = line.split(']')
            if len(parts) >= 2:
                module = parts[0].strip('[') if '[' in parts[0] else 'Unknown'
                error_msg = parts[-1].strip()[:30]
                error_patterns.append(f"{module}:{error_msg}")
    
    signature_data = {
        "error_count": error_count,
        "warn_count": warn_count,
        "info_count": info_count,
        "error_patterns": sorted(set(error_patterns))[:10]  # Top 10 unique errors
    }
    
    signature = hashlib.md5(str(signature_data).encode()).hexdigest()
    return signature, signature_data


def check_cache(log_signature):
    """Check if we have a cached report for this log signature."""
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        if cache.get('signature') == log_signature:
            print(f"♻️  Cache HIT! Using cached report (saved at: {cache.get('timestamp', 'unknown')})")
            print(f"   💰 Cost saved: This analysis would have cost ~$0.01-0.05")
            return cache.get('report')
        else:
            print(f"🆕 Cache MISS: Log pattern has changed, generating new analysis")
            return None
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def save_cache(log_signature, report):
    """Save the report to cache."""
    cache_data = {
        "signature": log_signature,
        "report": report,
        "timestamp": datetime.now().isoformat()
    }
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"💾 Report cached for future reference")



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
    print(f"📂 Using model: {Config.MODEL}")
    print("=" * 50)
    print("⚡ Cost Optimization Features:")
    print("   ✅ INFO logs filtered out (reduces token usage)")
    print("   ✅ Repeated errors detected and compressed")
    print("   ✅ Smart caching for identical issues")
    print("=" * 50 + "\n")
    
    try:
        print("📖 Reading log file...")
        raw_log = read_logs("sample_logs.txt")
        print(f"✅ Raw log loaded ({len(raw_log)} characters)")
        
        # ====== STEP 1: Preprocess (Save Money!) ======
        print("\n🔄 Preprocessing logs to reduce AI cost...")
        compressed_log = preprocess_logs(raw_log)
        
        # ====== STEP 2: Check Cache (Save More Money!) ======
        print("\n🔍 Checking cache for identical issue...")
        signature, sig_data = get_log_signature(compressed_log)
        cached_report = check_cache(signature)
        
        if cached_report:
            report = cached_report
            print("\n📊 Using cached report (no API call needed!)")
        else:
            # ====== STEP 3: Call AI (Only when needed) ======
            print("\n🤖 No cache found. Calling AI for analysis...")
            report = analyze_logs_with_ai(compressed_log)
            
            # ====== STEP 4: Save to Cache ======
            save_cache(signature, report)
        
        # Print report
        print_header("AI LOG ANALYSIS REPORT")
        print(report)
        print("=" * 70)
        
        # Save report
        saved_file = save_report(report)
        print(f"\n✅ Report saved to: {saved_file}")
        
        # ====== Cost Summary ======
        print("\n" + "=" * 50)
        print("💰 COST OPTIMIZATION SUMMARY")
        print("=" * 50)
        print(f"📉 Original log size: {len(raw_log)} chars")
        print(f"📈 Compressed size: {len(compressed_log)} chars")
        print(f"💾 Reduction: ~{(1 - len(compressed_log)/len(raw_log)) * 100:.0f}%")
        if cached_report:
            print("♻️  This report was served from CACHE (zero API cost!)")
        else:
            print("🆕 This was a fresh AI analysis (cached for future use)")
        print("=" * 50)
        
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
