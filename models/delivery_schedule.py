# models/delivery_schedule.py
from odoo import models, fields, api # type: ignore
from datetime import datetime, timedelta

class CRMLeadInherit(models.Model):
    _inherit = 'crm.lead'
    
    def calculate_next_delivery_date(self):
        """Calculate the next delivery date based on recurrence plan and day of the week."""
        for record in self:
            # Skip if required fields are missing
            if not record.x_studio_plan_recurrente or not record.x_studio_da_de_despacho:
                continue
                
            # Map Spanish day names to weekday numbers (0=Monday, 6=Sunday)
            day_mapping = {
                'lunes': 0,      # Monday
                'martes': 1,     # Tuesday
                'miercoles': 2,  # Wednesday
                'jueves': 3,     # Thursday
                'viernes': 4,    # Friday
                'sabado': 5,     # Saturday
                'domingo': 6     # Sunday
            }
            
            # Get target weekday (0-6)
            target_day = day_mapping.get(record.x_studio_da_de_despacho.lower())
            if target_day is None:
                continue
                
            # Start from today
            today = datetime.now().date()
            
            # Calculate days until the next occurrence of the target day
            days_ahead = (target_day - today.weekday()) % 7
            
            # If today is the target day and it's past noon, schedule for next week
            if days_ahead == 0 and datetime.now().hour >= 12:
                days_ahead = 7
                
            # Get the next occurrence of the specified day
            next_day = today + timedelta(days=days_ahead)
            
            # Adjust based on the recurrence plan
            recurrence_plan = record.x_studio_plan_recurrente.lower()
            if recurrence_plan == 'semanal':
                # The next occurrence is already correct (next week's specified day)
                pass
            elif recurrence_plan == 'quincenal':
                # Add another week (total of 2 weeks)
                next_day = next_day + timedelta(days=7)
            elif recurrence_plan == 'mensual':
                # Add 3 more weeks (total of 4 weeks, approximately a month)
                next_day = next_day + timedelta(days=21)
            
            # Update the record
            record.x_studio_fecha_de_prximo_pedido = next_day
    
    @api.model
    def create(self, vals):
        """Override create to calculate delivery date on new lead creation."""
        # Create the record first
        record = super(CRMLeadInherit, self).create(vals)
        
        # Calculate delivery date if the required fields are set
        if record.x_studio_plan_recurrente and record.x_studio_da_de_despacho:
            record.calculate_next_delivery_date()
            
        return record
        
    def write(self, vals):
        """Override write to recalculate delivery date when relevant fields change."""
        # Update the record first
        result = super(CRMLeadInherit, self).write(vals)
        
        # If any of the relevant fields were updated, recalculate the date
        if 'x_studio_plan_recurrente' in vals or 'x_studio_da_de_despacho' in vals:
            self.calculate_next_delivery_date()
            
        return result