# Polar Sleep Analysis with AI

n8n workflow for automated sleep data analysis using Polar API, MongoDB, and Ollama LLM.

## Tech Stack

- **n8n** - Workflow automation
- **MongoDB** - Data storage
- **Ollama (Mistral 7B)** - AI analysis
- **Python** - Custom sleep analytics
- **Docker** - Containerization
- **Telegram Bot** - Notifications and reports

## Features

- Polar OAuth2 integration
- Sleep metrics analysis (REM, deep, light sleep)
- AI-generated insights
- Automated data processing pipeline
- MongoDB persistence

## Quick Start

```bash
# Set environment variables in .env
cp .env.example .env

# Start services
docker-compose up -d
```

## Workflow

1. Authenticate with Polar API
2. Fetch sleep data
3. Process with Python analytics
4. Store in MongoDB
5. Generate AI insights

## Architecture

```
Polar API → n8n → Python Analytics → MongoDB
                ↓
            Ollama LLM (AI Insights)
```

## Project Structure

```
├── docker-compose.yml       # Service orchestration
├── polar-sync/
│   └── n8n-flow.json       # Main workflow
├── sleep/
│   └── simple_sleep_analyzer.py  # Custom analytics
├── mongo-init/              # DB initialization
└── llm-init/               # Ollama setup
```

## Sample Output

```
SLEEP ANALYSIS - 06/08/2025

🕐 SLEEP TIME:
   Bedtime: 23:19 | Wake time: 06:30
   Time in bed: 7h 10m
   Actual sleep: 6h 49m
   Sleep goal: 7h 30m
   Deficit: 41m
   Efficiency: 95.0%

🧠 SLEEP PHASES:
   • Light:  4h 15m  (62.5%) (Normal: 44-65%)
   • Deep: 1h 10m (17.2%) (Normal: 17-20%)
   • REM:     1h 23m (20.3%) (Normal: 20-25%)
   • Unrecognized: 0m (0.0%) (Normal: 0-10%)

📊 SLEEP QUALITY:
   Overall score: 84/100
   Continuity: 3.5/5.0 low
   Sleep cycles: 4
   Sleep charge: 4/5 (vs usual level)

⚠️  AWAKENINGS:
   • Wake episodes: 19

💡 RECOMMENDATIONS:
 1. 🕐 Increase sleep time by 41m for optimal recovery
 2. 😴 Moderate continuity: create consistent bedtime ritual
 3. ✨ Excellent sleep quality! Continue current habits
 4. 🌟 Optimal sleep phase ratio for recovery
```

Raw data available in `polar-sync/polar-examples/`
