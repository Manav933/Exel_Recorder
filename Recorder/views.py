import os
import csv
import calendar
from datetime import datetime, date
import xlsxwriter
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .models import Invoice
from .forms import InvoiceForm, UserRegistrationForm, UserLoginForm

def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('Recorder:invoice_list')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(
                    request, 
                    'Registration successful! Please login with your credentials.'
                )
                return redirect('Recorder:login')
            except Exception as e:
                messages.error(request, f'Error during registration: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'Recorder/auth/register.html', {'form': form})

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('Recorder:invoice_list')
        
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                # Redirect to next page if specified, otherwise to invoice list
                next_page = request.GET.get('next')
                return redirect(next_page if next_page else 'Recorder:invoice_list')
    else:
        form = UserLoginForm()
    
    return render(request, 'Recorder/auth/login.html', {'form': form})

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('Recorder:login')

# Add login_required decorator to all views that need authentication
@login_required(login_url='Recorder:login')
def invoice_list(request):
    """
    Display all invoices with pagination and filtering options
    Allow generating and downloading monthly Excel files
    """
    # Get all invoices ordered by created date for the current user
    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
    
    # Get unique months from invoices for filtering
    months = {}
    for invoice in Invoice.objects.filter(user=request.user).dates('created_at', 'month'):
        month_year = invoice.strftime('%Y-%m')
        month_name = invoice.strftime('%B %Y')
        months[month_year] = month_name
    
    # Filter by month if requested
    month_filter = request.GET.get('month')
    if month_filter:
        year, month = month_filter.split('-')
        invoices = invoices.filter(created_at__year=year, created_at__month=month)
    
    # Paginate results
    paginator = Paginator(invoices, 10)  # Show 10 invoices per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Store current filter in session
    request.session['current_month_filter'] = month_filter
    
    context = {
        'page_obj': page_obj,
        'months': months,
        'current_month': month_filter,
    }
    return render(request, 'Recorder/invoice_list.html', context)

@login_required(login_url='Recorder:login')
def invoice_create(request):
    """Create a new invoice"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            # Get form data
            invoice = form.save(commit=False)
            invoice.user = request.user
            
            # Calculate payment_2 if not provided
            if not invoice.payment_2:
                invoice.payment_2 = invoice.calculate_payment_2()
                
            # Save the invoice
            invoice.save()
            
            # Store in session that a new invoice was added this month
            month_year = invoice.created_at.strftime('%Y-%m')
            request.session[f'invoice_added_{month_year}'] = True
            
            messages.success(request, 'Invoice created successfully!')
            
            # If user wants to add another invoice, redirect to empty form
            if 'save_and_add' in request.POST:
                # Save some form data in session for convenience
                request.session['last_firm'] = invoice.firm
                request.session['last_quality'] = invoice.quality
                return redirect('Recorder:invoice_create')
            
            return redirect('Recorder:invoice_list')
    else:
        # Pre-fill some fields from session if available
        initial_data = {}
        if 'last_firm' in request.session:
            initial_data['firm'] = request.session.get('last_firm')
        if 'last_quality' in request.session:
            initial_data['quality'] = request.session.get('last_quality')
            
        form = InvoiceForm(initial=initial_data)
    
    context = {'form': form, 'is_create': True}
    return render(request, 'Recorder/invoice_form.html', context)

@login_required(login_url='Recorder:login')
def invoice_update(request, pk):
    """Update an existing invoice"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            # Get form data
            invoice = form.save(commit=False)
            
            # Calculate payment_2
            invoice.payment_2 = invoice.calculate_payment_2()
            
            # Save the invoice
            invoice.save()
            
            messages.success(request, 'Invoice updated successfully!')
            return redirect('Recorder:invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    
    context = {'form': form, 'is_create': False, 'invoice': invoice}
    return render(request, 'Recorder/invoice_form.html', context)

@login_required(login_url='Recorder:login')
def invoice_delete(request, pk):
    """Delete an invoice"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    if request.method == 'POST':
        month_year = invoice.created_at.strftime('%Y-%m')
        invoice.delete()
        messages.success(request, 'Invoice deleted successfully!')
        
        # Check if this was the last invoice for this month
        remaining = Invoice.objects.filter(
            user=request.user,
            created_at__year=invoice.created_at.year, 
            created_at__month=invoice.created_at.month
        ).count()
        
        if remaining == 0:
            # Clean up any monthly Excel file
            try:
                excel_path = os.path.join(settings.INVOICE_EXCEL_DIR, f'invoices_{month_year}_{request.user.id}.xlsx')
                if os.path.exists(excel_path):
                    os.remove(excel_path)
            except Exception as e:
                messages.error(request, f'Error cleaning up Excel file: {str(e)}')
        
        return redirect('Recorder:invoice_list')
    
    context = {'invoice': invoice}
    return render(request, 'Recorder/invoice_confirm_delete.html', context)

@login_required(login_url='Recorder:login')
def invoice_detail(request, pk):
    """Show invoice details"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    # Initialize default values
    days_diff = None
    days_minus_dhara = None
    payment_2 = None
    
    # Calculate the difference in days between payment_date_1 and invoice_date
    if invoice.payment_date_1 and invoice.invoice_date:
        days_diff = (invoice.payment_date_1 - invoice.invoice_date).days
        
        # Calculate days_minus_dhara only if dhara_day is provided
        if invoice.dhara_day is not None:
            days_minus_dhara = days_diff - invoice.dhara_day
            
            # Calculate payment_2 using your formula
            if invoice.payment_1:
                payment_2 = (invoice.payment_1 / Decimal('1.05')) * Decimal('0.0004931507') * days_minus_dhara
    
    context = {
        'invoice': invoice,
        'days_diff': days_diff,
        'days_minus_dhara': days_minus_dhara,
        'payment_2': payment_2,
    }
    return render(request, 'Recorder/invoice_detail.html', context)

@login_required(login_url='Recorder:login')
def generate_excel(request):
    """Generate Excel file for the current month or specified month"""
    # Get month from form or use current month
    month_filter = request.GET.get('month')
    if not month_filter:
        month_filter = timezone.now().strftime('%Y-%m')
    
    month, year = month_filter.split('-')
    
    # Get invoices for the specified month for the current user
    invoices = Invoice.objects.filter(
        user=request.user,
        created_at__year=year, 
        created_at__month=month
    ).order_by('invoice_date')
    
    if not invoices:
        messages.warning(request, f'No invoices found for {calendar.month_name[int(month)]} {year}')
        return redirect('Recorder:invoice_list')
    
    # Create Excel file
    try:
        # Include user ID in filename to keep files separate
        excel_path = os.path.join(settings.INVOICE_EXCEL_DIR, f'invoices_{year}-{month}_{request.user.id}.xlsx')
        
        # Create Excel workbook
        workbook = xlsxwriter.Workbook(excel_path)
        worksheet = workbook.add_worksheet('Invoices')
        
        # Add header formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'color': 'white',
            'border': 1,
            'align': 'center',
        })
        
        # Define columns
        columns = [
            'Firm', 'Quality', 'Invoice Date', 'Invoice Number', 'Party', 
            'Total Amount', 'Due Date', 'Balance', 'Payment Date 1', 
            'Payment 1', 'Dhara Day', 'Taka', 'Payment Date 2', 'Payment 2'
        ]
        
        # Write headers
        for col_num, column_title in enumerate(columns):
            worksheet.write(0, col_num, column_title, header_format)
        
        # Row styling
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        
        def date_to_datetime(d):
            """Convert date object to datetime object"""
            if isinstance(d, date):
                return datetime.combine(d, datetime.min.time())
            return d
        
        # Write data rows
        for row_num, invoice in enumerate(invoices, 1):
            worksheet.write(row_num, 0, invoice.firm)
            worksheet.write(row_num, 1, invoice.quality)
            worksheet.write_datetime(row_num, 2, date_to_datetime(invoice.invoice_date), date_format)
            worksheet.write(row_num, 3, invoice.invoice_number)
            worksheet.write(row_num, 4, invoice.party)
            worksheet.write_number(row_num, 5, float(invoice.total_amount), money_format)
            worksheet.write_datetime(row_num, 6, date_to_datetime(invoice.due_date), date_format)
            worksheet.write_number(row_num, 7, float(invoice.balance), money_format)
            worksheet.write_datetime(row_num, 8, date_to_datetime(invoice.payment_date_1), date_format)
            worksheet.write_number(row_num, 9, float(invoice.payment_1), money_format)
            worksheet.write_number(row_num, 10, invoice.dhara_day)
            worksheet.write_number(row_num, 11, float(invoice.taka), money_format)
            if invoice.payment_date_2:
                worksheet.write_datetime(row_num, 12, date_to_datetime(invoice.payment_date_2), date_format)
            else:
                worksheet.write(row_num, 12, '')  # Write empty cell if payment_date_2 is None
            worksheet.write_number(row_num, 13, float(invoice.payment_2 or 0), money_format)
        
        # Add summary row
        total_row = row_num + 2
        worksheet.write(total_row, 4, 'TOTAL:', header_format)
        worksheet.write_formula(total_row, 5, f'=SUM(F2:F{row_num+1})', money_format)
        worksheet.write_formula(total_row, 7, f'=SUM(H2:H{row_num+1})', money_format)
        worksheet.write_formula(total_row, 9, f'=SUM(J2:J{row_num+1})', money_format)
        worksheet.write_formula(total_row, 11, f'=SUM(L2:L{row_num+1})', money_format)
        worksheet.write_formula(total_row, 13, f'=SUM(N2:N{row_num+1})', money_format)
        
        # Auto-size columns
        for col_num, _ in enumerate(columns):
            worksheet.set_column(col_num, col_num, 15)
        
        workbook.close()
        
        # Store in session that the file was generated
        request.session[f'excel_generated_{year}-{month}'] = True
        
        # Record the last generated month
        request.session['last_generated_month'] = f'{year}-{month}'
        
        messages.success(request, f'Excel file for {calendar.month_name[int(month)]} {year} generated successfully')
        
        # Redirect to download
        return redirect('Recorder:download_excel', year_month=f'{year}-{month}')
        
    except Exception as e:
        messages.error(request, f'Error generating Excel: {str(e)}')
        return redirect('Recorder:invoice_list')

@login_required(login_url='Recorder:login')
def download_excel(request, year_month):
    """Download the Excel file for a specific month"""
    try:
        year, month = year_month.split('-')
        file_path = os.path.join(settings.INVOICE_EXCEL_DIR, f'invoices_{year_month}.xlsx')
        
        if not os.path.exists(file_path):
            # Try to generate the file if it doesn't exist
            return redirect('Recorder:generate_excel')
        
        with open(file_path, 'rb') as excel_file:
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="invoices_{year_month}.xlsx"'
            return response
            
    except Exception as e:
        messages.error(request, f'Error downloading Excel: {str(e)}')
        return redirect('Recorder:invoice_list')

@login_required(login_url='Recorder:login')
def settle_payment_1(request, pk):
    """Handle Payment 1 settlement"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Update balance by subtracting payment_1
        invoice.balance -= invoice.payment_1
        invoice.save()
        messages.success(request, 'Payment 1 has been settled successfully!')
        return redirect('Recorder:invoice_detail', pk=pk)
    
    return redirect('Recorder:invoice_detail', pk=pk)

@login_required(login_url='Recorder:login')
def settle_payment_2(request, pk):
    """Handle Payment 2 settlement and invoice deletion"""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Delete the invoice
        invoice.delete()
        messages.success(request, 'Payment 2 has been settled and invoice has been deleted!')
        return redirect('Recorder:invoice_list')
    
    return redirect('Recorder:invoice_detail', pk=pk)