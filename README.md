# Car Dealership Web Application

A Django-based web application for managing a car dealership. Users can browse, add, edit, and delete car listings, manage customer complaints, and view sales statistics through an intuitive and user-friendly interface.


## Table of Contents
- [Features](#features)
- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Contact](#contact)

## Features
- **Car Management**: Add, edit, and delete car listings with details like brand, model, price, and images.
- **Complaint Management**: Handle customer complaints efficiently.
- **Sales Statistics**: View insights and analytics on car sales.
- **User Authentication**: Secure login and registration for users and admins.
- **Responsive Design**: User-friendly interface compatible with desktop and mobile devices.
- **Search and Filtering**: Advanced search and filter options for car listings.

## Technologies
- **Python**: 3.8+
- **Django**: 5.x
- **Database**: MySQL (recommended) or SQLite (for development)
- **Pipenv**: For dependency management and virtual environment
- **Bootstrap**: For responsive front-end styling
- **Font Awesome**: For icons

## Prerequisites
Before you begin, ensure you have the following installed:
- [Python](https://www.python.org/downloads/) (version 3.8 or higher)
- [Pipenv](https://pipenv.pypa.io/en/latest/) (`pip install pipenv`)
- [MySQL](https://www.mysql.com/downloads/) (if using MySQL) or SQLite (included with Python)
- [Git](https://git-scm.com/downloads/)

## Installation
Follow these steps to set up the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/fadel-hasan/Car-Dealership.git
   cd Car-Dealership
   ```

2. **Install Pipenv** (if not already installed):
   ```bash
   pip install pipenv
   ```

3. **Set up the virtual environment and install dependencies**:
   ```bash
   pipenv install
   ```
   This will install all dependencies listed in `Pipfile`.

4. **Activate the virtual environment**:
   ```bash
   pipenv shell
   ```

5. **Set up environment variables**:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file to include your configuration (see [Environment Variables](#environment-variables) for details).

6. **Configure the database**:
   - If using **MySQL**, ensure the database is created and running. Update the database settings in `.env`.
   - If using **SQLite**, no additional setup is required (a `db.sqlite3` file will be created automatically).

7. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

8. **(Optional) Create a superuser for admin access**:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set up an admin account.

## Environment Variables
Create a `.env` file in the project root with the following variables:

```plaintext
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False in production

# Database settings (MySQL example)
DB_ENGINE=django.db.backends.mysql
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306

# Database settings (SQLite example, uncomment if using SQLite)
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3

# Other settings (optional)
ALLOWED_HOSTS=localhost,127.0.0.1
```

- **SECRET_KEY**: Generate a secure key (e.g., using `django.core.management.utils.get_random_secret_key()`).
- **DEBUG**: Set to `True` for development, `False` for production.
- **Database settings**: Configure based on whether you're using MySQL or SQLite.
- **ALLOWED_HOSTS**: Add your domain or IP in production.

## Running the Application
1. Ensure the virtual environment is activated:
   ```bash
   pipenv shell
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

4. Access the admin panel (if you created a superuser):
   ```
   http://localhost:8000/admin
   ```

## Project Structure
```
Car-Dealership/
├── .env.example          # Example environment file
├── .gitignore            # Git ignore file
├── Pipfile               # Pipenv dependency file
├── Pipfile.lock          # Locked dependency versions (optional)
├── README.md             # This file
├── manage.py             # Django management script
├── media/                # User-uploaded files (not tracked by Git)
├── static/               # Static files (CSS, JS, images)
├── carDealership/        # Main Django inner peoject
├── carDealer/            # Main Django app
│   ├── migrations/       # Database migrations
│   ├── templates/        # HTML templates
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
└── requirements.txt      # Optional, for non-Pipenv users
```

## Contact
For questions or feedback, please contact:
- **Email**: fadl.hasn.work@gmail.com
- **GitHub Issues**: [Open an issue](https://github.com/fadel-hasan/Car-Dealership/issues)
