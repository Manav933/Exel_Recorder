from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    firm = models.CharField(max_length=255)
    quality = models.CharField(max_length=255)
    invoice_date = models.DateField()
    invoice_number = models.CharField(max_length=100)
    party = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date_1 = models.DateField()
    payment_1 = models.DecimalField(max_digits=15, decimal_places=2)
    dhara_day = models.IntegerField()
    taka = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date_2 = models.DateField(null=True, blank=True)
    payment_2 = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    settled_payment_2 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    @property
    def month_year(self):
        """Return month and year as a string for grouping invoices by month."""
        return self.created_at.strftime('%Y-%m')
    
    @property
    def payment_status(self):
        """Return the payment settlement status of the invoice."""
        if self.balance == 0 and self.settled_payment_2:
            return 'both_settled'
        elif self.balance == 0:
            return 'payment_1_settled'
        else:
            return 'pending'
    
    def calculate_payment_2(self):
        """Calculate payment 2 based on the formula."""
        if self.settled_payment_2:
            return Decimal('0.00')
            
        if not all([self.payment_date_1, self.invoice_date, self.dhara_day, self.payment_1]):
            return 0
            
        # Calculate days difference
        days_diff = (self.payment_date_1 - self.invoice_date).days
        
        # Calculate Payment 2 based on the formula
        if self.dhara_day < days_diff:
            interest_factor = (self.payment_1 / Decimal('1.05')) * (Decimal('0.0004931507') * (days_diff - self.dhara_day))
            return Decimal(interest_factor)
            
    def save(self, *args, **kwargs):
        # Calculate payment_2 before saving if not settled
        if not self.settled_payment_2:
            self.payment_2 = self.calculate_payment_2()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.party}"