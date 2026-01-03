import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import sqlite3


# Create database and tables if not exists
def create_db():
    conn = sqlite3.connect('finance.db')
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


create_db()


class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense & Income Tracker")
        self.root.geometry("1000x600")

        self.conn = sqlite3.connect('finance.db')
        self.c = self.conn.cursor()

        # GUI Elements
        self.create_widgets()
        self.load_categories()
        self.load_transactions()

    def create_widgets(self):
        # Left Frame: Input Form
        left_frame = tk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(left_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w')
        self.date_entry = tk.Entry(left_frame)
        self.date_entry.grid(row=0, column=1)

        tk.Label(left_frame, text="Amount:").grid(row=1, column=0, sticky='w')
        self.amount_entry = tk.Entry(left_frame)
        self.amount_entry.grid(row=1, column=1)

        tk.Label(left_frame, text="Category:").grid(row=2, column=0, sticky='w')
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(left_frame, textvariable=self.category_var)
        self.category_dropdown.grid(row=2, column=1)

        tk.Label(left_frame, text="Type:").grid(row=3, column=0, sticky='w')
        self.type_var = tk.StringVar(value='expense')
        self.type_radio_expense = tk.Radiobutton(left_frame, text="Expense", variable=self.type_var, value='expense')
        self.type_radio_income = tk.Radiobutton(left_frame, text="Income", variable=self.type_var, value='income')
        self.type_radio_expense.grid(row=3, column=1, sticky='w')
        self.type_radio_income.grid(row=3, column=1, sticky='e')

        tk.Label(left_frame, text="Description:").grid(row=4, column=0, sticky='w')
        self.description_entry = tk.Entry(left_frame, width=40)
        self.description_entry.grid(row=4, column=1)

        self.add_button = tk.Button(left_frame, text="Add Transaction", command=self.add_transaction)
        self.add_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.save_button = tk.Button(left_frame, text="Save Transaction", command=self.save_transaction)
        self.save_button.grid(row=6, column=0, columnspan=2, pady=10)
        self.save_button.config(state=tk.DISABLED)  # Initially disabled

        # Right Frame: Display
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons for filters
        filter_frame = tk.Frame(right_frame)
        filter_frame.pack(fill=tk.X)

        self.filter_type_var = tk.StringVar(value='all')
        self.filter_type_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, values=['all', 'expense', 'income'])
        self.filter_type_dropdown.pack(side=tk.LEFT, padx=5)

        self.filter_period_var = tk.StringVar(value='all')
        self.filter_period_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_period_var, values=['all', 'month', 'year', 'custom'])
        self.filter_period_dropdown.pack(side=tk.LEFT, padx=5)

        self.filter_date_button = tk.Button(filter_frame, text="Filter", command=self.filter_transactions)
        self.filter_date_button.pack(side=tk.LEFT, padx=5)

        # Treeview
        self.tree = ttk.Treeview(right_frame, columns=("ID", "Date", "Amount", "Category", "Type", "Description"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Description", text="Description")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, event):
        """Handle row selection to pre-fill form"""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item['values']

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[1])

        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, str(values[2]))

        self.category_var.set(values[3])

        self.type_var.set(values[4])

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, values[5])

        self.save_button.config(state=tk.NORMAL)

    def load_categories(self):
        self.c.execute("SELECT name FROM categories")
        categories = [row[0] for row in self.c.fetchall()]
        self.category_dropdown['values'] = categories

    def load_transactions(self, filter_type='all', filter_period='all', start_date=None, end_date=None):
        self.tree.delete(*self.tree.get_children())
        query = "SELECT t.id, t.date, t.amount, c.name, t.type, t.description FROM transactions t JOIN categories c ON t.category_id = c.id"
        params = []

        if filter_type != 'all':
            query += " WHERE t.type = ?"
            params.append(filter_type)

        if filter_period == 'month':
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = (today + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
            if filter_type != 'all':
                query += " AND t.date >= ? AND t.date < ?"
            else:
                query += " WHERE t.date >= ? AND t.date < ?"
            params.extend([start_date, end_date])

        elif filter_period == 'year':
            today = datetime.now()
            start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
            end_date = today.replace(year=today.year + 1, month=1, day=1).strftime('%Y-%m-%d')
            if filter_type != 'all':
                query += " AND t.date >= ? AND t.date < ?"
            else:
                query += " WHERE t.date >= ? AND t.date < ?"
            params.extend([start_date, end_date])

        elif filter_period == 'custom':
            if start_date and end_date:
                if filter_type != 'all':
                    query += " AND t.date >= ? AND t.date <= ?"
                else:
                    query += " WHERE t.date >= ? AND t.date <= ?"
                params.extend([start_date, end_date])
            else:
                messagebox.showerror("Error", "Please enter both start and end dates.")
                return

        self.c.execute(query, params)
        for row in self.c.fetchall():
            self.tree.insert('', 'end', values=row)

    def add_transaction(self):
        # Get values from the form
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        transaction_type = self.type_var.get()
        description = self.description_entry.get()

        if not all([date, amount, category]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        # Check if category exists
        self.c.execute("SELECT id FROM categories WHERE name = ? AND type = ?", (category, transaction_type))
        category_result = self.c.fetchone()

        if not category_result:
            # If category does not exist, create it
            self.c.execute("INSERT INTO categories (name, type) VALUES (?, ?)", (category, transaction_type))
            self.conn.commit()
            # Get the new category ID
            self.c.execute("SELECT id FROM categories WHERE name = ? AND type = ?", (category, transaction_type))
            category_result = self.c.fetchone()

        category_id = category_result[0]

        # Insert into transactions
        self.c.execute(
            "INSERT INTO transactions (date, amount, category_id, type, description) VALUES (?, ?, ?, ?, ?)",
            (date, amount, category_id, transaction_type, description)
        )
        self.conn.commit()
        self.load_transactions()
        self.clear_form()
        self.save_button.config(state=tk.DISABLED)
        messagebox.showinfo("Success", "Transaction added successfully.")

    def clear_form(self):
        self.date_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.category_var.set('')
        self.type_var.set('expense')

    def save_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a record to save.")
            return

        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        transaction_type = self.type_var.get()
        description = self.description_entry.get()

        if not all([date, amount, category]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        # Check if category exists
        self.c.execute("SELECT id FROM categories WHERE name = ? AND type = ?", (category, transaction_type))
        category_result = self.c.fetchone()

        if not category_result:
            # If category does not exist, create it
            self.c.execute("INSERT INTO categories (name, type) VALUES (?, ?)", (category, transaction_type))
            self.conn.commit()
            # Get the new category ID
            self.c.execute("SELECT id FROM categories WHERE name = ? AND type = ?", (category, transaction_type))
            category_result = self.c.fetchone()

        category_id = category_result[0]

        # Get the selected transaction ID
        item = self.tree.item(selected[0])
        transaction_id = item['values'][0]

        # Update the transaction
        self.c.execute(
            "UPDATE transactions SET date=?, amount=?, category_id=?, type=?, description=? WHERE id=?",
            (date, amount, category_id, transaction_type, description, transaction_id)
        )
        self.conn.commit()
        self.load_transactions()
        self.clear_form()
        self.save_button.config(state=tk.DISABLED)
        messagebox.showinfo("Success", "Transaction updated successfully.")

    def filter_transactions(self):
        filter_type = self.filter_type_var.get()
        filter_period = self.filter_period_var.get()

        if filter_period == 'custom':
            start_date = simpledialog.askstring("Start Date", "Enter start date (YYYY-MM-DD):")
            end_date = simpledialog.askstring("End Date", "Enter end date (YYYY-MM-DD):")
            if not start_date or not end_date:
                return
            self.load_transactions(filter_type, filter_period, start_date, end_date)
        else:
            self.load_transactions(filter_type, filter_period)


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
