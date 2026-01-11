import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    item TEXT,
    amount REAL
)
""")

cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin')")
conn.commit()

def main_app():
    root = tk.Tk()
    root.title("Personal Expense Management System")
    root.geometry("900x600")
    root.configure(bg="#121212")

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Treeview",
        background="#1e1e1e",
        foreground="white",
        fieldbackground="#1e1e1e"
    )
    style.configure(
        "Treeview.Heading",
        background="#333333",
        foreground="white"
    )
    def add_expense():
        date = date_entry.get()
        category = category_entry.get()
        item = item_entry.get()
        amount = amount_entry.get()

        if not date or not category or not item or not amount:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid date or amount")
            return

        cursor.execute(
            "INSERT INTO expenses (date, category, item, amount) VALUES (?, ?, ?, ?)",
            (date, category, item, amount)
        )
        conn.commit()
        view_expenses()

    def view_expenses():
        for row in tree.get_children():
            tree.delete(row)

        total = 0
        cursor.execute("SELECT * FROM expenses")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
            total += row[4]

        total_label.config(text=f"Total Spent: ₹{total:.2f}")

    def delete_expense():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an expense to delete")
            return

        expense_id = tree.item(selected[0])["values"][0]
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        view_expenses()

    def edit_expense():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an expense to edit")
            return

        expense_id = tree.item(selected[0])["values"][0]

        try:
            datetime.strptime(date_entry.get(), "%Y-%m-%d")
            amount = float(amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid date or amount")
            return

        cursor.execute("""
            UPDATE expenses
            SET date=?, category=?, item=?, amount=?
            WHERE id=?
        """, (
            date_entry.get(),
            category_entry.get(),
            item_entry.get(),
            amount,
            expense_id
        ))
        conn.commit()
        view_expenses()

    def show_chart():
        cursor.execute(
            "SELECT category, SUM(amount) FROM expenses GROUP BY category"
        )
        data = cursor.fetchall()

        if not data:
            messagebox.showinfo("Info", "No data to display")
            return

        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        plt.figure()
        plt.bar(categories, amounts)
        plt.title("Category-wise Expenses")
        plt.xlabel("Category")
        plt.ylabel("Amount")
        plt.show()

    frame = tk.Frame(root, bg="#121212", padx=10, pady=10)
    frame.pack()

    tk.Label(frame, text="Date (YYYY-MM-DD)", bg="#121212", fg="white").grid(row=0, column=0)
    date_entry = tk.Entry(frame)
    date_entry.grid(row=0, column=1)

    tk.Label(frame, text="Category", bg="#121212", fg="white").grid(row=1, column=0)
    category_entry = tk.Entry(frame)
    category_entry.grid(row=1, column=1)

    tk.Label(frame, text="Item", bg="#121212", fg="white").grid(row=2, column=0)
    item_entry = tk.Entry(frame)
    item_entry.grid(row=2, column=1)

    tk.Label(frame, text="Amount", bg="#121212", fg="white").grid(row=3, column=0)
    amount_entry = tk.Entry(frame)
    amount_entry.grid(row=3, column=1)

    tk.Button(frame, text="Add Expense", command=add_expense).grid(row=4, column=0, pady=5)
    tk.Button(frame, text="Edit Expense", command=edit_expense).grid(row=4, column=1)
    tk.Button(frame, text="Delete Expense", command=delete_expense).grid(row=5, column=0)
    tk.Button(frame, text="Show Chart", command=show_chart).grid(row=5, column=1)

    columns = ("ID", "Date", "Category", "Item", "Amount")
    tree = ttk.Treeview(root, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(expand=True, fill="both", pady=10)

    total_label = tk.Label(
        root,
        text="Total Spent: ₹0.00",
        bg="#121212",
        fg="white",
        font=("Arial", 12, "bold")
    )
    total_label.pack()

    view_expenses()
    root.mainloop()

def login():
    username = user_entry.get()
    password = pass_entry.get()

    if username == "admin" and password == "admin":
        login_window.destroy()
        main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")
login_window.configure(bg="#1e1e1e")

tk.Label(login_window, text="Username", bg="#1e1e1e", fg="white").pack(pady=5)
user_entry = tk.Entry(login_window)
user_entry.pack()

tk.Label(login_window, text="Password", bg="#1e1e1e", fg="white").pack(pady=5)
pass_entry = tk.Entry(login_window, show="*")
pass_entry.pack()

tk.Button(login_window, text="Login", command=login).pack(pady=20)

login_window.mainloop()
