# AGENTS.md

This file contains guidelines for agentic coding agents working on the Tkinter Expense Tracker project.

## Project Overview

A simple Tkinter-based expense and income tracking application that uses SQLite for data persistence. The project consists of two main application files:
- `app.py` - Main application with full CRUD operations
- `app1.py` - Alternative version with improved UI interactions

## Development Environment

### Python Environment
- Python version: 3.12
- Virtual environment: `venv/` (already created)
- External dependencies: flake8 (linting), pytest (testing)

### Running the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run main application
python app.py

# Run alternative version
python app1.py
```

## Build, Lint, and Test Commands

### Running the Application
```bash
python app.py    # Run main expense tracker
python app1.py   # Run alternative version
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_database.py
pytest tests/test_finance_app.py

# Run tests with verbose output
pytest tests/ -v

# Run tests with coverage (if coverage.py is installed)
pytest tests/ --cov=app
```

Manual testing approach (for GUI testing):
1. Run the application
2. Test adding transactions (both expense and income)
3. Test filtering functionality
4. Test edit/delete operations
5. Verify database operations work correctly

### Code Quality
```bash
# Lint with flake8
flake8 app.py app1.py

# Python syntax checking
python -m py_compile app.py
python -m py_compile app1.py

# Check for unused imports (if available)
python -m pyflakes app.py app1.py
```

## Code Style Guidelines

### Import Organization
- Standard library imports first: `sqlite3`, `os`, `datetime`
- Third-party imports second: `tkinter` and its submodules
- Import specific modules: `from tkinter import ttk, messagebox, simpledialog`
- No blank line between import groups if only standard library

### Naming Conventions
- **Classes**: PascalCase (e.g., `FinanceApp`)
- **Functions/Methods**: snake_case (e.g., `create_db`, `add_transaction`)
- **Variables**: snake_case (e.g., `filter_type_var`, `category_dropdown`)
- **Constants**: UPPER_SNAKE_CASE (if any constants are added)
- **Database columns**: snake_case (e.g., `category_id`, `transaction_type`)

### Database Schema
- Use SQLite with standard SQL syntax
- Tables: `categories` and `transactions`
- Always use parameterized queries to prevent SQL injection
- Connection management: Open connection in `__init__`, close properly in cleanup

### GUI Organization (Tkinter)
- Use Frame widgets for layout organization
- Grid layout for forms, Pack for main layout
- ttk widgets for modern appearance
- Variable naming: `<widget_type>_<purpose>_var` for StringVar, `<widget_type>_<purpose>` for widgets
- Event handlers should be descriptive: `on_select`, `filter_transactions`

### Error Handling
- Use `messagebox.showerror()` for user-facing errors
- Validate user input before database operations
- Use try/except for type conversions (especially float conversion for amounts)
- Provide clear, user-friendly error messages

### Method Organization
1. `__init__()` - Initialize GUI components and database
2. `create_widgets()` - Build the UI layout
3. Load methods: `load_categories()`, `load_transactions()`
4. CRUD operations: `add_transaction()`, `edit_transaction()`, `delete_transaction()`
5. Helper methods: `clear_form()`, `filter_transactions()`
6. Event handlers: `on_select()` (in app1.py)

### Code Patterns
- Database queries should use parameterized statements
- Form validation before database operations
- Refresh data displays after CRUD operations
- Use StringVar for Tkinter variables
- Separate UI concerns from business logic

### File Structure
- Main application logic in `app.py` and `app1.py`
- Database file: `finance.db` (auto-created)
- Keep database schema consistent between both versions
- Each file should be runnable independently

## Specific Considerations

### Database Connection Management
- Open connection in class `__init__`
- Use cursor for operations
- Commit transactions after modifications
- Handle connection errors gracefully

### Date Handling
- Use `datetime` module for date operations
- Store dates as TEXT in 'YYYY-MM-DD' format
- Provide date validation for user input

### Amount Validation
- Convert to float with try/except
- Handle negative amounts appropriately
- Provide clear error messages for invalid input

### Category Management
- Auto-create categories if they don't exist
- Separate categories for expense vs income types
- Use dropdown/combo box for category selection

## Development Notes

- This is a simple desktop application, not a web service
- Focus on UI responsiveness and data integrity
- No external dependencies beyond Python standard library
- Database operations should be atomic and transactional
- User experience should be straightforward and intuitive

## Future Enhancement Guidelines

If adding new features:
- Follow existing naming conventions and code patterns
- Maintain database schema backward compatibility
- Add corresponding validation for new data fields
- Update both app.py and app1.py consistently if features should be shared
- Add corresponding unit tests for new functionality
- Run flake8 linting before committing changes
- Ensure all tests pass when adding new features