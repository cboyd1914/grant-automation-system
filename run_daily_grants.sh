#!/bin/bash

# Daily Grant Automation Script
# Runs grant discovery and analysis

echo "🔍 Starting Daily Grant Automation"
echo "=================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "Started at: $TIMESTAMP"

# Run grant discovery
echo ""
echo "📡 Running Grant Discovery..."
python3 scripts/grant_discovery.py

if [ $? -eq 0 ]; then
    echo "✅ Grant discovery completed successfully"
else
    echo "❌ Grant discovery failed"
    exit 1
fi

# Run grant analysis
echo ""
echo "📊 Running Grant Analysis..."
python3 scripts/grant_analyzer.py

if [ $? -eq 0 ]; then
    echo "✅ Grant analysis completed successfully"
else
    echo "❌ Grant analysis failed"
    exit 1
fi

# Show summary
echo ""
echo "📋 Summary:"
echo "- Data files: $(ls -1 data/grants_discovery_*.json 2>/dev/null | wc -l) total"
echo "- Latest reports in: reports/"
echo "- Logs available in: logs/"

# Show latest files
echo ""
echo "📁 Latest Files:"
echo "Data: $(ls -1t data/grants_discovery_*.json 2>/dev/null | head -1)"
echo "Excel: $(ls -1t reports/grants_analysis_*.xlsx 2>/dev/null | head -1)"
echo "Report: $(ls -1t reports/grants_report_*.md 2>/dev/null | head -1)"

echo ""
echo "🎉 Daily grant automation completed!"
echo "Finished at: $(date +"%Y-%m-%d %H:%M:%S")"

