import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


def setup_database():
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ExpenseTracker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL CHECK (transaction_type IN ('Income', 'Expense')),
        category TEXT NOT NULL,
        date DATE NOT NULL,
        notes TEXT
    )''')
    conn.commit()
    conn.close()


def add_expense(description, amount, transaction_type, category, date, notes):
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO ExpenseTracker (description, amount, transaction_type, category, date, notes)
    VALUES (?, ?, ?, ?, ?, ?)''', (description, amount, transaction_type, category, date, notes))
    conn.commit()
    conn.close()

def view_expenses():
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ExpenseTracker')
    expenses = cursor.fetchall()
    conn.close()
    return expenses

def edit_expense(expense_id, description, amount, transaction_type, category, date, notes):
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE ExpenseTracker
    SET description = ?, amount = ?, transaction_type = ?, category = ?, date = ?, notes = ?
    WHERE id = ?''', (description, amount, transaction_type, category, date, notes, expense_id))
    conn.commit()
    conn.close()

def delete_expense(expense_id):
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ExpenseTracker WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("400x450")

        
        self.add_button = tk.Button(root, text="Add Expense", command=self.open_add_expense_window, width=20)
        self.add_button.pack(pady=10)

        self.view_button = tk.Button(root, text="View Expenses", command=self.view_expenses, width=20)
        self.view_button.pack(pady=10)

        self.edit_button = tk.Button(root, text="Edit Expense", command=self.open_edit_expense_window, width=20)
        self.edit_button.pack(pady=10)

        self.delete_button = tk.Button(root, text="Delete Expense", command=self.prompt_delete_expense, width=20)
        self.delete_button.pack(pady=10)

    def open_add_expense_window(self):
        self.add_expense_window = tk.Toplevel(self.root)
        self.add_expense_window.title("Add Expense")
        self.add_expense_window.geometry("300x400")
        
        self.create_expense_form(self.add_expense_window, self.submit_expense)

    def open_edit_expense_window(self):
        expense_id = simpledialog.askinteger("Input", "Enter the ID of the expense to edit:")
        if expense_id:
            self.edit_expense_window = tk.Toplevel(self.root)
            self.edit_expense_window.title("Edit Expense")
            self.edit_expense_window.geometry("300x400")

            # Fetch existing expense data
            expense = self.get_expense_by_id(expense_id)
            if expense:
                self.create_expense_form(self.edit_expense_window, lambda desc, amt, tran, cat, dt, notes: self.update_expense(expense_id, desc, amt, tran, cat, dt, notes), expense)
            else:
                messagebox.showerror("Error", "Expense ID not found.")

    def create_expense_form(self, parent, submit_command, expense=None):
        tk.Label(parent, text="Description").pack(pady=5)
        self.description_entry = tk.Entry(parent, width=30)
        self.description_entry.pack(pady=5)
        
        tk.Label(parent, text="Amount").pack(pady=5)
        self.amount_entry = tk.Entry(parent, width=30)
        self.amount_entry.pack(pady=5)

        tk.Label(parent, text="Transaction Type").pack(pady=5)
        self.transaction_type = ttk.Combobox(parent, values=["Income", "Expense"], state="readonly")
        self.transaction_type.pack(pady=5)

        tk.Label(parent, text="Category").pack(pady=5)
        self.category_entry = tk.Entry(parent, width=30)
        self.category_entry.pack(pady=5)

        tk.Label(parent, text="Date (YYYY-MM-DD)").pack(pady=5)
        self.date_entry = tk.Entry(parent, width=30)
        self.date_entry.pack(pady=5)

        tk.Label(parent, text="Notes").pack(pady=5)
        self.notes_entry = tk.Entry(parent, width=30)
        self.notes_entry.pack(pady=5)

        submit_button = tk.Button(parent, text="Submit", command=lambda: submit_command(self.description_entry.get(), self.amount_entry.get(), self.transaction_type.get(), self.category_entry.get(), self.date_entry.get(), self.notes_entry.get()), width=20)
        submit_button.pack(pady=20)

        if expense:
            # Populate form with existing data
            self.description_entry.insert(0, expense[1])
            self.amount_entry.insert(0, expense[2])
            self.transaction_type.set(expense[3])
            self.category_entry.insert(0, expense[4])
            self.date_entry.insert(0, expense[5])
            self.notes_entry.insert(0, expense[6])

    def submit_expense(self, description, amount, transaction_type, category, date, notes):
        if description and amount and transaction_type and category and date:
            try:
                amount = float(amount)
                add_expense(description, amount, transaction_type, category, date, notes)
                messagebox.showinfo("Success", "Expense added successfully.")
                self.add_expense_window.destroy()  # Close window after submission
            except ValueError:
                messagebox.showerror("Invalid Input", "Amount must be a number.")
        else:
            messagebox.showerror("Error", "All fields must be filled!")

    def update_expense(self, expense_id, description, amount, transaction_type, category, date, notes):
        if description and amount and transaction_type and category and date:
            try:
                amount = float(amount)
                edit_expense(expense_id, description, amount, transaction_type, category, date, notes)
                messagebox.showinfo("Success", "Expense updated successfully.")
                self.edit_expense_window.destroy()  # Close window after submission
            except ValueError:
                messagebox.showerror("Invalid Input", "Amount must be a number.")
        else:
            messagebox.showerror("Error", "All fields must be filled!")

    def get_expense_by_id(self, expense_id):
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ExpenseTracker WHERE id = ?', (expense_id,))
        expense = cursor.fetchone()
        conn.close()
        return expense

    def view_expenses(self):
        expenses = view_expenses()
        view_window = tk.Toplevel(self.root)
        view_window.title("View Expenses")
        view_window.geometry("600x400")

        tree = ttk.Treeview(view_window, columns=("ID", "Description", "Amount", "Type", "Category", "Date", "Notes"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Description", text="Description")
        tree.heading("Amount", text="Amount")
        tree.heading("Type", text="Type")
        tree.heading("Category", text="Category")
        tree.heading("Date", text="Date")
        tree.heading("Notes", text="Notes")
        tree.pack(fill=tk.BOTH, expand=True)

        for expense in expenses:
            tree.insert("", tk.END, values=expense)

    def prompt_delete_expense(self):
        expense_id = simpledialog.askinteger("Input", "Enter the ID of the expense to delete:")
        if expense_id:
            if self.get_expense_by_id(expense_id):
                delete_expense(expense_id)
                messagebox.showinfo("Success", "Expense deleted successfully.")
            else:
                messagebox.showerror("Error", "Expense ID not found.")


if __name__ == "__main__":
    setup_database() 
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
