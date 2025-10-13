# Grant Automation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Daily Grant Discovery](https://github.com/YOUR_USERNAME/grant-automation-system/actions/workflows/daily-grants.yml/badge.svg)](https://github.com/YOUR_USERNAME/grant-automation-system/actions/workflows/daily-grants.yml)

A comprehensive daily grant discovery and processing system that automatically finds, analyzes, and reports on new grant opportunities from multiple sources.

## 🚀 Features

- **Automated Grant Discovery**: Searches grants.gov API for new opportunities
- **Intelligent Filtering**: Filters grants based on customizable criteria
- **Data Enrichment**: Adds urgency levels, relevance scores, and categorization
- **Multiple Output Formats**: Generates Excel spreadsheets and Markdown reports
- **Priority Ranking**: Automatically ranks grants by relevance and urgency
- **Comprehensive Logging**: Detailed logs for monitoring and debugging

## 📁 Project Structure

```
grant_automation/
├── config/
│   └── settings.py          # Configuration settings
├── scripts/
│   ├── grant_discovery.py   # Main discovery script
│   └── grant_analyzer.py    # Data analysis and reporting
├── data/                    # Raw grant data (JSON files)
├── reports/                 # Generated reports (Excel, Markdown)
├── logs/                    # System logs
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/grant-automation-system.git
cd grant-automation-system

# Install dependencies
pip install -r requirements.txt

# Run your first grant discovery
./run_daily_grants.sh
```

## 🛠️ Installation

1. **Clone or download the project**:
   ```bash
   cd grant_automation
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python3 scripts/grant_discovery.py --help
   ```

## 🔧 Configuration

Edit `config/settings.py` to customize:

- **Search Keywords**: Modify `SEARCH_CRITERIA['keywords']`
- **Minimum Grant Amount**: Adjust `SEARCH_CRITERIA['min_amount']`
- **Age Limit**: Change `SEARCH_CRITERIA['max_days_old']`
- **Categories**: Update `SEARCH_CRITERIA['categories']`

Example configuration:
```python
SEARCH_CRITERIA = {
    'keywords': ['technology', 'innovation', 'AI', 'machine learning'],
    'min_amount': 25000,
    'max_days_old': 14,
    'categories': ['Science & Technology', 'Research']
}
```

## 🚀 Usage

### Daily Grant Discovery

Run the main discovery script:
```bash
python3 scripts/grant_discovery.py
```

This will:
1. Search grants.gov for new opportunities
2. Filter results based on your criteria
3. Save raw data to `data/` directory
4. Display summary statistics

### Grant Analysis and Reporting

Process discovered grants:
```bash
python3 scripts/grant_analyzer.py
```

This will:
1. Load the latest grant data
2. Enrich with additional information
3. Generate Excel and Markdown reports
4. Create priority rankings

### Automated Daily Workflow

For daily automation, create a cron job:
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/grant_automation && python3 scripts/grant_discovery.py && python3 scripts/grant_analyzer.py
```

## 📊 Output Files

### Data Files
- `data/grants_discovery_YYYYMMDD_HHMMSS.json`: Raw grant data

### Reports
- `reports/grants_analysis_YYYYMMDD_HHMMSS.xlsx`: Excel workbook with multiple sheets
- `reports/grants_report_YYYYMMDD_HHMMSS.md`: Comprehensive Markdown report

### Logs
- `logs/grant_discovery_YYYYMMDD.log`: Discovery process logs
- `logs/grant_analyzer_YYYYMMDD.log`: Analysis process logs

## 📈 Report Contents

### Excel Report Sheets
1. **All Grants**: Complete dataset with enriched information
2. **Priority Grants**: Top 20 grants ranked by relevance and urgency
3. **Summary**: Statistical overview
4. **Urgent Grants**: Grants with approaching deadlines

### Markdown Report Sections
1. **Executive Summary**: Key statistics and metrics
2. **Top Priority Grants**: Detailed list of highest-priority opportunities
3. **Urgent Grants**: Grants closing soon
4. **Statistics by Category**: Breakdown by agency, status, urgency, etc.

## 🎯 Grant Scoring System

Grants are scored based on:
- **Relevance Score**: Keyword matches in title (0-6 points)
- **Urgency Weight**: Days until deadline (0-4 points)
- **Status Bonus**: Active grants get extra points
- **Recency Bonus**: Recently posted grants get extra points

## 🔍 Data Sources

### Primary Sources
- **grants.gov API**: Official federal grant database
  - No authentication required
  - Real-time data
  - Comprehensive federal opportunities

### Future Expansion
- **GrantWatch.com**: Subscription-based database (requires paid access)
- **Foundation Directory**: Private foundation grants (requires subscription)
- **State and Local Databases**: Regional opportunities

## 🚨 Troubleshooting

### Common Issues

1. **No grants found**:
   - Check internet connection
   - Verify grants.gov API is accessible
   - Adjust search criteria (broader keywords)

2. **API errors**:
   - Check logs for detailed error messages
   - Verify API endpoint is correct
   - Implement retry logic for temporary failures

3. **Missing dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Permission errors**:
   - Ensure write permissions for data/, reports/, and logs/ directories
   - Check file ownership and permissions

### Debug Mode

Enable verbose logging by editing `config/settings.py`:
```python
LOG_LEVEL = 'DEBUG'
```

## 📅 Scheduling Recommendations

### Daily Discovery
- **Best Time**: Early morning (6-9 AM)
- **Frequency**: Once per day
- **Duration**: 5-10 minutes typical

### Weekly Analysis
- **Best Time**: Monday morning
- **Purpose**: Review weekly trends and plan applications

### Monthly Review
- **Purpose**: Update search criteria and evaluate system performance

## 🔐 Security Considerations

- **No sensitive data**: System doesn't store personal information
- **API keys**: Currently no API keys required for grants.gov
- **Network access**: Requires outbound HTTPS connections
- **File permissions**: Ensure appropriate access controls on output files

## 🚀 Advanced Usage

### Custom Filters

Add custom filtering logic in `grant_discovery.py`:
```python
def custom_filter(grant_info):
    # Add your custom logic here
    if grant_info.get('agency_code') == 'NSF':
        return True
    return False
```

### Additional Data Sources

Extend the system by adding new sources in `search_additional_sources()`:
```python
def search_additional_sources(self):
    # Add new grant sources here
    additional_grants = []
    # Your implementation
    return additional_grants
```

### Email Notifications

Configure email alerts in `config/settings.py`:
```python
EMAIL_NOTIFICATIONS = {
    'enabled': True,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your_email@gmail.com',
    'password': 'your_app_password',
    'recipients': ['recipient@example.com']
}
```

## 📞 Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review configuration in `config/settings.py`
3. Verify network connectivity to grants.gov
4. Ensure all dependencies are installed

## 📄 License

This project is provided as-is for educational and research purposes. Please respect the terms of service of all data sources used.

## 🔄 Updates and Maintenance

### Regular Maintenance
- Monitor logs for errors
- Update search criteria based on results
- Review and adjust filtering logic
- Check for API changes or updates

### System Updates
- Keep Python dependencies updated
- Monitor grants.gov for API changes
- Add new data sources as they become available

## 🤖 GitHub Automation

This repository includes GitHub Actions for automated daily grant discovery:

### Automatic Daily Discovery
- Runs every day at 9 AM UTC
- Discovers new grants automatically
- Generates reports and saves them as artifacts
- Can be manually triggered from the Actions tab

### Setting Up GitHub Actions
1. Fork this repository
2. Enable GitHub Actions in your repository settings
3. The workflow will run automatically according to the schedule
4. View results in the "Actions" tab

### Manual Trigger
You can manually run the grant discovery from GitHub:
1. Go to the "Actions" tab in your repository
2. Select "Daily Grant Discovery"
3. Click "Run workflow"

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test them
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Last Updated**: September 8, 2025
**Version**: 1.0.0

