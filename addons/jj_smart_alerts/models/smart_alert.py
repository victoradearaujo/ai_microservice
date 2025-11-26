from odoo import models, fields, api
import requests
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class JJSmartAlert(models.Model):
    _name = "jj.smart.alert"
    _description = "Smart Alerts from FastAPI"

    name = fields.Char(string="Lead", required=True)
    alert_message = fields.Text(string="Alert Message")
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string="Priority", default='low')
    state = fields.Selection([
        ('new', 'New'),
        ('read', 'Read'),
    ], string="State", default='new')
    timestamp = fields.Datetime(string="Generated At", default=fields.Datetime.now)

    @api.model
    def fetch_from_api(self):
        url = "http://host.docker.internal:8000/api/smart-alerts"

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            data = response.json()
            alerts = data.get("alerts", [])

            for alert in alerts:
                lead_name = alert.get("lead_name")
                alert_message = alert.get("ai_alert")
                priority_raw = alert.get("priority", "Low Priority")

                # Normalize priority to: low / medium / high
                priority = "low"
                if "medium" in priority_raw.lower():
                    priority = "medium"
                elif "high" in priority_raw.lower():
                    priority = "high"

                timestamp = datetime.now()

                # Check if an alert for this lead already exists
                existing = self.search([('name', '=', lead_name)], limit=1)

                if existing:
                    _logger.info(f"Updating existing alert for lead: {lead_name}")
                    # Update the existing alert
                    existing.write({
                        'alert_message': alert_message,
                        'priority': priority,
                        'timestamp': timestamp,
                    })
                else:
                    # Create new alert if lead doesn't exist
                    self.create({
                        'name': lead_name,
                        'alert_message': alert_message,
                        'priority': priority,
                        'timestamp': timestamp,
                    })

            return True

        except Exception as e:
            _logger.error(f"Error calling Smart Alerts API: {e}")
            return False
