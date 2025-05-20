# Invoice Manager

A Django-based web application for managing invoices and generating Excel reports.

## Features

- User Authentication (Register, Login, Logout)
- Create, Read, Update, and Delete Invoices
- Generate Excel Reports for Monthly Invoices
- Automatic Payment Calculations
- Responsive Bootstrap UI
- User-friendly Forms with Date Pickers

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Excel_Record
```

2. Create and activate a virtual environment:

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Create necessary directories:
```bash
mkdir -p media/invoice_excel
```

## Configuration

1. Create a `.env` file in the project root:
```bash
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

2. Update settings if needed in `Excel_Record/settings.py`

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Access the application:
- Main application: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

## Usage

1. Register a new account or login with existing credentials
2. Navigate to "New Invoice" to create invoices
3. View all invoices in the list view
4. Generate Excel reports for monthly invoices
5. Download generated Excel reports

## Project Structure

```
Excel_Record/
├── Excel_Record/          # Project settings
├── Recorder/             # Main application
│   ├── migrations/      # Database migrations
│   ├── templates/      # HTML templates
│   ├── forms.py       # Form definitions
│   ├── models.py      # Database models
│   ├── urls.py        # URL configurations
│   └── views.py       # View logic
├── media/              # User uploaded files
│   └── invoice_excel/  # Generated Excel files
├── static/             # Static files
├── templates/          # Global templates
├── manage.py          # Django management script
├── requirements.txt   # Project dependencies
└── README.md         # Project documentation
```

## Security Considerations

1. Keep your SECRET_KEY secure and never commit it to version control
2. Use strong passwords for user accounts
3. Regular database backups are recommended
4. Keep Django and all dependencies updated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 