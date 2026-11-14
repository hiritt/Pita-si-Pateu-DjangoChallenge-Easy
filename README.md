## Installation and Setup

### Requirements

- Python 3.15
- Git (to clone the repository)

### 1. Clone the repository

```powershell
git clone https://github.com/hiritt/Pita-si-Pateu-DjangoChallenge-Easy.git
cd Pita-si-Pateu-DjangoChallenge-Easy
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Install the dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Set up the database

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

### 5. Run automated tests

```powershell
.\.venv\Scripts\python.exe manage.py test
```

### 6. Start the application

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

### 7. Open the application

- Add fighters: http://127.0.0.1:8000/unit
- View fighters and simulate battles: http://127.0.0.1:8000/unit/all

Press `Ctrl + C` in the terminal to stop the server.

## Notes

The application uses SQLite. Database tables are created automatically through Django migrations.

The project is configured for local development, not production deployment.
