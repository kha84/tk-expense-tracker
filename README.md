# Tkinter Expense Tracker

A simple desktop application for tracking income and expenses using Tkinter and SQLite.

## Features

- Add, edit, and delete transactions
- Categorize transactions
- Filter by transaction type (income/expense) and category
- SQLite database for data persistence
- Simple, intuitive GUI

## Dependencies

- Python 3.12+
- tkinter (included with Python, but may require system package installation)
- sqlite3 (included with Python)

## Installation

1. Install tkinter system package if not already installed:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # Fedora
   sudo dnf install python3-tkinter
   
   # macOS (tkinter comes with Python from python.org)
   # Windows (tkinter is included with Python installer)
   ```

2. Clone the repository
3. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. No additional packages required - uses only Python standard library

## Usage

Run the main application:
```bash
python app.py
```

Or run the alternative version:
```bash
python app1.py
```

## Database

The application uses SQLite database (`finance.db`) that's automatically created on first run.

## Project Structure

- `app.py` - Main application with full CRUD operations
- `app1.py` - Alternative version with improved UI interactions
- `finance.db` - SQLite database file (auto-created)
