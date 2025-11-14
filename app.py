from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse
from datetime import datetime

# Infos about the API
app = FastAPI(
    title = "JJungles Smart Alerts - AI Microservice",
    version = "1.0.0"
)

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
    
# Root endpoint to check if the API is running
@app.get("/")
def root():
    return {"message": "JJungles Smart Alerts API is running"}

# Endpoint to get smart alerts data
@app.get("/api/smart-alerts")
def get_smart_alerts():
    try:
        df = pd.read_csv("leads.csv")
        
        enriched = [] # List to hold enriched lead data
        
        for _,row in df.iterrows():
             days = compute_days_since(str(row["last_contacted"]))
             engagement = int(row["engagement_score"])
             priority = compute_priority(engagement, days)
             
             enriched.append({
                 "lead_name": row["lead_name"],
                 "last_contacted": row["last_contacted"],
                 "engagement_score": row["engagement_score"],
                 "stage": row["stage"],
                 "days_since_last_contacted": days,
                    "priority": priority
                })
        return enriched
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"ERROR": "leads.csv file not found or invalid format."})
    
    
