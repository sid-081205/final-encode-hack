# stubble burning detection & prediction system

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

ai-powered fire detection and prediction system for northern india using satellite data, ml models, and real-time monitoring.

## architecture

real-time satellite fire detection via nasa firms + ml prediction models + ai chatbot for analysis and reporting.

## screenshots

![Screenshot 2025-06-22 at 11.58.12](Screenshot%202025-06-22%20at%2011.58.12.png)

![Screenshot 2025-06-22 at 11.58.24](Screenshot%202025-06-22%20at%2011.58.24.png)

![Screenshot 2025-06-22 at 11.58.50](Screenshot%202025-06-22%20at%2011.58.50.png)

![Screenshot 2025-06-23 at 15.24.48](Screenshot%202025-06-23%20at%2015.24.48.png)

![Screenshot 2025-06-23 at 15.25.40](Screenshot%202025-06-23%20at%2015.25.40.png)

## features

### fire detection
- nasa firms integration (modis/viirs sensors)
- interactive maps with clustered markers
- 300k+ historical fire records
- regional filtering and confidence scoring

### ml prediction
- random forest models with 18 features
- weather data integration
- 7-day forecasting with risk classification
- historical pattern analysis (2+ years data)

### ai chatbot
- claude ai integration for analysis
- real-time prediction generation
- pdf report export
- natural language queries

### citizen reporting
- gps-enabled incident reporting
- map visualization of user reports
- authority notification system

## tech stack

**backend**: fastapi, python 3.8+, sqlalchemy, sqlite, scikit-learn, claude ai  
**frontend**: next.js 14, typescript, react, tailwind css, leaflet  
**apis**: nasa firms, openweathermap, anthropic claude

## installation

### prerequisites
- node.js 18+, python 3.8+, git

### setup
```bash
# clone repo
git clone <repository-url>
cd final-encode-hack

# backend setup
cd backend
python -m venv venv
source venv/bin/activate  # windows: venv\scripts\activate
pip install uvicorn fastapi python-dotenv anthropic pandas sqlalchemy reportlab

# create .env with claude api key
echo 'CLAUDE_API_KEY="your_key_here"' > .env

# start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

**access**: frontend at http://localhost:3000, api at http://localhost:8000

## api endpoints

### fire detection
```
GET /api/fires/detected      # all detected fires
GET /api/fires/regions       # available regions
POST /api/fires/user-report  # submit citizen report
```

### predictions
```
POST /api/predictions/generate  # generate ml predictions
GET /api/predictions/regions    # prediction regions
```

### chatbot
```
POST /api/chat/message                    # send message
POST /api/chat/generate-prediction-report # generate pdf
```

## ml model

**type**: random forest ensemble  
**training data**: 321k+ fire records (2023-2025)  
**features**: 18 parameters (weather, crop patterns, historical data)  
**accuracy**: 89.2% overall, 85.7% precision, 92.1% recall  
**coverage**: northern india, 7-day predictions, ~11km resolution

## license

mit license