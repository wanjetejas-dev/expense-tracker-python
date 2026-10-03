"""Expense Manager: a small Tkinter + MySQL desktop app for tracking expenses.

Database settings are read from environment variables (see README.md):
DB_HOST, DB_USER, DB_PASSWORD, DB_NAME.
"""

import math
import os
import tkinter as tk
from contextlib import contextmanager
from datetime import datetime
from tkinter import messagebox, ttk

import mysql.connector
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DATE_FORMAT = "%Y-%m-%d"


# Database 
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "expense_user"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "expense_tracker"),
    )


@contextmanager
def db_cursor(commit=False):
    """Open a connection and cursor, and always close them afterwards."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()
    finally:
        conn.close()


def add_expense(date, category, description, amount):
    with db_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO expenses (date, category, description, amount) "
            "VALUES (%s, %s, %s, %s)",
            (date, category, description, amount),
        )


def fetch_expenses():
    with db_cursor() as cur:
        cur.execute("SELECT id, date, category, description, amount "
                    "FROM expenses ORDER BY date DESC, id DESC")
        return cur.fetchall()


def update_expense(expense_id, date, category, description, amount):
    with db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE expenses SET date=%s, category=%s, description=%s, amount=%s "
            "WHERE id=%s",
            (date, category, description, amount, expense_id),
        )
        return cur.rowcount


def delete_expense(expense_id):
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
        return cur.rowcount


def fetch_totals_by_category():
    with db_cursor() as cur:
        cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        return cur.fetchall()


def fetch_monthly_total(month, year):
    with db_cursor() as cur:
        cur.execute(
            "SELECT SUM(amount) FROM expenses "
            "WHERE MONTH(date)=%s AND YEAR(date)=%s",
            (month, year),
        )
        result = cur.fetchone()[0]
        return result if result else 0


# Validation helpers
def parse_date(text):
    """Return a date from 'YYYY-MM-DD' text, or raise ValueError."""
    try:
        return datetime.strptime(text, DATE_FORMAT).date()
    except ValueError:
        raise ValueError("Date must be a real date in YYYY-MM-DD format.")


def parse_amount(text):
    """Return a positive, finite amount rounded to 2 decimals, or raise ValueError."""
    try:
        value = float(text)
    except ValueError:
        raise ValueError("Amount must be a number.")
    if not math.isfinite(value) or value <= 0:
        raise ValueError("Amount must be a positive number.")
    return round(value, 2)


# External API
def fetch_exchange_rate(base_currency="USD", target_currency="INR"):
    response = requests.get(
        f"https://open.er-api.com/v6/latest/{base_currency}", timeout=5
    )
    response.raise_for_status()
    data = response.json()
    if data.get("result") != "success":
        raise ValueError("API did not return success")
    rate = data["rates"][target_currency]
    updated = data.get("time_last_update_utc", "unknown time")
    return rate, updated


# GUI
class ExpenseManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Manager")
        self.root.geometry("800x620")

        tk.Label(root, text="EXPENSE MANAGER", font=("Arial", 18, "bold")).pack(pady=10)

        self.build_menu_frame(root)
        self.build_form_frame(root)
        self.build_table_frame(root)
        self.build_status_bar(root)

        self.load_expenses()

    #  Frame builders
    def build_menu_frame(self, root):
        menu_frame = tk.Frame(root)
        menu_frame.pack(fill="x", padx=15, pady=5)

        actions_frame = tk.LabelFrame(menu_frame, text="Actions", padx=5, pady=5)
        actions_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))

        for col, (label, cmd) in enumerate([
            ("Add", self.add_expense_gui),
            ("Update", self.update_expense_gui),
            ("Delete", self.delete_expense_gui),
            ("Refresh List", self.load_expenses),
        ]):
            tk.Button(actions_frame, text=label, width=12, command=cmd).grid(
                row=0, column=col, padx=3, pady=3)

        reports_frame = tk.LabelFrame(menu_frame, text="Reports", padx=5, pady=5)
        reports_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))

        for col, (label, cmd) in enumerate([
            ("Category Totals", self.show_category_totals),
            ("Monthly Total", self.show_monthly_total),
            ("Pie Chart", self.show_pie_chart),
            ("Exchange Rate", self.show_exchange_rate),
        ]):
            tk.Button(reports_frame, text=label, width=14, command=cmd).grid(
                row=0, column=col, padx=3, pady=3)

    def build_form_frame(self, root):
        form_frame = tk.LabelFrame(root, text="Expense Details", padx=10, pady=10)
        form_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(form_frame, text="ID (for update/delete):").grid(row=0, column=0, sticky="e")
        self.id_entry = tk.Entry(form_frame, width=10)
        self.id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="e")
        self.date_entry = tk.Entry(form_frame, width=20)
        self.date_entry.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        self.date_entry.insert(0, datetime.now().strftime(DATE_FORMAT))

        tk.Label(form_frame, text="Category:").grid(row=2, column=0, sticky="e")
        self.category_entry = tk.Entry(form_frame, width=20)
        self.category_entry.grid(row=2, column=1, sticky="w", padx=5, pady=3)

        tk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky="e")
        self.description_entry = tk.Entry(form_frame, width=30)
        self.description_entry.grid(row=3, column=1, sticky="w", padx=5, pady=3)

        tk.Label(form_frame, text="Amount (₹):").grid(row=4, column=0, sticky="e")
        self.amount_entry = tk.Entry(form_frame, width=15)
        self.amount_entry.grid(row=4, column=1, sticky="w", padx=5, pady=3)

    def build_table_frame(self, root):
        table_frame = tk.LabelFrame(root, text="Expenses", padx=5, pady=5)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id", "date", "category", "description", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, width in zip(columns, (40, 100, 100, 220, 80)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def build_status_bar(self, root):
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(root, textvariable=self.status_var, bd=1, relief="sunken",
                 anchor="w").pack(fill="x", side="bottom")

    # ---------------- Helpers ----------------
    def set_status(self, message):
        self.status_var.set(message)

    @staticmethod
    def _set_entry(entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def clear_form(self):
        for entry in (self.id_entry, self.category_entry,
                      self.description_entry, self.amount_entry):
            entry.delete(0, tk.END)
        self._set_entry(self.date_entry, datetime.now().strftime(DATE_FORMAT))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self._set_entry(self.id_entry, values[0])
        self._set_entry(self.date_entry, values[1])
        self._set_entry(self.category_entry, values[2])
        self._set_entry(self.description_entry, values[3])
        self._set_entry(self.amount_entry, str(values[4]).replace("₹", ""))

    def read_form(self):
        """Validate and return (date, category, description, amount).

        Shows an error dialog and returns None if anything is invalid.
        """
        category = self.category_entry.get().strip().title()
        description = self.description_entry.get().strip()
        if not category:
            messagebox.showwarning("Missing Info", "Category is required.")
            return None
        try:
            date = parse_date(self.date_entry.get().strip()
                              or datetime.now().strftime(DATE_FORMAT))
            amount = parse_amount(self.amount_entry.get().strip())
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return None
        return date, category, description, amount

    #  Actions
    def load_expenses(self):
        try:
            rows = fetch_expenses()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        self.tree.delete(*self.tree.get_children())
        for id_, date, category, description, amount in rows:
            self.tree.insert("", tk.END,
                             values=(id_, date, category, description, f"₹{amount}"))

        self.set_status(f"Loaded {len(rows)} expense(s).")

    def add_expense_gui(self):
        data = self.read_form()
        if data is None:
            return

        try:
            add_expense(*data)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", "Expense added successfully!")
        self.clear_form()
        self.load_expenses()

    def update_expense_gui(self):
        id_text = self.id_entry.get().strip()
        if not id_text:
            messagebox.showwarning("Missing ID", "Select a row or enter an ID to update.")
            return
        try:
            expense_id = int(id_text)
        except ValueError:
            messagebox.showerror("Invalid Input", "ID must be an integer.")
            return

        data = self.read_form()
        if data is None:
            return

        try:
            affected = update_expense(expense_id, *data)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        if affected:
            messagebox.showinfo("Updated", "Expense updated!")
        else:
            messagebox.showwarning(
                "No Change", "No expense found with that ID, or nothing was changed.")

        self.clear_form()
        self.load_expenses()

    def delete_expense_gui(self):
        id_text = self.id_entry.get().strip()
        if not id_text:
            messagebox.showwarning("Missing ID", "Select a row or enter an ID to delete.")
            return

        try:
            expense_id = int(id_text)
        except ValueError:
            messagebox.showerror("Invalid Input", "ID must be an integer.")
            return

        if not messagebox.askyesno("Confirm Delete", f"Delete expense ID {expense_id}?"):
            return

        try:
            affected = delete_expense(expense_id)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        if affected:
            messagebox.showinfo("Deleted", "Expense deleted!")
        else:
            messagebox.showwarning("Not Found", "No expense found with that ID.")

        self.clear_form()
        self.load_expenses()

    def show_category_totals(self):
        try:
            rows = fetch_totals_by_category()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        if not rows:
            messagebox.showinfo("Category Totals", "No data to summarize.")
            return

        lines = [f"{category:<15}: ₹{total}" for category, total in rows]
        messagebox.showinfo("Category-wise Total Spending", "\n".join(lines))

    def show_monthly_total(self):
        popup = tk.Toplevel(self.root)
        popup.title("Monthly Total")
        popup.geometry("250x170")

        tk.Label(popup, text="Month (1-12):").pack(pady=5)
        month_entry = tk.Entry(popup)
        month_entry.pack()
        month_entry.insert(0, str(datetime.now().month))

        tk.Label(popup, text="Year (e.g. 2026):").pack(pady=5)
        year_entry = tk.Entry(popup)
        year_entry.pack()
        year_entry.insert(0, str(datetime.now().year))

        def calculate():
            try:
                month = int(month_entry.get())
                year = int(year_entry.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Enter valid month and year numbers.",
                                     parent=popup)
                return
            if not 1 <= month <= 12:
                messagebox.showerror("Invalid Input", "Month must be between 1 and 12.",
                                     parent=popup)
                return

            try:
                total = fetch_monthly_total(month, year)
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", str(e), parent=popup)
                return

            messagebox.showinfo("Monthly Total",
                                f"Total spent in {month}/{year}: ₹{total}", parent=popup)
            popup.destroy()

        tk.Button(popup, text="Calculate", command=calculate).pack(pady=10)

    def show_pie_chart(self):
        try:
            rows = fetch_totals_by_category()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return

        if not rows:
            messagebox.showinfo("Pie Chart", "No data to plot.")
            return

        categories = [r[0] for r in rows]
        amounts = [float(r[1]) for r in rows]

        # Embedded in a Toplevel 
        window = tk.Toplevel(self.root)
        window.title("Expense Distribution")

        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
        ax.set_title("Expense Distribution by Category")

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_exchange_rate(self):
        try:
            rate, updated = fetch_exchange_rate("USD", "INR")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network Error", str(e))
            return
        except (KeyError, ValueError):
            messagebox.showerror("Error", "Unexpected response format from exchange API.")
            return

        messagebox.showinfo(
            "Exchange Rate",
            f"1 USD = ₹{rate:.2f}\n(Last updated: {updated})",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseManagerApp(root)
    root.mainloop()
