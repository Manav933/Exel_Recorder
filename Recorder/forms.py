from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Invoice

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class InvoiceForm(forms.ModelForm):
    invoice_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d'}),
        input_formats=['%Y-%m-%d']
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d'}),
        input_formats=['%Y-%m-%d']
    )
    payment_date_1 = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d'}),
        input_formats=['%Y-%m-%d'],
        required=False
    )
    payment_date_2 = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d'}),
        input_formats=['%Y-%m-%d'],
        required=False
    )
    payment_1 = forms.DecimalField(max_digits=15, decimal_places=2, required=False)
    
    class Meta:
        model = Invoice
        fields = [
            'firm', 'quality', 'invoice_date', 'invoice_number', 
            'party', 'meter', 'total_amount', 'due_date', 'balance', 
            'payment_date_1', 'payment_1', 'dhara_day', 'taka', 
            'payment_date_2'
        ]
        # Exclude payment_2 as it's calculated automatically
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if isinstance(field, forms.DateField):
                field.widget.attrs['data-date-format'] = 'yyyy-mm-dd'