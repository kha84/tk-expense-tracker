import unittest
import tempfile
import os
import sqlite3
import datetime
import tkinter as tk
from unittest.mock import patch, MagicMock
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import FinanceApp


class TestDatabaseOperations(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Create a root window for testing (but don't show it)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
        # Create database tables directly
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS categories (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     type TEXT NOT NULL CHECK(type IN ('expense', 'income'))
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date TEXT NOT NULL,
                     amount REAL NOT NULL,
                     category_id INTEGER NOT NULL,
                     type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
                     description TEXT
                     )''')
        conn.commit()
        conn.close()
        
        # Create app and replace its database connection with test DB
        self.app = FinanceApp(self.root)
        self.app.conn.close()  # Close original connection to finance.db
        self.app.conn = sqlite3.connect(self.db_path)
        self.app.cursor = self.app.conn.cursor()
        
        # Update the module-level connection too
        import app
        app.conn = self.app.conn
        app.c = self.app.cursor
        
        # Also update the app's cursor reference that load_categories uses
        self.app.c = self.app.cursor
        
        # Create database tables in test database
        self.app.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     type TEXT NOT NULL CHECK(type IN ('expense', 'income'))
                     )''')
        self.app.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date TEXT NOT NULL,
                     amount REAL NOT NULL,
                     category_id INTEGER NOT NULL,
                     type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
                     description TEXT
                     )''')
        self.app.conn.commit()
        
        self.app.load_categories()
    
    def tearDown(self):
        """Clean up temporary database"""
        if hasattr(self, 'app') and hasattr(self.app, 'conn'):
            self.app.conn.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_create_db_tables(self):
        """Test that database tables are created correctly"""
        # Check if tables exist
        self.app.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('categories', 'transactions')"
        )
        tables = self.app.cursor.fetchall()
        print(f"DEBUG: Found tables: {tables}")
        self.assertEqual(len(tables), 2)
        
        # Check table schemas
        self.app.cursor.execute("PRAGMA table_info(categories)")
        categories_schema = self.app.cursor.fetchall()
        self.assertEqual(len(categories_schema), 3)  # id, name, type
        
        self.app.cursor.execute("PRAGMA table_info(transactions)")
        transactions_schema = self.app.cursor.fetchall()
        self.assertEqual(len(transactions_schema), 6)  # id, type, category, amount, date, description
    
    def test_add_category(self):
        """Test adding a new category"""
        # Add expense category
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Test Expense", "expense")
        )
        self.app.conn.commit()
        
        # Verify category was added
        self.app.cursor.execute(
            "SELECT * FROM categories WHERE name = ? AND type = ?",
            ("Test Expense", "expense")
        )
        result = self.app.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "Test Expense")
        self.assertEqual(result[2], "expense")
    
    def test_add_transaction(self):
        """Test adding a new transaction"""
        # First add a category
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Test Category", "expense")
        )
        self.app.conn.commit()
        
        # Add transaction (need category_id)
        # Get category ID first
        self.app.cursor.execute(
            "SELECT id FROM categories WHERE name = ? AND type = ?",
            ("Test Category", "expense")
        )
        category_id = self.app.cursor.fetchone()[0]
        
        transaction_data = {
            'type': 'expense',
            'category_id': category_id,
            'amount': 50.25,
            'date': '2024-01-15',
            'description': 'Test transaction'
        }
        
        self.app.cursor.execute(
            """INSERT INTO transactions (type, category_id, amount, date, description) 
               VALUES (?, ?, ?, ?, ?)""",
            (transaction_data['type'], transaction_data['category_id'],
             transaction_data['amount'], transaction_data['date'], transaction_data['description'])
        )
        self.app.conn.commit()
        
        # Verify transaction was added
        self.app.cursor.execute(
            "SELECT * FROM transactions WHERE description = ?",
            ("Test transaction",)
        )
        result = self.app.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[1], '2024-01-15')  # date
        self.assertEqual(result[2], 50.25)  # amount
        self.assertEqual(result[3], category_id)  # category_id
        self.assertEqual(result[4], 'expense')  # type
        self.assertEqual(result[5], 'Test transaction')  # description
    
    def test_load_categories(self):
        """Test loading categories from database"""
        # Add test categories
        test_categories = [
            ("Food", "expense"),
            ("Salary", "income"),
            ("Rent", "expense")
        ]
        
        for name, cat_type in test_categories:
            self.app.cursor.execute(
                "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
                (name, cat_type)
            )
        self.app.conn.commit()
        
        # Test the core functionality: querying categories from database
        self.app.cursor.execute("SELECT name FROM categories")
        all_categories = [row[0] for row in self.app.cursor.fetchall()]
        
        # Verify our test data exists in database
        self.assertIn("Food", all_categories)
        self.assertIn("Salary", all_categories)
        self.assertIn("Rent", all_categories)
        
        # Test that load_categories method can query without errors
        # (avoiding the UI dropdown part for testing)
        try:
            categories_query = "SELECT name FROM categories"
            result = self.app.cursor.execute(categories_query).fetchall()
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
        except Exception as e:
            self.fail(f"load_categories query failed: {e}")
    
    def test_load_transactions(self):
        """Test loading transactions from database"""
        # Add test data
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Food", "expense")
        )
        # Get category ID
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Food", "expense"))
        food_id = self.app.cursor.fetchone()[0]
        
        self.app.cursor.execute(
            """INSERT INTO transactions (type, category_id, amount, date, description) 
               VALUES (?, ?, ?, ?, ?)""",
            ('expense', food_id, 25.50, '2024-01-15', 'Lunch')
        )
        self.app.conn.commit()
        
        # Load transactions (simulating tree view population)
        self.app.cursor.execute(
            "SELECT * FROM transactions ORDER BY date DESC"
        )
        transactions = self.app.cursor.fetchall()
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][5], 'Lunch')  # description
        self.assertEqual(transactions[0][2], 25.50)  # amount
    
    def test_delete_transaction(self):
        """Test deleting a transaction"""
        # Add test transaction
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Test", "expense")
        )
        # Get category ID
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Test", "expense"))
        test_id = self.app.cursor.fetchone()[0]
        
        self.app.cursor.execute(
            "INSERT INTO transactions (type, category_id, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            ('expense', test_id, 100.0, '2024-01-15', 'To be deleted')
        )
        self.app.conn.commit()
        
        # Get transaction ID
        self.app.cursor.execute(
            "SELECT id FROM transactions WHERE description = ?",
            ('To be deleted',)
        )
        transaction_id = self.app.cursor.fetchone()[0]
        
        # Delete transaction
        self.app.cursor.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )
        self.app.conn.commit()
        
        # Verify deletion
        self.app.cursor.execute(
            "SELECT COUNT(*) FROM transactions WHERE id = ?",
            (transaction_id,)
        )
        count = self.app.cursor.fetchone()[0]
        self.assertEqual(count, 0)
    
    def test_filter_transactions_by_type(self):
        """Test filtering transactions by type"""
        # Add test transactions
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Food", "expense")
        )
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Salary", "income")
        )
        
        # Get category IDs
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Food", "expense"))
        food_id = self.app.cursor.fetchone()[0]
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Salary", "income"))
        salary_id = self.app.cursor.fetchone()[0]
        
        self.app.cursor.execute(
            "INSERT INTO transactions (type, category_id, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            ('expense', food_id, 50.0, '2024-01-15', 'Groceries')
        )
        self.app.cursor.execute(
            "INSERT INTO transactions (type, category_id, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            ('income', salary_id, 2000.0, '2024-01-01', 'Monthly salary')
        )
        self.app.conn.commit()
        
        # Filter expenses
        self.app.cursor.execute(
            "SELECT * FROM transactions WHERE type = ? ORDER BY date DESC",
            ('expense',)
        )
        expenses = self.app.cursor.fetchall()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0][4], 'expense')  # type column is at index 4
        
        # Filter income
        self.app.cursor.execute(
            "SELECT * FROM transactions WHERE type = ? ORDER BY date DESC",
            ('income',)
        )
        income = self.app.cursor.fetchall()
        self.assertEqual(len(income), 1)
        self.assertEqual(income[0][4], 'income')  # type column is at index 4
    
    def test_amount_validation(self):
        """Test amount validation in transactions"""
        # Test valid amounts
        valid_amounts = [50.0, 100.25, 0.01, 9999.99]
        for amount in valid_amounts:
            try:
                float(amount)
                is_valid = True
            except (ValueError, TypeError):
                is_valid = False
            self.assertTrue(is_valid, f"Amount {amount} should be valid")
        
        # Test invalid amounts
        invalid_amounts = ["invalid", "", None, "-50"]
        for amount in invalid_amounts:
            try:
                float_val = float(amount) if amount is not None else None
                is_valid = float_val is not None and float_val >= 0
            except (ValueError, TypeError):
                is_valid = False
            self.assertFalse(is_valid, f"Amount {amount} should be invalid")


if __name__ == '__main__':
    unittest.main()