from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse
from datetime import datetime
import ollama 

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
    
# Initialize Ollama model
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
    

    response = client.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


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
        
        client = ollama.Chat()

        for _,row in df.iterrows():
             days = compute_days_since(str(row["last_contacted"]))
             engagement = int(row["engagement_score"])
             priority = compute_priority(engagement, days)

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
             
        return enriched
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"ERROR": "leads.csv file not found or invalid format."})
    

