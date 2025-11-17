from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse
from datetime import datetime
import ollama 
import os 
import logging 
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List 


# Infos about the API
app = FastAPI(
    title = "JJungles Smart Alerts - AI Microservice",
    version = "1.0.0"
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Response model (pydantic)
class LeadAlert(BaseModel):
    lead_name: str
    last_contacted: str
    engagement_score: int
    stage: str
    days_since_last_contacted: int
    priority: str
    ai_alert: str
    error: Optional[str] = None
#Response Model List 
class SmartAlertsResponse(BaseModel):
    alerts: List[LeadAlert]

# Validate CSV File (exists file, read, pandasDF, HTTPEexception)
def load_leads_csv(filename: str = "leads.csv"):
     
    # Path relative to app.py (define base directory)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, filename)

    # Check if file exists (if not, log error and raise HTTPException)
    if not os.path.exists(csv_path):
        logging.error(f"CSV file not found at path: {csv_path}")
        raise HTTPException(status_code=404, detail="Leads CSV file not found.")

    # Try to read CSV file into a pandas DataFrame(except log error and raise HTTPException)
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        raise HTTPException(status_code=400, detail=f"Error reading {filename} CSV file.")

    # Validate required columns in CSV file (except log error and raise HTTPException)
    required_columns = {"lead_name", "last_contacted", "engagement_score", "stage"}
    missing = required_columns - set(df.columns)

    if missing: 
        logging.error(f"CSV file is missing required columns: {missing}")
        raise HTTPException(status_code=400, detail=f"Missing columns in {filename}: {sorted(list(missing))} CSV file.")
    
    # If all validations pass, return the DataFrame
    return df


# Rule to identify leads not contacted in the last 30 days
def compute_days_since(last_contacted_str: str) -> int:
    last_contacted = datetime.strptime(last_contacted_str, "%Y-%m-%d")
    delta = datetime.now() - last_contacted
    return delta.days

# Rule to identify the priority of the lead based on engagement score and delta days 
def compute_priority(engagement_score: int, delta_days: int) -> str:
    if engagement_score <30 and delta_days >14:
        return "High Priority"
    elif engagement_score >30 or delta_days >=14:
        return "Medium Priority"
    else:
        return "Low Priority"
    
# Initialize Ollama model (LLM integration)
def generate_ai_alert(lead_name: str, engagement_score: int, days_since_last_contacted: int, stage: str) -> str:

    prompt = (f"""
    You are a sales assistant. Based on the following lead information, generate a smart short alert message(1-2 sentences):
    Lead Name: {lead_name}
    Engagement Score: {engagement_score}
    Days Since Last Contacted: {days_since_last_contacted}
    Stage: {stage}
    
    Provide a concise alert message.
    """
    )

    response = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# Test load endpoint to validate CSV loading 
@app.get("/api/test-load")
def test_load():
    df = load_leads_csv()   
    return {"rows": df.head().to_dict(orient="records")}

# Root endpoint to check if the API is running
@app.get("/")
def root():
    return {"message": "JJungles Smart Alerts API is running"}

# Endpoint to get smart alerts data
@app.get("/api/smart-alerts", response_model=SmartAlertsResponse)
async def get_smart_alerts():
        # Log the request
        logging.info("Received request for smart alerts")

        # Load the leads CSV file
        try:
            df = load_leads_csv()
        except Exception as e:
            logging.error(f"Error loading leads CSV file: {e}")
            raise HTTPException(status_code=500, detail="Error loading leads CSV file")
        logging.info(f"Loaded {len(df)} leads from CSV file")

        enriched = [] # List to hold enriched lead data
         
        for idx, row in df.iterrows():
            try:
                lead_name = row.get("lead_name", "Unknown")
                logging.info(f"Processing lead: {lead_name}")

                # Calculations
                days = compute_days_since(str(row["last_contacted"]))
                engagement = int(row["engagement_score"])
                priority = compute_priority(engagement, days)

                # Generate AI alert
                ai_text = generate_ai_alert(
                    lead_name=row["lead_name"],
                    days_since_last_contacted=days,
                    engagement_score=engagement,
                    stage=row["stage"]
                )

                enriched.append({
                "lead_name": row["lead_name"],
                "last_contacted": row["last_contacted"],
                "engagement_score": row["engagement_score"],
                "stage": row["stage"],
                "days_since_last_contacted": days,
                "priority": priority,
                "ai_alert": ai_text
            })

            except Exception as e:
                logging.exception(f"Error processing lead at row {idx}: {e}")
                enriched.append({
                     "lead_name": row.get("lead_name", f"Row {idx}"),
                    "last_contacted": "",
                    "engagement_score": 0,
                    "stage": "",
                    "days_since_last_contacted": 0,
                    "priority": "Unknown",
                    "ai_alert": "",
                     "error": f"Could not process lead: {str(e)}"
         })

        logging.info("Completed processing all leads")
        return SmartAlertsResponse(alerts=enriched)
