from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.services.claude_service import ClaudeService

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Claude service
claude_service = ClaudeService()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None

class ReportRequest(BaseModel):
    fire_id: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    report_type: str = "general"  # "general", "specific", "summary"

class PredictionReportRequest(BaseModel):
    criteria: Optional[Dict[str, Any]] = None
    format: str = "pdf"  # "pdf", "text"
    region: Optional[str] = None
    risk_level: Optional[str] = None

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(chat_request: ChatRequest):
    """
    Send a message to the AI assistant and get a response
    """
    try:
        logger.info(f"Received chat message: {chat_request.message[:100]}...")
        
        # Convert ChatMessage objects to dictionaries for Claude service
        history = []
        if chat_request.conversation_history:
            for msg in chat_request.conversation_history:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Get response from Claude
        response = await claude_service.chat_with_claude(
            user_message=chat_request.message,
            conversation_history=history
        )
        
        logger.info(f"Generated response: {response[:100]}...")
        
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )

@router.post("/generate-report")
async def generate_fire_report(report_request: ReportRequest):
    """
    Generate a fire report for authorities
    """
    try:
        logger.info(f"Generating fire report: {report_request.report_type}")
        
        report = claude_service.generate_fire_report(
            fire_id=report_request.fire_id,
            criteria=report_request.criteria
        )
        
        return {"report": report, "type": report_request.report_type}
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )

@router.get("/fire-summary")
async def get_fire_summary():
    """
    Get a summary of fire data
    """
    try:
        summary = claude_service.get_fire_data_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Error getting fire summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting fire summary: {str(e)}"
        )

@router.get("/top-fires")
async def get_top_fires(limit: int = 5, min_power: float = 0):
    """
    Get top fires by power
    """
    try:
        criteria = {"limit": limit}
        if min_power > 0:
            criteria["min_power"] = min_power
            
        fires = claude_service.get_fires_by_criteria(criteria)
        return {"fires": fires, "count": len(fires)}
        
    except Exception as e:
        logger.error(f"Error getting top fires: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting top fires: {str(e)}"
        )

@router.post("/generate-prediction-report")
async def generate_prediction_pdf_report(report_request: PredictionReportRequest):
    """
    Generate a PDF report for predicted fires for authorities
    """
    try:
        logger.info(f"Generating prediction PDF report")
        
        # Build criteria from request
        criteria = report_request.criteria or {}
        if report_request.region:
            criteria['region'] = report_request.region
        if report_request.risk_level:
            criteria['risk_level'] = report_request.risk_level
        
        if report_request.format == "pdf":
            # Generate PDF report
            pdf_bytes = claude_service.generate_prediction_pdf_report(criteria)
            
            if not pdf_bytes:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate PDF report"
                )
            
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=fire_prediction_report.pdf"
                }
            )
        else:
            # Generate text report (fallback)
            predictions = claude_service.get_predictions_by_criteria(criteria)
            summary = claude_service.get_prediction_data_summary()
            
            return {
                "report_type": "prediction_summary",
                "summary": summary,
                "predictions": predictions[:10],  # Top 10
                "total_count": len(predictions)
            }
        
    except Exception as e:
        logger.error(f"Error generating prediction report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating prediction report: {str(e)}"
        )

@router.get("/prediction-summary")
async def get_prediction_summary():
    """
    Get a summary of prediction data
    """
    try:
        summary = claude_service.get_prediction_data_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Error getting prediction summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting prediction summary: {str(e)}"
        )

@router.get("/top-predictions")
async def get_top_predictions(limit: int = 5, min_probability: float = 0, risk_level: str = None):
    """
    Get top predictions by probability
    """
    try:
        criteria = {"limit": limit}
        if min_probability > 0:
            criteria["min_probability"] = min_probability
        if risk_level:
            criteria["risk_level"] = risk_level
            
        predictions = claude_service.get_predictions_by_criteria(criteria)
        return {"predictions": predictions, "count": len(predictions)}
        
    except Exception as e:
        logger.error(f"Error getting top predictions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting top predictions: {str(e)}"
        )

@router.get("/health")
async def chat_health_check():
    """
    Health check for chat service
    """
    try:
        # Test Claude service
        summary = claude_service.get_fire_data_summary()
        prediction_summary = claude_service.get_prediction_data_summary()
        
        return {
            "status": "healthy",
            "service": "ai-chat-service",
            "version": "1.0.0",
            "claude_api": "connected",
            "database": "connected" if "error" not in summary else "error",
            "features": {
                "fire_reports": True,
                "prediction_reports": True,
                "pdf_generation": True,
                "data_analysis": True,
                "conversation": True,
                "fire_statistics": True,
                "prediction_statistics": True
            },
            "data_status": {
                "fires": summary.get('total_fires', 0),
                "predictions": prediction_summary.get('total_predictions', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )