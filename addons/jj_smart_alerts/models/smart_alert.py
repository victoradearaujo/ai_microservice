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
        # Alerts from the FastAPI endpoint and create/update records

        url = "http://host.docker.internal:8000/api/smart-alerts"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            alerts = response.json()

            for alert in alerts:

                lead_name = alert.get('lead')
                alert_message = alert.get('alert')
                priority = alert.get('priority', 'low')
                timestamp = datetime.now()

                # Prevent duplicates
                existing = self.search([
                    ('name', '=', lead_name),
                    ('alert_message', '=', alert_message),
                ], limit=1)

                if existing:
                    _logger.info(f"Alert already exists for lead: {lead_name}")
                    continue

                # Create new alert
                self.create({
                    'name': lead_name,
                    'alert_message': alert_message,
                    'priority': priority.lower(),
                    'timestamp': timestamp,
                })

            return True

        except Exception as e:
            _logger.error(f"Error calling Smart Alerts API: {e}")
            return False
