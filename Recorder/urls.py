"""
App URL Configuration
"""
from django.urls import path
from . import views

app_name = 'Recorder'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Invoice URLs
    path('', views.invoice_list, name='invoice_list'),
    path('invoice/create/', views.invoice_create, name='invoice_create'),
    path('invoice/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:pk>/update/', views.invoice_update, name='invoice_update'),
    path('invoice/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('csv/generate/', views.generate_csv, name='generate_csv'),
    path('csv/download/<str:year_month>/', views.download_csv, name='download_csv'),
    path('invoice/<int:pk>/settle-payment-1/', views.settle_payment_1, name='settle_payment_1'),
    path('invoice/<int:pk>/settle-payment-2/', views.settle_payment_2, name='settle_payment_2'),
    path('invoice/csv-upload/', views.invoice_csv_upload, name='invoice_csv_upload'),
]