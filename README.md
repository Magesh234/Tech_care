Hospital Management System
A comprehensive web application for hospital management with a Django backend and React frontend.

Project Overview
This Hospital Management System is designed to streamline hospital operations, manage patient records, schedule appointments, and handle administrative tasks. The application features a responsive user interface built with React and a robust Django backend for data management and business logic.

Tech Stack

Backend
Django: Python web framework
Django REST Framework: For API development
SQLite (development) / MySQL (production)

Frontend
React: JavaScript library for building user interfaces
Vite: Next-generation frontend tooling
CSS: For styling components


Project Structure
├── backend/                # Django backend
│   ├── app/                # Main Django application
│   ├── hospital_backend/   # Django project settings
│   ├── manage.py           # Django command-line utility
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # React frontend
    ├── public/             # Static assets
    ├── src/                # Source code
    │   ├── assets/         # Images, fonts, etc.
    │   ├── components/     # React components
    │   ├── App.jsx         # Main application component
    │   └── main.jsx        # Entry point
    └── package.json        # NPM dependencies


Backend Setup

Navigate to the backend directory:
cd backend
Create and activate a virtual environment (optional if you're using the existing venv):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt
Set up the database:

python manage.py migrate
Create a superuser:
python manage.py createsuperuser

Start the development server:
python manage.py runserver

Frontend Setup
Navigate to the frontend directory:
cd frontend
Install dependencies:
npm install
Start the development server:
npm run dev


Contributing
Clone the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)


