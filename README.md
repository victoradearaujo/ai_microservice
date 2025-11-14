# 📘 JJungles Smart Alerts — README

## 📌 Project Description
JJungles Smart Alerts is a Python microservice built with **FastAPI** to generate intelligent alerts for sales leads.  
The service reads a `leads.csv` file, enriches each lead with computed fields (such as days since last contact and priority), and will soon include AI-generated alert messages using **Ollama** (local LLM).

---

# ✅ 1. What Has Been Completed

### ✔️ Environment Setup
- FastAPI installed and running locally  
- `/` root endpoint working (health check)  
- `/api/smart-alerts` endpoint returning enriched lead data  
- CSV successfully read and parsed  

### ✔️ Business Logic Implemented
- `compute_days_since()` to calculate time since the last interaction  
- `compute_priority()` to classify leads (High/Medium/Low)  
- Iteration through CSV using pandas  
- Enrichment of each lead with:
  - lead name  
  - last contacted date  
  - engagement score  
  - pipeline stage  
  - days since contact  
  - priority level  

### ✔️ API now reliably returns all leads (not only one)

---

# 🔧 2. Current Project Structure

project/
│── app.py
│── leads.csv
│── requirements.txt (optional)
└── README.md
