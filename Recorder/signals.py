from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Invoice

@receiver(post_save, sender=Invoice)
def mark_invoice_added(sender, instance, created, **kwargs):
    """
    When an invoice is created or updated, mark that there's a new invoice this month.
    This will be used by the middleware to suggest generating an Excel file.
    """
    from django.core.cache import cache
    
    # Get the month-year from the instance
    month_year = instance.created_at.strftime('%Y-%m')
    
    # Store in cache that a new invoice was added for this month
    cache_key = f'invoice_added_{month_year}'
    cache.set(cache_key, True, 60*60*24*7)  # Cache for a week
    
    # If there's an existing Excel file for this month, mark it as outdated
    cache.set(f'excel_file_outdated_{month_year}', True, 60*60*24*7)

@receiver(post_delete, sender=Invoice)
def mark_invoice_deleted(sender, instance, **kwargs):
    """
    When an invoice is deleted, mark that the Excel file for this month is outdated.
    """
    from django.core.cache import cache
    
    # Get the month-year from the instance
    month_year = instance.created_at.strftime('%Y-%m')
    
    # Mark any existing Excel file for this month as outdated
    cache.set(f'excel_file_outdated_{month_year}', True, 60*60*24*7)