# models/delivery_schedule.py
from odoo import models, fields, api # type: ignore
from datetime import datetime, timedelta

class CRMLeadInherit(models.Model):
    _inherit = 'crm.lead'
    
    def calculate_next_delivery_date(self, force_recalculation=False):
        """
        Calculate the next delivery date based on recurrence plan and day of the week.
        
        Args:
            force_recalculation: When True, recalculates even if the next delivery date 
                                is not today (used for manual button clicks)
        """
        today = fields.Date.today()
        
        for record in self:
            # Skip if required fields are missing
            if not record.x_studio_plan_recurrente or not record.x_studio_da_de_despacho:
                continue
                
            # Skip if the existing next delivery date is not today
            # Unless force_recalculation is True (manual button click)
            if not force_recalculation and record.x_studio_fecha_de_prximo_pedido and record.x_studio_fecha_de_prximo_pedido != today:
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
            current_date = datetime.now().date()
            
            # Calculate days until the next occurrence of the target day
            days_ahead = (target_day - current_date.weekday()) % 7
            
            # If today is the target day and it's past noon, schedule for next week
            if days_ahead == 0 and datetime.now().hour >= 12:
                days_ahead = 7
                
            # Get the next occurrence of the specified day (without adding extra weeks)
            next_day = current_date + timedelta(days=days_ahead)
            
            # If this is not a forced recalculation and we have an existing date,
            # apply the recurrence pattern from that date instead
            if not force_recalculation and record.x_studio_fecha_de_prximo_pedido:
                # Apply recurrence pattern from the existing date
                start_date = record.x_studio_fecha_de_prximo_pedido
                
                # Calculate the next date based on recurrence plan
                recurrence_plan = record.x_studio_plan_recurrente.lower()
                if recurrence_plan == 'semanal':
                    next_day = start_date + timedelta(days=7)
                elif recurrence_plan == 'quincenal':
                    next_day = start_date + timedelta(days=14)
                elif recurrence_plan == 'mensual':
                    next_day = start_date + timedelta(days=28)
            
            # Update the record
            record.x_studio_fecha_de_prximo_pedido = next_day
    
    # Method specifically for the button to force recalculation
    def button_calculate_next_delivery_date(self):
        """Button method to force recalculation of the next delivery date."""
        return self.calculate_next_delivery_date(force_recalculation=True)
    
    @api.model
    def create(self, vals):
        """Override create to calculate delivery date on new lead creation."""
        # Create the record first
        record = super(CRMLeadInherit, self).create(vals)
        
        # Calculate delivery date if the required fields are set
        if record.x_studio_plan_recurrente and record.x_studio_da_de_despacho:
            record.calculate_next_delivery_date(force_recalculation=True)
            
        return record
        
    def write(self, vals):
        """Override write to recalculate delivery date when relevant fields change."""
        # Update the record first
        result = super(CRMLeadInherit, self).write(vals)
        
        # If any of the relevant fields were updated, recalculate the date
        if 'x_studio_plan_recurrente' in vals or 'x_studio_da_de_despacho' in vals:
            self.calculate_next_delivery_date(force_recalculation=True)
            
        return result