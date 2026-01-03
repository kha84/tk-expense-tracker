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
- flake8 (for linting)
- pytest (for testing)

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
4. Install development dependencies:
   ```bash
   pip install flake8 pytest
   ```

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

## Code Quality and Testing

### Linting
Run flake8 to check code style and potential issues:
```bash
flake8 app.py app1.py
```

### Running Tests
Execute the unit test suite:
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_database.py
pytest tests/test_finance_app.py

# Run tests with coverage (if coverage.py is installed)
pytest tests/ --cov=app
```

### Test Coverage
The test suite includes comprehensive testing with **18 test cases** covering:

#### Database Operations (`test_database.py`)
- **Database schema validation** - Table creation and structure verification
- **Category management** - Adding and loading expense/income categories  
- **Transaction CRUD** - Create, Read, Update, Delete operations
- **Data filtering** - Query transactions by type (expense/income)
- **Input validation** - Amount format and required field validation

#### Application Functionality (`test_finance_app.py`)
- **App initialization** - GUI setup and database connectivity
- **Transaction workflow** - End-to-end transaction addition process
- **Form operations** - Clear input fields and form validation
- **Date validation** - Proper date format handling
- **Financial calculations** - Total expenses, income, and balance computation
- **UI interactions** - Mock GUI components for testing
- **Category auto-creation** - Dynamic category management

#### Test Statistics
- **18 total tests** - All passing ✅
- **8 database tests** - Core data layer functionality
- **10 finance app tests** - Application layer and UI logic
- **100% test coverage** for critical application paths

#### Test Environment
- Isolated temporary databases for each test
- Mock GUI components to prevent window popups
- Parameterized SQL queries to prevent injection
- Proper cleanup of test resources

## Project Structure

- `app.py` - Main application with full CRUD operations
- `app1.py` - Alternative version with improved UI interactions
- `finance.db` - SQLite database file (auto-created)
- `tests/` - Unit test suite
  - `test_database.py` - Database operation tests
  - `test_finance_app.py` - Application functionality tests
- `AGENTS.md` - Development guidelines for contributors
