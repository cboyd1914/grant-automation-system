#!/bin/bash

# Enhanced Grant Automation System
# Daily discovery and analysis with business-specific targeting

echo "🚀 Enhanced Grant Automation System"
echo "=================================="
echo "Starting enhanced grant discovery and analysis..."
echo "Timestamp: $(date)"
echo ""

# Set up environment
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/config"

# Create directories if they don't exist
mkdir -p data logs reports

# Run enhanced grant discovery
echo "📡 Running enhanced grant discovery..."
python3 scripts/enhanced_grant_discovery.py

if [ $? -eq 0 ]; then
    echo "✅ Enhanced discovery completed successfully"
    echo ""
    
    # Run enhanced analysis
    echo "📊 Running enhanced grant analysis..."
    python3 scripts/enhanced_grant_analyzer.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Enhanced analysis completed successfully"
        echo ""
        
        # Display summary
        echo "📋 Enhanced Grant Automation Summary"
        echo "==================================="
        echo "✅ Discovery: Completed with business-specific targeting"
        echo "✅ Analysis: Generated with strategic priority scoring"
        echo "✅ Reports: Created with action plan and business insights"
        echo ""
        echo "📁 Check the reports/ directory for:"
        echo "   - Enhanced Excel analysis with multiple worksheets"
        echo "   - Markdown report with business-specific insights"
        echo "   - Action plan with prioritized grant opportunities"
        echo ""
        echo "🎯 Focus Areas Covered:"
        echo "   - Minority-owned business development"
        echo "   - Financial literacy & economic empowerment"
        echo "   - Technology & workforce development"
        echo "   - Youth AI empowerment & digital inclusion"
        echo ""
        echo "🔗 Next Steps:"
        echo "   1. Review the action plan in the Excel report"
        echo "   2. Research top priority grants"
        echo "   3. Begin application preparation for critical opportunities"
        echo ""
        echo "Enhanced grant automation completed at $(date)"
        
    else
        echo "❌ Enhanced analysis failed"
        exit 1
    fi
else
    echo "❌ Enhanced discovery failed"
    exit 1
fi

