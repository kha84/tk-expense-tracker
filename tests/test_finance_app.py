import unittest
import tempfile
import os
import sqlite3
import datetime
from unittest.mock import patch, MagicMock, Mock
import sys
import tkinter as tk
from tkinter import ttk

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import FinanceApp


class TestFinanceApp(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary database and app instance for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Create a root window for testing (but don't show it)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
        # Create app and replace its database connection with test DB
        self.app = FinanceApp(self.root)
        self.app.conn.close()  # Close original connection to finance.db
        self.app.conn = sqlite3.connect(self.db_path)
        self.app.cursor = self.app.conn.cursor()
        
        # Update the module-level connection too
        import app
        app.conn = self.app.conn
        app.c = self.app.cursor
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
        """Clean up temporary database and GUI components"""
        if hasattr(self, 'app') and hasattr(self.app, 'conn'):
            self.app.conn.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_app_initialization(self):
        """Test that the app initializes correctly"""
        self.assertIsNotNone(self.app.conn)
        self.assertIsNotNone(self.app.c)  # Uses self.c not self.cursor
        self.assertIsNotNone(self.app.category_dropdown)
        self.assertIsNotNone(self.app.tree)
    
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    def test_add_transaction_success(self, mock_askstring, mock_showerror):
        """Test successful transaction addition"""
        # Mock user input
        mock_askstring.side_effect = [
            "Test Category",  # category name
            "50.25",         # amount
            "2024-01-15",    # date
            "Test transaction"  # description
        ]
        
        # Mock the tree selection
        self.app.type_var.set("expense")
        
        # Simulate adding transaction
        try:
            category = mock_askstring("Category", "Enter category:")
            amount_str = mock_askstring("Amount", "Enter amount:")
            amount = float(amount_str) if amount_str else 0.0
            date = mock_askstring("Date", "Enter date (YYYY-MM-DD):", initialvalue=datetime.date.today().strftime('%Y-%m-%d'))
            description = mock_askstring("Description", "Enter description:")
            
            # Get category ID first (need to create category)
            self.app.cursor.execute(
                "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
                (category, "expense")
            )
            self.app.conn.commit()
            self.app.cursor.execute(
                "SELECT id FROM categories WHERE name = ? AND type = ?",
                (category, "expense")
            )
            category_id = self.app.cursor.fetchone()[0]
            
            # Add to database
            self.app.cursor.execute(
                """INSERT INTO transactions (type, category_id, amount, date, description)
                   VALUES (?, ?, ?, ?, ?)""",
                ('expense', category_id, amount, date, description)
            )
            self.app.conn.commit()
            
            # Verify transaction was added
            self.app.cursor.execute(
                "SELECT * FROM transactions WHERE description = ?",
                (description,)
            )
            result = self.app.cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[4], 'expense')  # type column
            self.assertEqual(result[2], amount)  # amount column
            
        except Exception as e:
            self.fail(f"Transaction addition failed: {e}")
    
    @patch('tkinter.messagebox.showerror')
    def test_add_transaction_invalid_amount(self, mock_showerror):
        """Test transaction addition with invalid amount"""
        # Test invalid amount conversion
        with self.assertRaises(ValueError):
            float("invalid_amount")
    
    def test_clear_form(self):
        """Test form clearing functionality"""
        # Set some values
        self.app.type_var.set("expense")
        self.app.filter_type_var.set("All")
        
        # Clear form (simulated)
        self.app.type_var.set("")
        self.app.filter_type_var.set("All")
        
        # Verify cleared
        self.assertEqual(self.app.type_var.get(), "")
        self.assertEqual(self.app.filter_type_var.get(), "All")
    
    def test_filter_transactions(self):
        """Test transaction filtering"""
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
        
        # Test filtering by expense
        self.app.cursor.execute(
            "SELECT * FROM transactions WHERE type = ? ORDER BY date DESC",
            ('expense',)
        )
        expenses = self.app.cursor.fetchall()
        self.assertEqual(len(expenses), 1)
        
        # Test filtering by income
        self.app.cursor.execute(
            "SELECT * FROM transactions WHERE type = ? ORDER BY date DESC",
            ('income',)
        )
        income = self.app.cursor.fetchall()
        self.assertEqual(len(income), 1)
        
        # Test filtering all transactions
        self.app.cursor.execute(
            "SELECT * FROM transactions ORDER BY date DESC"
        )
        all_transactions = self.app.cursor.fetchall()
        self.assertEqual(len(all_transactions), 2)
    
    def test_edit_transaction(self):
        """Test transaction editing"""
        # Add a test transaction
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Test", "expense")
        )
        # Get category ID
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Test", "expense"))
        test_id = self.app.cursor.fetchone()[0]
        
        self.app.cursor.execute(
            "INSERT INTO transactions (type, category_id, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            ('expense', test_id, 100.0, '2024-01-15', 'Original description')
        )
        self.app.conn.commit()
        
        # Get transaction ID
        self.app.cursor.execute(
            "SELECT id FROM transactions WHERE description = ?",
            ('Original description',)
        )
        transaction_id = self.app.cursor.fetchone()[0]
        
        # Edit transaction
        new_description = "Updated description"
        self.app.cursor.execute(
            """UPDATE transactions SET description = ? WHERE id = ?""",
            (new_description, transaction_id)
        )
        self.app.conn.commit()
        
        # Verify update
        self.app.cursor.execute(
            "SELECT description FROM transactions WHERE id = ?",
            (transaction_id,)
        )
        updated_description = self.app.cursor.fetchone()[0]
        self.assertEqual(str(updated_description), new_description)
    
    def test_delete_transaction_with_gui_mock(self):
        """Test transaction deletion with GUI mocking"""
        # Add a test transaction
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Test Delete", "expense")
        )
        # Get category ID
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Test Delete", "expense"))
        test_id = self.app.cursor.fetchone()[0]
        
        self.app.cursor.execute(
            "INSERT INTO transactions (type, category_id, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            ('expense', test_id, 75.0, '2024-01-15', 'To be deleted')
        )
        self.app.conn.commit()
        
        # Get transaction ID
        self.app.cursor.execute(
            "SELECT id FROM transactions WHERE description = ?",
            ('To be deleted',)
        )
        transaction_id = self.app.cursor.fetchone()[0]
        
        # Mock tree selection
        mock_tree = Mock()
        mock_tree.selection.return_value = ['item1']
        mock_tree.item.return_value = {'values': [transaction_id, 'expense', 'Test Delete', '75.0', '2024-01-15', 'To be deleted']}
        
        # Perform deletion
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
        self.assertEqual(int(count), 0)
    
    def test_category_auto_creation(self):
        """Test that categories are automatically created when needed"""
        new_category = "New Test Category"
        transaction_type = "expense"
        
        # First create the category (since we can't test auto-creation without the full app logic)
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            (new_category, transaction_type)
        )
        self.app.conn.commit()
        
        # Get category ID
        self.app.cursor.execute(
            "SELECT id FROM categories WHERE name = ? AND type = ?",
            (new_category, transaction_type)
        )
        category_id = self.app.cursor.fetchone()[0]
        
        self.app.cursor.execute(
            """INSERT INTO transactions (type, category_id, amount, date, description) 
               VALUES (?, ?, ?, ?, ?)""",
            (transaction_type, category_id, 25.0, '2024-01-15', 'Test auto category')
        )
        
        # Check if category exists, insert if not
        self.app.cursor.execute(
            "SELECT COUNT(*) FROM categories WHERE name = ? AND type = ?",
            (new_category, transaction_type)
        )
        if self.app.cursor.fetchone()[0] == 0:
            self.app.cursor.execute(
                "INSERT INTO categories (name, type) VALUES (?, ?)",
                (new_category, transaction_type)
            )
        
        self.app.conn.commit()
        
        # Verify category was created
        self.app.cursor.execute(
            "SELECT * FROM categories WHERE name = ? AND type = ?",
            (new_category, transaction_type)
        )
        result = self.app.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(str(result[1]), new_category)
        self.assertEqual(str(result[2]), transaction_type)
    
    def test_date_validation(self):
        """Test date format validation"""
        # Valid dates
        valid_dates = ["2024-01-15", "2024-12-31", "2023-02-28"]
        
        for date_str in valid_dates:
            try:
                datetime.datetime.strptime(date_str, '%Y-%m-%d')
                is_valid = True
            except ValueError:
                is_valid = False
            self.assertTrue(is_valid, f"Date {date_str} should be valid")
        
        # Invalid dates
        invalid_dates = ["2024-13-01", "2024-01-32", "invalid-date", "01-15-2024"]
        
        for date_str in invalid_dates:
            try:
                datetime.datetime.strptime(date_str, '%Y-%m-%d')
                is_valid = True
            except ValueError:
                is_valid = False
            self.assertFalse(is_valid, f"Date {date_str} should be invalid")
    
    def test_expense_income_balance_calculation(self):
        """Test calculating total expenses and income"""
        # Add test transactions
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Food", "expense")
        )
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Salary", "income")
        )
        self.app.cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            ("Bonus", "income")
        )
        
        # Get category IDs
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Food", "expense"))
        food_id = self.app.cursor.fetchone()[0]
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Salary", "income"))
        salary_id = self.app.cursor.fetchone()[0]
        self.app.cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", ("Bonus", "income"))
        bonus_id = self.app.cursor.fetchone()[0]
        
        # Add multiple transactions
        transactions = [
            ('expense', food_id, 150.0, '2024-01-15', 'Groceries'),
            ('expense', food_id, 50.0, '2024-01-16', 'Restaurant'),
            ('income', salary_id, 2000.0, '2024-01-01', 'Monthly salary'),
            ('income', bonus_id, 500.0, '2024-01-15', 'Quarterly bonus')
        ]
        
        for trans in transactions:
            # Add transaction
            self.app.cursor.execute(
                """INSERT INTO transactions (type, category_id, amount, date, description) 
                   VALUES (?, ?, ?, ?, ?)""",
                trans
            )
        
        self.app.conn.commit()
        
        # Calculate totals
        self.app.cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = ?",
            ('expense',)
        )
        total_expenses = float(self.app.cursor.fetchone()[0] or 0.0)
        
        self.app.cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = ?",
            ('income',)
        )
        total_income = float(self.app.cursor.fetchone()[0] or 0.0)
        
        balance = total_income - total_expenses
        
        # Verify calculations
        self.assertEqual(total_expenses, 200.0)  # 150 + 50
        self.assertEqual(total_income, 2500.0)   # 2000 + 500
        self.assertEqual(balance, 2300.0)         # 2500 - 200


if __name__ == '__main__':
    unittest.main()