# AISolution - Django Project

## Overview
AISolution is a Django-based web application designed to facilitate document management and RAG-based Q&A solutions using AI models. This documentation provides guidance on setting up, installing dependencies, and running the Django development server, along with details on authentication, document ingestion, chat session management, and WebSocket communication.

## Prerequisites

Before you start, make sure you have the following installed:
- Python (version 3.8 or higher)
- pip (Python package installer)
- Virtualenv (for creating isolated Python environments)
- Git (if cloning the repository)

## Setting Up the Development Environment

### 1. Clone the Repository
If you haven't already, clone the project from your repository:
```bash
git clone https://github.com/Sushil2308/qna
cd aisolution
```

### 2. Set Up a Virtual Environment
It is recommended to use a virtual environment to manage dependencies:
```bash
python -m venv venv
```

Activate the virtual environment:
- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
Install the required dependencies using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Set Up the Database
Run the Django migrations to set up the database:
```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)
To create a superuser for accessing the Django admin interface:
```bash
python manage.py createsuperuser --username admin --email admin@example.com
```
Follow the prompts to create your superuser account.

## Running the Development Server

To start the Django development server, run the following command:
```bash
python manage.py runserver
```

This will start the development server at `http://127.0.0.1:8000/`. You can access your application through this URL.