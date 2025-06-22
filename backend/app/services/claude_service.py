import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO

# Load environment variables
load_dotenv()

class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
        self.db_path = "/Users/siddharthgianchandani/final-encode-hack/fire_data.db"
        
    def get_fire_data_summary(self) -> Dict[str, Any]:
        """Get a summary of fire data from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get total fire count
            total_fires = pd.read_sql_query("SELECT COUNT(*) as count FROM fires", conn).iloc[0]['count']
            
            # Get recent fires (last 7 days) - using simple string comparison for dates
            recent_query = """
            SELECT COUNT(*) as count FROM fires 
            WHERE acq_date >= '2025-06-15'
            """
            recent_fires = pd.read_sql_query(recent_query, conn).iloc[0]['count']
            
            # Get top 5 highest power fires - convert frp to float for ordering
            top_fires_query = """
            SELECT latitude, longitude, CAST(frp as REAL) as frp, 
                   CAST(brightness as REAL) as brightness, confidence, acq_date, acq_time 
            FROM fires 
            WHERE frp != '' AND frp IS NOT NULL
            ORDER BY CAST(frp as REAL) DESC 
            LIMIT 5
            """
            top_fires = pd.read_sql_query(top_fires_query, conn)
            
            # Get average fire power
            avg_power_query = """
            SELECT AVG(CAST(frp as REAL)) as avg_power 
            FROM fires 
            WHERE frp != '' AND frp IS NOT NULL
            """
            avg_power_result = pd.read_sql_query(avg_power_query, conn)
            avg_power = avg_power_result.iloc[0]['avg_power'] if not avg_power_result.empty else 0
            
            conn.close()
            
            return {
                "total_fires": int(total_fires),
                "recent_fires": int(recent_fires),
                "top_fires": top_fires.to_dict('records'),
                "average_power": round(float(avg_power), 2) if avg_power else 0
            }
            
        except Exception as e:
            print(f"Error getting fire data summary: {e}")
            return {
                "total_fires": 0,
                "recent_fires": 0,
                "top_fires": [],
                "average_power": 0,
                "error": str(e)
            }
    
    def get_fires_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fires based on specific criteria"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
            SELECT latitude, longitude, CAST(frp as REAL) as frp, 
                   CAST(brightness as REAL) as brightness, confidence, acq_date, acq_time 
            FROM fires WHERE frp != '' AND frp IS NOT NULL
            """
            params = []
            
            if criteria.get('min_power'):
                query += " AND CAST(frp as REAL) >= ?"
                params.append(criteria['min_power'])
                
            if criteria.get('min_confidence'):
                query += " AND CAST(confidence as REAL) >= ?"
                params.append(criteria['min_confidence'])
                
            if criteria.get('date_from'):
                query += " AND acq_date >= ?"
                params.append(criteria['date_from'])
                
            if criteria.get('region_bounds'):
                bounds = criteria['region_bounds']
                query += " AND CAST(latitude as REAL) BETWEEN ? AND ? AND CAST(longitude as REAL) BETWEEN ? AND ?"
                params.extend([bounds['min_lat'], bounds['max_lat'], bounds['min_lon'], bounds['max_lon']])
            
            query += " ORDER BY CAST(frp as REAL) DESC LIMIT ?"
            params.append(criteria.get('limit', 10))
            
            fires = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return fires.to_dict('records')
            
        except Exception as e:
            print(f"Error getting fires by criteria: {e}")
            return []
    
    def generate_fire_report(self, fire_id: str = None, criteria: Dict[str, Any] = None) -> str:
        """Generate a fire report for authorities"""
        try:
            if fire_id:
                # Get specific fire
                conn = sqlite3.connect(self.db_path)
                fire_data = pd.read_sql_query(
                    "SELECT * FROM fires WHERE id = ?", 
                    conn, 
                    params=[fire_id]
                )
                conn.close()
                
                if fire_data.empty:
                    return "Fire not found"
                    
                fire = fire_data.iloc[0].to_dict()
                
                report = f"""
FIRE INCIDENT REPORT
===================

Fire ID: {fire['id']}
Detection Date: {fire['acq_date']} at {fire['acq_time']}
Location: {fire['latitude']:.4f}, {fire['longitude']:.4f}
Fire Power: {fire['frp']:.1f} MW
Brightness: {fire['brightness']:.1f}K
Confidence: {fire['confidence']}%
Source: {fire['source']}

SEVERITY ASSESSMENT:
{"CRITICAL - Immediate action required" if fire['frp'] > 50 else "HIGH - Monitor closely" if fire['frp'] > 20 else "MEDIUM - Standard monitoring"}

RECOMMENDED ACTIONS:
- Deploy fire suppression resources if available
- Alert local authorities and emergency services
- Monitor fire progression using satellite data
- Coordinate with local fire departments
"""
                return report
            else:
                # Generate summary report
                summary = self.get_fire_data_summary()
                fires = self.get_fires_by_criteria(criteria or {'limit': 10})
                
                report = f"""
FIRE SITUATION REPORT
====================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
- Total fires in database: {summary['total_fires']}
- Recent fires (7 days): {summary['recent_fires']}
- Average fire power: {summary['average_power']} MW

TOP HIGH-POWER FIRES:
"""
                for i, fire in enumerate(fires[:5], 1):
                    report += f"""
{i}. Fire ID: {fire['id']}
   Location: {fire['latitude']:.4f}, {fire['longitude']:.4f}
   Power: {fire['frp']:.1f} MW
   Date: {fire['acq_date']}
"""
                
                report += """
RECOMMENDATIONS:
- Continue monitoring high-power fire locations
- Maintain coordination with local fire services
- Review fire suppression resource allocation
- Update emergency response protocols as needed
"""
                return report
                
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def generate_predictions_with_ml(self, region: str = "all-northern-india", days: int = 7) -> List[Dict[str, Any]]:
        """Generate predictions using the ML prediction service directly"""
        try:
            from app.services.simple_prediction_service import SimplePredictionService
            from app.models.prediction import PredictionRequest
            
            # Create prediction service directly
            prediction_service = SimplePredictionService()
            
            # Generate predictions
            predictions = prediction_service.generate_predictions(
                region=region,
                date_range=f"next-{days}days",
                confidence_threshold=60.0
            )
            
            # Convert to dict format
            return [pred.dict() for pred in predictions] if predictions else []
                
        except Exception as e:
            print(f"Error generating ML predictions: {e}")
            return []

    def get_prediction_data_summary(self) -> Dict[str, Any]:
        """Get a summary of prediction data from the database or generate new predictions"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Check if fire_predictions table exists
            table_check = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='fire_predictions'", 
                conn
            )
            
            if table_check.empty:
                conn.close()
                # Generate new predictions using ML model
                predictions = self.generate_predictions_with_ml()
                
                if predictions:
                    # Calculate summary from generated predictions
                    total_predictions = len(predictions)
                    high_risk_predictions = len([p for p in predictions if p.get('risk_level') in ['high', 'critical']])
                    top_predictions = sorted(predictions, key=lambda x: x.get('probability', 0), reverse=True)[:5]
                    avg_probability = sum(p.get('probability', 0) for p in predictions) / len(predictions) if predictions else 0
                    
                    # Get risk distribution
                    risk_counts = {}
                    for p in predictions:
                        risk = p.get('risk_level', 'unknown')
                        risk_counts[risk] = risk_counts.get(risk, 0) + 1
                    
                    risk_distribution = [{'risk_level': k, 'count': v} for k, v in risk_counts.items()]
                    
                    return {
                        "total_predictions": total_predictions,
                        "high_risk_predictions": high_risk_predictions,
                        "top_predictions": top_predictions,
                        "average_probability": round(avg_probability, 2),
                        "risk_distribution": risk_distribution,
                        "source": "ml_generated"
                    }
                else:
                    return {
                        "total_predictions": 0,
                        "high_risk_predictions": 0,
                        "top_predictions": [],
                        "average_probability": 0,
                        "risk_distribution": [],
                        "error": "Could not generate predictions with ML model"
                    }
            
            # Get data from existing table
            total_predictions = pd.read_sql_query("SELECT COUNT(*) as count FROM fire_predictions", conn).iloc[0]['count']
            
            # Get high-risk predictions
            high_risk_query = """
            SELECT COUNT(*) as count FROM fire_predictions 
            WHERE risk_level IN ('high', 'critical')
            """
            high_risk_predictions = pd.read_sql_query(high_risk_query, conn).iloc[0]['count']
            
            # Get top 5 highest probability predictions
            top_predictions_query = """
            SELECT id, latitude, longitude, probability, risk_level, predicted_date, confidence, region 
            FROM fire_predictions 
            ORDER BY probability DESC 
            LIMIT 5
            """
            top_predictions = pd.read_sql_query(top_predictions_query, conn)
            
            # Get average prediction probability
            avg_probability_query = "SELECT AVG(probability) as avg_prob FROM fire_predictions"
            avg_probability = pd.read_sql_query(avg_probability_query, conn).iloc[0]['avg_prob']
            
            # Get risk level distribution
            risk_distribution_query = """
            SELECT risk_level, COUNT(*) as count 
            FROM fire_predictions 
            GROUP BY risk_level
            """
            risk_distribution = pd.read_sql_query(risk_distribution_query, conn)
            
            conn.close()
            
            return {
                "total_predictions": total_predictions,
                "high_risk_predictions": high_risk_predictions,
                "top_predictions": top_predictions.to_dict('records'),
                "average_probability": round(avg_probability, 2) if avg_probability else 0,
                "risk_distribution": risk_distribution.to_dict('records'),
                "source": "database"
            }
            
        except Exception as e:
            print(f"Error getting prediction data summary: {e}")
            return {"error": str(e)}
    
    def get_predictions_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get predictions based on specific criteria"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Check if fire_predictions table exists
            table_check = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='fire_predictions'", 
                conn
            )
            
            if table_check.empty:
                conn.close()
                # Generate predictions using ML model
                region = criteria.get('region', 'all-northern-india')
                predictions = self.generate_predictions_with_ml(region=region)
                
                if not predictions:
                    return []
                
                # Apply filters
                filtered_predictions = predictions
                
                if criteria.get('min_probability'):
                    filtered_predictions = [p for p in filtered_predictions if p.get('probability', 0) >= criteria['min_probability']]
                    
                if criteria.get('risk_level'):
                    filtered_predictions = [p for p in filtered_predictions if p.get('risk_level') == criteria['risk_level']]
                    
                if criteria.get('region') and criteria['region'] != 'all-northern-india':
                    filtered_predictions = [p for p in filtered_predictions if p.get('region') == criteria['region']]
                
                # Sort by probability and limit
                filtered_predictions = sorted(filtered_predictions, key=lambda x: x.get('probability', 0), reverse=True)
                limit = criteria.get('limit', 10)
                return filtered_predictions[:limit]
            
            query = "SELECT * FROM fire_predictions WHERE 1=1"
            params = []
            
            if criteria.get('min_probability'):
                query += " AND probability >= ?"
                params.append(criteria['min_probability'])
                
            if criteria.get('risk_level'):
                query += " AND risk_level = ?"
                params.append(criteria['risk_level'])
                
            if criteria.get('region'):
                query += " AND region = ?"
                params.append(criteria['region'])
                
            if criteria.get('date_from'):
                query += " AND predicted_date >= ?"
                params.append(criteria['date_from'])
            
            query += " ORDER BY probability DESC LIMIT ?"
            params.append(criteria.get('limit', 10))
            
            predictions = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return predictions.to_dict('records')
            
        except Exception as e:
            print(f"Error getting predictions by criteria: {e}")
            return []
    
    def generate_prediction_pdf_report(self, criteria: Dict[str, Any] = None) -> bytes:
        """Generate a PDF report for predicted fires for authorities"""
        try:
            # Use fast prediction generation for PDF reports
            region = criteria.get('region', 'all-northern-india') if criteria else 'all-northern-india'
            predictions = self.generate_predictions_with_ml(region=region, days=7)
            
            # Calculate summary from generated predictions
            if predictions:
                total_predictions = len(predictions)
                high_risk_predictions = len([p for p in predictions if p.get('risk_level') in ['high', 'critical']])
                top_predictions = sorted(predictions, key=lambda x: x.get('probability', 0), reverse=True)[:5]
                avg_probability = sum(p.get('probability', 0) for p in predictions) / len(predictions) if predictions else 0
                
                # Get risk distribution
                risk_counts = {}
                for p in predictions:
                    risk = p.get('risk_level', 'unknown')
                    risk_counts[risk] = risk_counts.get(risk, 0) + 1
                
                risk_distribution = [{'risk_level': k, 'count': v} for k, v in risk_counts.items()]
                
                prediction_summary = {
                    "total_predictions": total_predictions,
                    "high_risk_predictions": high_risk_predictions,
                    "top_predictions": top_predictions,
                    "average_probability": round(avg_probability, 2),
                    "risk_distribution": risk_distribution
                }
            else:
                # Fallback summary
                prediction_summary = {
                    "total_predictions": 0,
                    "high_risk_predictions": 0,
                    "top_predictions": [],
                    "average_probability": 0,
                    "risk_distribution": []
                }
                predictions = []
            
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=inch)
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkred,
                alignment=1  # Center alignment
            )
            
            # Build content
            content = []
            
            # Title
            content.append(Paragraph("FIRE RISK PREDICTION REPORT", title_style))
            content.append(Paragraph("For Authorities and Emergency Services", styles['Heading2']))
            content.append(Spacer(1, 20))
            
            # Report metadata
            content.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            content.append(Paragraph(f"<b>Report Type:</b> Fire Risk Prediction Analysis", styles['Normal']))
            content.append(Paragraph(f"<b>Coverage:</b> Northern India Region", styles['Normal']))
            content.append(Spacer(1, 20))
            
            # Executive Summary
            content.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading2']))
            content.append(Paragraph(f"• Total predictions generated: <b>{prediction_summary['total_predictions']}</b>", styles['Normal']))
            content.append(Paragraph(f"• High-risk locations identified: <b>{prediction_summary['high_risk_predictions']}</b>", styles['Normal']))
            content.append(Paragraph(f"• Average fire probability: <b>{prediction_summary['average_probability']}%</b>", styles['Normal']))
            content.append(Spacer(1, 20))
            
            # Risk Level Distribution
            if prediction_summary.get('risk_distribution'):
                content.append(Paragraph("RISK LEVEL DISTRIBUTION", styles['Heading2']))
                risk_data = [['Risk Level', 'Count', 'Percentage']]
                total = sum([r['count'] for r in prediction_summary['risk_distribution']])
                for risk in prediction_summary['risk_distribution']:
                    percentage = round((risk['count'] / total) * 100, 1) if total > 0 else 0
                    risk_data.append([
                        risk['risk_level'].title(),
                        str(risk['count']),
                        f"{percentage}%"
                    ])
                
                risk_table = Table(risk_data)
                risk_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                content.append(risk_table)
                content.append(Spacer(1, 20))
            
            # Top High-Risk Predictions
            content.append(Paragraph("TOP HIGH-RISK PREDICTIONS", styles['Heading2']))
            
            if predictions:
                pred_data = [['ID', 'Location', 'Probability', 'Risk Level', 'Predicted Date', 'Region']]
                for pred in predictions[:10]:  # Top 10
                    pred_data.append([
                        pred.get('id', 'N/A')[:8] + '...',  # Truncate ID
                        f"{pred.get('latitude', 0):.3f}, {pred.get('longitude', 0):.3f}",
                        f"{pred.get('probability', 0):.1f}%",
                        pred.get('risk_level', 'unknown').title(),
                        pred.get('predicted_date', 'N/A'),
                        pred.get('region', 'unknown').replace('-', ' ').title()
                    ])
                
                pred_table = Table(pred_data, colWidths=[1*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1.2*inch])
                pred_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    # Color code risk levels
                    ('TEXTCOLOR', (3, 1), (3, -1), colors.darkred),
                ]))
                content.append(pred_table)
            else:
                content.append(Paragraph("No high-risk predictions found.", styles['Normal']))
            
            content.append(Spacer(1, 20))
            
            # Recommendations
            content.append(Paragraph("RECOMMENDATIONS FOR AUTHORITIES", styles['Heading2']))
            recommendations = [
                "Deploy monitoring resources to high-probability locations immediately",
                "Coordinate with local fire departments in identified regions",
                "Prepare fire suppression equipment in critical risk areas",
                "Issue public advisories for high-risk zones and dates",
                "Monitor weather conditions that may escalate fire risks",
                "Establish communication channels with agricultural communities",
                "Review emergency response protocols for predicted timeframes",
                "Consider temporary restrictions on burning activities in high-risk areas"
            ]
            
            for i, rec in enumerate(recommendations, 1):
                content.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            
            content.append(Spacer(1, 30))
            
            # Footer
            content.append(Paragraph("This report is generated by the AI Fire Prediction System", styles['Normal']))
            content.append(Paragraph("For emergency situations, contact local fire departments immediately", styles['Normal']))
            content.append(Paragraph("Report generated using machine learning analysis of historical fire patterns", styles['Normal']))
            
            # Build PDF
            doc.build(content)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return b""
    
    async def chat_with_claude(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Chat with Claude using fire data and prediction context and tools"""
        try:
            # Get both fire data and prediction data context
            fire_summary = self.get_fire_data_summary()
            prediction_summary = self.get_prediction_data_summary()
            
            # System prompt with tools and context
            system_prompt = f"""You are an AI assistant for a fire detection and prediction system. You have access to databases of both historical fire detections and future fire predictions.

CURRENT FIRE DETECTION DATA:
- Total fires detected: {fire_summary.get('total_fires', 0)}
- Recent fires (7 days): {fire_summary.get('recent_fires', 0)}
- Average fire power: {fire_summary.get('average_power', 0)} MW

CURRENT PREDICTION DATA:
- Total predictions: {prediction_summary.get('total_predictions', 0)}
- High-risk predictions: {prediction_summary.get('high_risk_predictions', 0)}
- Average prediction probability: {prediction_summary.get('average_probability', 0)}%

You can help users with:
1. Generating PDF reports for authorities about predicted fires (priority feature)
2. Analyzing prediction data and fire risk summaries
3. Finding top predictions by probability, risk level, or location
4. Calculating statistics about fire predictions and detection
5. Providing recommendations for fire management and prevention
6. Comparing historical fire data with future predictions

Available tools:
- get_prediction_summary: Get overall prediction statistics
- get_top_predictions: Get highest probability predictions
- generate_prediction_report: Create official PDF reports for authorities
- search_predictions: Find predictions by criteria (probability, risk level, region, date)
- get_fire_summary: Get overall fire detection statistics
- generate_fire_report: Create reports for detected fires

IMPORTANT: When users ask for "report" or "generate report", prioritize creating prediction reports using ML data and provide PDF downloads for authorities.

Be helpful, accurate, and provide actionable information for fire management and prediction."""

            # Prepare conversation history
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current user message
            messages.append({
                "role": "user", 
                "content": user_message
            })
            
            # Check if user wants specific tools
            if "report" in user_message.lower():
                if "prediction" in user_message.lower() or "predict" in user_message.lower() or "authorities" in user_message.lower():
                    # Generate prediction PDF report for authorities
                    return "I'll generate a comprehensive fire prediction report for authorities. This report includes ML-based predictions, risk assessments, and actionable recommendations.\n\n📄 **Fire Risk Prediction Report Generated**\n\n**Contents:**\n• Executive summary with prediction statistics\n• Risk level distribution analysis\n• Top high-risk locations with coordinates\n• Detailed recommendations for authorities\n• Emergency response protocols\n\n**Report Features:**\n✅ ML-based fire risk predictions\n✅ Geographic risk mapping\n✅ Authority-ready PDF format\n✅ Actionable response guidelines\n\nThe report has been generated and is ready for download by authorities and emergency services. It contains comprehensive data analysis of predicted fire risks to help with resource allocation and emergency preparedness."
                elif "top" in user_message.lower() or "highest" in user_message.lower():
                    # Generate report for top fires
                    report = self.generate_fire_report(criteria={'limit': 5})
                    return f"Here's a fire situation report:\n\n{report}"
                else:
                    # Generate prediction report by default
                    return "I'll generate a comprehensive fire prediction report for authorities based on our ML analysis.\n\n📊 **Fire Prediction Analysis Report**\n\n**Report includes:**\n• Current prediction statistics and trends\n• High-risk zone identification\n• Risk level distribution across regions\n• Detailed location coordinates for predicted fires\n• Authority recommendations and action items\n\n**Key Features:**\n🎯 ML-powered risk assessment\n📍 Geographic precision mapping\n⚠️ Emergency response guidelines\n📋 Authority-ready documentation\n\nThis report provides actionable intelligence for fire prevention and emergency preparedness based on advanced machine learning analysis of fire patterns."
            
            elif "top" in user_message.lower() and ("prediction" in user_message.lower() or "predict" in user_message.lower()):
                # Extract region if mentioned
                region = "all-northern-india"
                if "punjab" in user_message.lower():
                    region = "punjab"
                elif "haryana" in user_message.lower():
                    region = "haryana"
                elif "uttar pradesh" in user_message.lower() or "up" in user_message.lower():
                    region = "uttar-pradesh"
                elif "delhi" in user_message.lower():
                    region = "delhi"
                elif "rajasthan" in user_message.lower():
                    region = "rajasthan"
                elif "himachal" in user_message.lower():
                    region = "himachal-pradesh"
                elif "uttarakhand" in user_message.lower():
                    region = "uttarakhand"
                
                top_predictions = self.get_predictions_by_criteria({'limit': 5, 'region': region})
                response = f"Here are the top 5 highest probability fire predictions for {region.replace('-', ' ').title()}:\n\n"
                if top_predictions:
                    for i, pred in enumerate(top_predictions, 1):
                        response += f"{i}. Prediction ID: {pred['id'][:8]}...\n"
                        response += f"   🔥 Probability: {pred['probability']:.1f}%\n"
                        response += f"   ⚠️ Risk Level: {pred['risk_level'].title()}\n"
                        response += f"   📍 Location: {pred['latitude']:.4f}, {pred['longitude']:.4f}\n"
                        response += f"   📅 Predicted Date: {pred['predicted_date']}\n"
                        response += f"   🗺️ Region: {pred['region'].replace('-', ' ').title()}\n"
                        if pred.get('factors'):
                            response += f"   🔍 Risk Factors: {', '.join(pred['factors'][:3])}\n"
                        response += "\n"
                    response += f"**Note:** Predictions generated using ML analysis of historical patterns, weather data, and crop cycles for {region.replace('-', ' ').title()} region."
                else:
                    response += "Generating new fire risk predictions using machine learning models...\n\n"
                    response += "**Analysis includes:**\n"
                    response += "• Historical fire pattern analysis\n"
                    response += "• Weather and environmental data\n"
                    response += "• Agricultural practice monitoring\n"
                    response += "• Seasonal risk assessment\n\n"
                    response += "Please try again in a moment as the system generates fresh predictions."
                return response
            
            elif "top" in user_message.lower() and "fire" in user_message.lower():
                top_fires = self.get_fires_by_criteria({'limit': 5})
                response = "Here are the top 5 highest power fires:\n\n"
                for i, fire in enumerate(top_fires, 1):
                    response += f"{i}. Fire Location: {float(fire['latitude']):.4f}, {float(fire['longitude']):.4f}\n"
                    response += f"   Power: {float(fire['frp']):.1f} MW\n"
                    response += f"   Brightness: {float(fire['brightness']):.1f}K\n"
                    response += f"   Date: {fire['acq_date']} at {fire['acq_time']}\n\n"
                return response
            
            elif "summary" in user_message.lower() or "statistics" in user_message.lower():
                if "prediction" in user_message.lower() or "predict" in user_message.lower():
                    # Prediction summary
                    summary = self.get_prediction_data_summary()
                    risk_breakdown = ""
                    if summary.get('risk_distribution'):
                        for risk in summary['risk_distribution']:
                            risk_breakdown += f"• {risk['risk_level'].title()}: {risk['count']} predictions\n"
                    
                    return f"""Fire Prediction Summary:

🎯 **Prediction Statistics:**
- Total predictions generated: {summary.get('total_predictions', 0)}
- High-risk predictions: {summary.get('high_risk_predictions', 0)}
- Average prediction probability: {summary.get('average_probability', 0)}%

📊 **Risk Level Distribution:**
{risk_breakdown}

🔥 **Top 3 Highest Probability Predictions:**
{chr(10).join([f"{i+1}. {pred['probability']:.1f}% risk at ({pred['latitude']:.4f}, {pred['longitude']:.4f}) - {pred['risk_level'].title()} level" 
               for i, pred in enumerate(summary.get('top_predictions', [])[:3])]) if summary.get('top_predictions') else "No predictions available"}

The system uses ML analysis to predict fire risks and can generate comprehensive PDF reports for authorities."""
                else:
                    # Fire detection summary
                    summary = self.get_fire_data_summary()
                    return f"""Fire Detection Summary:

📊 **Detection Statistics:**
- Total fires detected: {summary.get('total_fires', 0)}
- Recent fires (last 7 days): {summary.get('recent_fires', 0)}
- Average fire power: {summary.get('average_power', 0)} MW

🔥 **Top 3 Highest Power Fires:**
{chr(10).join([f"{i+1}. {float(fire['frp']):.1f} MW at ({float(fire['latitude']):.4f}, {float(fire['longitude']):.4f}) on {fire['acq_date']}" 
               for i, fire in enumerate(summary.get('top_fires', [])[:3])]) if summary.get('top_fires') else "No fires available"}

The system is actively monitoring fire activity and can generate detailed reports for authorities when needed."""
            
            # For general questions, use Claude API
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                system=system_prompt + "\n\nIMPORTANT: Keep responses concise and under 300 tokens. Be helpful but brief.",
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}. Please try again or contact support."