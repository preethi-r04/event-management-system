#!/usr/bin/env python3
"""
Event Management System (Tkinter + SQLite)
Extra Features Added:
- Sort by Date button
- Upcoming Event reminder popup on startup
"""

import sqlite3
import csv
from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT,
        venue TEXT,
        description TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_event_to_db(title, date_str, time_str, venue, description):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO events (title, date, time, venue, description) VALUES (?, ?, ?, ?, ?)",
                (title, date_str, time_str, venue, description))
    conn.commit()
    conn.close()

def update_event_in_db(event_id, title, date_str, time_str, venue, description):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    UPDATE events SET title=?, date=?, time=?, venue=?, description=? WHERE id=?
    """, (title, date_str, time_str, venue, description, event_id))
    conn.commit()
    conn.close()

def delete_event_in_db(event_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()

def fetch_all_events():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, title, date, time, venue, description FROM events ORDER BY date")
    rows = cur.fetchall()
    conn.close()
    return rows

def search_events_db(keyword=None, date=None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if keyword and date:
        cur.execute("SELECT id, title, date, time, venue, description FROM events WHERE title LIKE ? AND date=? ORDER BY date",
                    (f"%{keyword}%", date))
    elif keyword:
        cur.execute("SELECT id, title, date, time, venue, description FROM events WHERE title LIKE ? ORDER BY date",
                    (f"%{keyword}%",))
    elif date:
        cur.execute("SELECT id, title, date, time, venue, description FROM events WHERE date=? ORDER BY date",
                    (date,))
    else:
        cur.execute("SELECT id, title, date, time, venue, description FROM events ORDER BY date")
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------- GUI ----------
class EventApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Event Management System")
        self.selected_event_id = None

        # Top frame: form
        frm = ttk.Frame(root, padding=12)
        frm.pack(fill=tk.X)

        ttk.Label(frm, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.title_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.title_var, width=30).grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(frm, text="Date (YYYY-MM-DD):").grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)
        self.date_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.date_var, width=15).grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(frm, text="Time (HH:MM):").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.time_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.time_var, width=15).grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(frm, text="Venue:").grid(row=1, column=2, sticky=tk.W, padx=4, pady=4)
        self.venue_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.venue_var, width=30).grid(row=1, column=3, padx=4, pady=4)

        ttk.Label(frm, text="Description:").grid(row=2, column=0, sticky=tk.NW, padx=4, pady=4)
        self.desc_text = tk.Text(frm, width=70, height=4)
        self.desc_text.grid(row=2, column=1, columnspan=3, padx=4, pady=4)

        # Buttons
        btn_frm = ttk.Frame(root, padding=8)
        btn_frm.pack(fill=tk.X)
        ttk.Button(btn_frm, text="Add Event", command=self.add_event).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frm, text="Update Selected", command=self.update_event).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frm, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frm, text="Sort by Date", command=self.sort_by_date).pack(side=tk.LEFT, padx=6)  # NEW BUTTON
        ttk.Button(btn_frm, text="Export CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=6)

        # Search
        search_frm = ttk.Frame(root, padding=8)
        search_frm.pack(fill=tk.X)
        ttk.Label(search_frm, text="Search Title:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frm, textvariable=self.search_var, width=25).pack(side=tk.LEFT, padx=6)
        ttk.Label(search_frm, text="or Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=6)
        self.search_date_var = tk.StringVar()
        ttk.Entry(search_frm, textvariable=self.search_date_var, width=15).pack(side=tk.LEFT)
        ttk.Button(search_frm, text="Search", command=self.search_events).pack(side=tk.LEFT, padx=6)
        ttk.Button(search_frm, text="Show All", command=self.load_events).pack(side=tk.LEFT, padx=6)

        # Table
        table_frm = ttk.Frame(root, padding=8)
        table_frm.pack(fill=tk.BOTH, expand=True)
        columns = ("id", "title", "date", "time", "venue", "description")
        self.tree = ttk.Treeview(table_frm, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=40)
        self.tree.heading("title", text="Title")
        self.tree.column("title", width=180)
        self.tree.heading("date", text="Date")
        self.tree.column("date", width=90)
        self.tree.heading("time", text="Time")
        self.tree.column("time", width=70)
        self.tree.heading("venue", text="Venue")
        self.tree.column("venue", width=140)
        self.tree.heading("description", text="Description")
        self.tree.column("description", width=260)

        vsb = ttk.Scrollbar(table_frm, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Delete button
        del_frm = ttk.Frame(root, padding=8)
        del_frm.pack(fill=tk.X)
        ttk.Button(del_frm, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=6)

        # Load events
        self.load_events()

        # Show reminder popup on startup
        self.show_upcoming_event_reminder()

    # ---------- helper methods ----------
    def validate_date(self, date_text):
        if not date_text:
            return False
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_time(self, time_text):
        if not time_text:
            return True
        try:
            datetime.strptime(time_text, "%H:%M")
            return True
        except ValueError:
            return False

    def add_event(self):
        title = self.title_var.get().strip()
        date_text = self.date_var.get().strip()
        time_text = self.time_var.get().strip()
        venue = self.venue_var.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning("Validation", "Title is required.")
            return
        if not self.validate_date(date_text):
            messagebox.showwarning("Validation", "Date is required and must be YYYY-MM-DD.")
            return
        if not self.validate_time(time_text):
            messagebox.showwarning("Validation", "Time must be HH:MM or left empty.")
            return

        add_event_to_db(title, date_text, time_text, venue, description)
        messagebox.showinfo("Success", "Event added.")
        self.clear_form()
        self.load_events()

    def load_events(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = fetch_all_events()
        for r in rows:
            self.tree.insert("", tk.END, values=r)

    def sort_by_date(self):
        rows = fetch_all_events()
        sorted_rows = sorted(rows, key=lambda r: r[2])  # r[2] is date
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in sorted_rows:
            self.tree.insert("", tk.END, values=r)

    def search_events(self):
        keyword = self.search_var.get().strip()
        date_filter = self.search_date_var.get().strip()
        if date_filter and not self.validate_date(date_filter):
            messagebox.showwarning("Validation", "Date filter must be YYYY-MM-DD.")
            return
        rows = search_events_db(keyword=keyword if keyword else None, date=date_filter if date_filter else None)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in rows:
            self.tree.insert("", tk.END, values=r)

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        values = item['values']
        self.selected_event_id = values[0]
        self.title_var.set(values[1])
        self.date_var.set(values[2])
        self.time_var.set(values[3] or "")
        self.venue_var.set(values[4] or "")
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", values[5] or "")

    def clear_form(self):
        self.selected_event_id = None
        self.title_var.set("")
        self.date_var.set("")
        self.time_var.set("")
        self.venue_var.set("")
        self.desc_text.delete("1.0", tk.END)

    def update_event(self):
        if not self.selected_event_id:
            messagebox.showwarning("Selection", "Select an event from the table to update.")
            return
        title = self.title_var.get().strip()
        date_text = self.date_var.get().strip()
        time_text = self.time_var.get().strip()
        venue = self.venue_var.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning("Validation", "Title is required.")
            return
        if not self.validate_date(date_text):
            messagebox.showwarning("Validation", "Date is required and must be YYYY-MM-DD.")
            return
        if not self.validate_time(time_text):
            messagebox.showwarning("Validation", "Time must be HH:MM or left empty.")
            return

        update_event_in_db(self.selected_event_id, title, date_text, time_text, venue, description)
        messagebox.showinfo("Success", "Event updated.")
        self.clear_form()
        self.load_events()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Select an event to delete.")
            return
        item = self.tree.item(sel[0])
        event_id = item["values"][0]
        confirmed = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected event?")
        if not confirmed:
            return
        delete_event_in_db(event_id)
        messagebox.showinfo("Deleted", "Event deleted.")
        self.load_events()
        self.clear_form()

    def export_csv(self):
        rows = fetch_all_events()
        if not rows:
            messagebox.showinfo("No data", "No events to export.")
            return
        fname = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                             title="Save CSV as")
        if not fname:
            return
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "date", "time", "venue", "description"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Events exported to:\n{fname}")

    def show_upcoming_event_reminder(self):
        today = datetime.today().strftime("%Y-%m-%d")
        rows = fetch_all_events()
        upcoming = [r for r in rows if r[2] >= today]
        if upcoming:
            next_event = sorted(upcoming, key=lambda r: r[2])[0]
            messagebox.showinfo("Upcoming Event Reminder",
                                f"Next Event:\n\nTitle: {next_event[1]}\nDate: {next_event[2]}\nTime: {next_event[3] or 'N/A'}\nVenue: {next_event[4] or 'N/A'}")

# ---------- run ----------
def main():
    init_db()
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass
    app = EventApp(root)
    root.geometry("900x650")
    root.mainloop()

if __name__ == "__main__":
    main()
