{
    "name": "JJ Smart Alerts",
    "version": "1.0",
    "summary": "Alert management integration for Odoo",
    "description": "This module integrates JJ Smart Alerts with Odoo to manage and send IA alerts efficiently with FastAPI.",
    "author": "Victor Araujo",
    "website": "https://github.com/victoradearaujo/ai_microservice",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "views/smart_alerts_views.xml",
        "data/cron_job.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": True

}