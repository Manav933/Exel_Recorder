from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'party', 'firm', 'invoice_date', 'total_amount', 'balance', 'payment_2')
    list_filter = ('firm', 'invoice_date', 'created_at')
    search_fields = ('invoice_number', 'party', 'firm')
    readonly_fields = ('payment_2', 'created_at', 'updated_at')
    date_hierarchy = 'invoice_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('firm', 'quality', 'invoice_date', 'invoice_number', 'party')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'due_date', 'balance')
        }),
        ('Payment Information', {
            'fields': ('payment_date_1', 'payment_1', 'dhara_day', 'taka', 'payment_date_2', 'payment_2')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        # Calculate payment_2 when saving through admin
        if not obj.payment_2:
            obj.payment_2 = obj.calculate_payment_2()
        super().save_model(request, obj, form, change)