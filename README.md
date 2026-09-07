# ai-powered-log-analysis

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-API-orange)](https://openrouter.ai/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Overview

This project is a **Proof-of-Concept (PoC)** that demonstrates how AI can automate ERP system log analysis and incident reporting. 

Instead of engineers spending **2 hours** manually scanning logs, this tool:
- ✅ Reads system logs automatically
- ✅ Analyzes them using AI (via OpenRouter API)
- ✅ Generates a structured incident report in **15 minutes** or less
- ✅ Saves reports for auditing and tracking

## Features

- **Executive Summary** - 2-3 sentences of what's wrong
- **Log Statistics** - INFO / WARN / ERROR counts
- **Critical Issues** - List of all errors with timestamps
- **Priority Ranking** - Which issue to fix first
- **Actionable Recommendations** - Step-by-step troubleshooting guide
- **Auto-Save** - Reports saved with timestamps in `reports/` folder

## Project Structure

```
.
├── .env                     # API configuration (not in git)
├── .gitignore              # Excluded files
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── sample_logs/            # Sample data files
│   └── (your data here)
├── reports/                # Generated outputs
└── ai_powered_log_analysis/
    ├── __init__.py
    ├── config.py           # Configuration
    └── main.py             # Main script
├── tests/                  # Test files
│   └── test_analyzer.py
```

## Quick Start

### 1. Navigate to project
```bash
cd ai-powered-log-analysis
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API key
Create a `.env` file with:
```env
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct
```

### 5. Run the project
```bash
py -m ai_powered_log_analysis.main
```

### 6. Check the output
Console: See the structured report immediately

Reports folder: Find saved reports with timestamps

### 7. Sample Output
📊 AI LOG ANALYSIS REPORT
======================================================================
1. EXECUTIVE SUMMARY: 
Critical issues include a third-party payment gateway timeout 
for multiple orders and a database deadlock affecting transactions.

2. LOG STATISTICS:
INFO: 7
WARN: 3
ERROR: 8

3. CRITICAL ISSUES:
- [2026-09-01 08:25:33] ERROR [PaymentModule] Third-party payment 
  gateway timeout, order #ORD-8893 (repeated 4 times)
- [2026-09-01 08:31:20] ERROR [DatabaseModule] Deadlock detected

4. PRIORITY RANKING:
1. Payment gateway timeout - impacts revenue directly
2. Database deadlock - impacts transaction consistency

5. ACTIONABLE RECOMMENDATIONS:
1. Check payment gateway provider's status page
2. Review timeout configuration
3. Implement circuit breaker pattern
======================================================================

## Technologies Used
Python 3.8+ - Core programming language
OpenRouter API - Access to multiple LLM models
requests - HTTP client for API calls
python-dotenv - Environment variable management

## Customization
Change the AI Model
Edit .env:
OPENROUTER_MODEL=anthropic/claude-3-haiku-20240307
OPENROUTER_MODEL=google/gemini-2.0-flash-lite-preview-02-05
OPENROUTER_MODEL=openai/gpt-4o-mini

## Use Your Own Logs
Place your log file in sample_logs/
Update the file path in config.py or pass it as an argument

## Use Cases
IT Operations - Automate daily log reviews
System Analysts - Quick incident triage
DevOps Teams - Proactive monitoring and alerting
IT Managers - Standardized incident reporting


## Future Enhancements
□ Real-time log monitoring (watch mode)
□ Email/Slack notifications for critical errors
□ HTML/PDF report generation
□ Support for JSON/CSV log formats
□ Local deployment with Ollama

## License

MIT License

## Author

**HwangChin**
- GitHub: [https://github.com/yourusername](https://github.com/yourusername)

---
Star this repository if you find it useful!