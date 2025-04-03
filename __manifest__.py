{
    'name': 'Delivery Schedule',
    'version': '1.0',
    'summary': 'Calculate next delivery dates based on recurrence plans',
    'description': """
        This module extends CRM to calculate next delivery dates based on 
        recurrence plans (weekly, biweekly, monthly) and preferred delivery days.
    """,
    'category': 'Sales/CRM',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['crm', 'sale'],
    'data': [
        'views/delivery_schedule_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}