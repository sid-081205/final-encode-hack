from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database.connection import get_database
from app.models.fire import FireFilterRequest, FireFilterResponse, FireDetectionResponse
from app.services.fire_service import FireService
from app.services.historical_fire_service import HistoricalFireService
from app.utils.regions import get_available_regions

router = APIRouter(prefix="/api/fires", tags=["fires"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/detect", response_model=FireFilterResponse)
async def detect_fires(
    filter_request: FireFilterRequest,
    db: Session = Depends(get_database)
):
    """
    Detect fires based on filters
    
    - **region**: Geographic region to filter by
    - **date_range**: Time range for fire detection ("24hr", "7day", "custom")
    - **custom_start_date**: Start date for custom range (YYYY-MM-DD)
    - **custom_end_date**: End date for custom range (YYYY-MM-DD)
    - **sources**: Dictionary of enabled data sources
    """
    try:
        logger.info(f"Fire detection request: {filter_request}")
        
        # Validate custom date range
        if filter_request.date_range == "custom":
            if not filter_request.custom_start_date or not filter_request.custom_end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom date range requires both start and end dates"
                )
        
        # Initialize fire service
        fire_service = FireService(db)
        
        # Get fires based on filters
        fires = fire_service.get_fires_by_filters(
            region=filter_request.region,
            date_range=filter_request.date_range,
            custom_start_date=filter_request.custom_start_date,
            custom_end_date=filter_request.custom_end_date,
            sources=filter_request.sources
        )
        
        # Calculate statistics
        stats = fire_service.get_fire_statistics(fires)
        
        logger.info(f"Found {len(fires)} fires for region {filter_request.region}")
        
        return FireFilterResponse(
            fires=fires,
            total_count=stats["total_fires"],
            filtered_count=len(fires),
            region=filter_request.region,
            date_range=filter_request.date_range
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fire detection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/statistics")
async def get_fire_statistics(
    region: str = "all-northern-india",
    date_range: str = "24hr",
    db: Session = Depends(get_database)
):
    """
    Get fire statistics for a region and date range
    """
    try:
        fire_service = FireService(db)
        
        # Get fires for statistics
        fires = fire_service.get_fires_by_filters(
            region=region,
            date_range=date_range,
            sources={"MODIS": True, "VIIRS": True, "User Reported": True}
        )
        
        # Calculate and return statistics
        stats = fire_service.get_fire_statistics(fires)
        
        return {
            "region": region,
            "date_range": date_range,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting fire statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting statistics: {str(e)}"
        )

@router.get("/regions")
async def get_regions():
    """
    Get available regions for fire detection
    """
    try:
        regions = get_available_regions()
        return {
            "regions": regions,
            "total_regions": len(regions)
        }
    except Exception as e:
        logger.error(f"Error getting regions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting regions: {str(e)}"
        )

@router.get("/date-range")
async def get_available_date_range():
    """
    Get available date range for historical fire data
    """
    try:
        historical_service = HistoricalFireService()
        date_range = historical_service.get_available_date_range()
        
        return {
            "available_range": date_range,
            "message": f"Historical fire data available from {date_range['min_date']} to {date_range['max_date']}"
        }
    except Exception as e:
        logger.error(f"Error getting date range: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting date range: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "fire-detection-api",
        "version": "1.0.0"
    }