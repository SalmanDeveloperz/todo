# Daymark Todo App

A FastAPI todo application with MySQL, user authentication, and a browser-based task dashboard.

## Requirements

Install these first:

- Python 3.11 or newer
- MySQL Server
- Git

The commands below are written for Windows PowerShell.

## 1. Get the project

If you have not cloned the repository:

```powershell
git clone https://github.com/SalmanDeveloperz/todo.git todoApp
cd todoApp
```

The application imports the project as the `todoApp` package. Therefore, the folder must be named `todoApp`, and Uvicorn must be started from its parent directory.

Expected structure:

```text
parent-folder/
└── todoApp/
    ├── main.py
    ├── database.py
    ├── models.py
    ├── routers/
    ├── templates/
    ├── static/
    └── requirements.txt
```

If the repository is already on your computer at `C:\Users\salman\Documents\fastvenv\todoApp`, skip cloning and use that path in the commands below.

## 2. Create the MySQL database

Open MySQL Workbench or the MySQL command line and run:

```sql
CREATE DATABASE TodoApplicationDatabase
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

The current local configuration expects:

```text
Host: 127.0.0.1
Port: 3306
Database: TodoApplicationDatabase
Username: root
Password: salman123
```

If your MySQL username or password is different, set `DATABASE_URL` before starting the application instead of editing Python code:

```powershell
$env:DATABASE_URL = "mysql+pymysql://USERNAME:PASSWORD@127.0.0.1:3306/TodoApplicationDatabase?charset=utf8mb4"
```

## 3. Create and activate a virtual environment

Run these commands from the directory containing the `todoApp` folder:

```powershell
cd C:\Users\salman\Documents\fastvenv
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in an Administrator PowerShell window:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

From the same directory:

```powershell
python -m pip install --upgrade pip
python -m pip install -r .\todoApp\requirements.txt
```

If you are using the existing virtual environment from this workspace, use its interpreter directly:

```powershell
.\fastvenv\Scripts\python.exe -m pip install -r .\todoApp\requirements.txt
```

## 5. Start the application

Start Uvicorn from the directory containing `todoApp`:

```powershell
python -m uvicorn todoApp.main:app --reload
```

Or, using the existing workspace environment:

```powershell
.\fastvenv\Scripts\python.exe -m uvicorn todoApp.main:app --reload
```

Open the application:

```text
http://127.0.0.1:8000
```

Useful pages:

- Login: `http://127.0.0.1:8000/auth/login-page`
- Registration: `http://127.0.0.1:8000/auth/register-page`
- Health check: `http://127.0.0.1:8000/healthy`
- API documentation: `http://127.0.0.1:8000/docs`

Keep the Uvicorn terminal open while using the application. Press `Ctrl+C` to stop it.

## 6. First use

1. Open the registration page.
2. Create an account with a password of at least 8 characters.
3. Sign in with the username and password you registered.
4. Add tasks from the dashboard.
5. Use the checkbox to complete a task.
6. Use **Edit** to update a task.
7. Use **Delete** and confirm when removing a task.

## Run the tests

From the directory containing `todoApp`:

```powershell
python -m pytest .\todoApp\test -q
```

Expected result:

```text
8 passed
```

## Common problems

### `ModuleNotFoundError: No module named 'todoApp'`

You started Uvicorn from inside the `todoApp` folder. Move to its parent folder:

```powershell
cd ..
python -m uvicorn todoApp.main:app --reload
```

### `No module named 'fastapi'`

The virtual environment is not active, or dependencies were installed into a different Python installation. Use the same interpreter for installation and startup:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\todoApp\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn todoApp.main:app --reload
```

### MySQL connection errors

Check that:

1. The MySQL service is running.
2. `TodoApplicationDatabase` exists.
3. The username and password are correct.
4. MySQL is listening on port `3306`.
5. `DATABASE_URL` does not contain a typo.

Test the database separately in MySQL Workbench before starting the app.

### The browser shows an old interface

Stop and restart Uvicorn, then hard-refresh the page with:

```text
Ctrl + F5
```

## Project overview

- `main.py`: Creates the FastAPI application and serves the templates and static files.
- `database.py`: Creates the SQLAlchemy engine and database sessions.
- `models.py`: Defines the `Users` and `Todos` database tables.
- `routers/auth.py`: Registration, login, JWT creation, and current-user authentication.
- `routers/todos.py`: Authenticated todo CRUD endpoints.
- `templates/`: Login, registration, and dashboard pages.
- `static/`: CSS and browser JavaScript.
- `test/`: Automated tests.

## Security note

The default local database password is only for this existing local setup. Do not use it for a public deployment. For local work, `DATABASE_URL` is optional; for another MySQL installation, set it as an environment variable before starting the app.
