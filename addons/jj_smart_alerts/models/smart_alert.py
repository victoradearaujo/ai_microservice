from odoo import models, fields
import requests
from datetime import datetime

class JJSmartAlert(models.Model):
    _name = "jj.smart.alert"
    _description = "Smart Alerts from FastAPI"

    name = fields.Char(string="Alert Title", required=True)
    alert_message = fields.Text(string="Message")
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Priority", default='low')
    state = fields.Selection([
        ('new', 'New'),
        ('read', 'Read')
    ], string="State", default='new')
    timestamp = fields.Datetime(string="Timestamp", default=fields.Datetime.now)

    def fetch_from_api(self):
        
        #Fetch alerts from the FastAPI endpoint and create records in Odoo.
      
        url = "http://host.docker.internal:8000/api/smart-alerts"
        try:
            response = requests.get(url)
            response.raise_for_status()  
            alerts = response.json()     

            for alert in alerts:
                # create a new record for each alert
                self.create({
                    'name': alert.get('name'),
                    'alert_message': alert.get('message'),
                    'priority': alert.get('priority', 'low'),
                    'timestamp': alert.get('timestamp', datetime.now().isoformat())
                })

        except Exception as e:
            # Log the error in Odoo's logging system
            _logger = self.env['ir.logging']
            _logger.create({
                'name': 'Smart Alerts API',
                'type': 'server',
                'level': 'error',
                'message': str(e),
                'path': 'jj.smart.alert',
                'func': 'fetch_from_api',
            })
