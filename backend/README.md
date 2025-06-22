# Stubble Burning Detection API Backend

FastAPI backend service for the stubble burning detection system, providing fire detection and tracking capabilities for Northern India.

## Features

- **Real-time Fire Detection**: Integration with NASA FIRMS API for 24-hour and 7-day fire data
- **Historical Data**: SQLite database for custom date range queries (up to 31 days)
- **Regional Filtering**: Support for states and cities in Northern India
- **Multi-source Data**: MODIS, VIIRS, and user-reported fire sources
- **Automatic Updates**: Database automatically updates with new fire detections
- **REST API**: Clean REST endpoints for frontend integration

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Fire Detection

#### POST /api/fires/detect
Detect fires based on filters

**Request Body:**
```json
{
  "region": "all-northern-india",
  "date_range": "24hr",
  "custom_start_date": null,
  "custom_end_date": null,
  "sources": {
    "MODIS": true,
    "VIIRS": true,
    "User Reported": false
  }
}
```

**Response:**
```json
{
  "fires": [
    {
      "id": "MODIS_30.7333_76.7794_2025-06-21_1030",
      "latitude": 30.7333,
      "longitude": 76.7794,
      "brightness": 325.5,
      "confidence": 75,
      "acq_date": "2025-06-21",
      "acq_time": "1030",
      "acq_datetime": "2025-06-21T10:30:00",
      "source": "MODIS",
      "frp": 12.5,
      "state": "punjab",
      "created_at": "2025-06-21T15:30:00Z"
    }
  ],
  "total_count": 67,
  "filtered_count": 67,
  "region": "all-northern-india",
  "date_range": "24hr"
}
```

#### GET /api/fires/statistics
Get fire statistics for a region

**Parameters:**
- `region`: Region identifier (default: "all-northern-india")
- `date_range`: Time range (default: "24hr")

#### GET /api/fires/regions
Get available regions for filtering

#### GET /api/fires/health
Health check endpoint

## Data Sources

### NASA FIRMS API
- **24-hour data**: `ms:fires_modis_24hrs`
- **7-day data**: `ms:fires_modis_7days`
- **Source**: MODIS thermal anomalies
- **Coverage**: South Asia region
- **Update frequency**: Real-time

### SQLite Database
- **Purpose**: Historical data storage and custom date ranges
- **Schema**: Fire detections with metadata
- **Indexes**: Optimized for date and location queries
- **Max range**: 31 days per query

## Supported Regions

### States
- Punjab
- Haryana
- Uttar Pradesh
- Delhi NCR
- Rajasthan
- Himachal Pradesh
- Uttarakhand

### Cities
- Chandigarh Area
- Amritsar Area
- Ludhiana Area
- Gurgaon Area

## Data Flow

1. **Recent Data (24hr/7day)**:
   - Frontend requests → API calls NASA FIRMS → Data processed → Saved to database → Returned to frontend

2. **Historical Data (custom range)**:
   - Frontend requests → API queries local database → Filtered by region/date → Returned to frontend

## Database Schema

```sql
CREATE TABLE fire_detections (
    id VARCHAR PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    brightness FLOAT NOT NULL,
    confidence INTEGER NOT NULL,
    acq_date VARCHAR NOT NULL,
    acq_time VARCHAR NOT NULL,
    acq_datetime DATETIME NOT NULL,
    source VARCHAR NOT NULL,
    frp FLOAT,
    scan FLOAT,
    track FLOAT,
    state VARCHAR,
    district VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

## Configuration

### Environment Variables
- `DATABASE_URL`: SQLite database path (default: `sqlite:///./fire_data.db`)
- `NASA_FIRMS_API_KEY`: Your NASA FIRMS API key
- `CORS_ORIGINS`: Allowed frontend origins

### Rate Limiting
- NASA FIRMS API has rate limits
- Automatic retry with exponential backoff
- Caching to reduce API calls

## Error Handling

- **400 Bad Request**: Invalid filter parameters
- **404 Not Found**: Region not found
- **500 Internal Server Error**: API or database errors
- **503 Service Unavailable**: NASA FIRMS API down

## Performance

- **Database indexes** on date, location, and source
- **Query optimization** for large datasets
- **Connection pooling** for concurrent requests
- **Async processing** for API calls

## Monitoring

- **Health check** endpoints
- **Structured logging** with request tracking
- **Error tracking** and alerting
- **Performance metrics**

## Development

### Running in Development
```bash
python run.py
```

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
# Initialize database
python -c "from app.database.connection import init_database; init_database()"
```

## Production Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

### Systemd Service
```ini
[Unit]
Description=Stubble Burning Detection API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
ExecStart=/usr/bin/python3 run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## License

This project is part of the Stubble Burning Detection System.