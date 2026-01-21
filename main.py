import customtkinter as ctk
import json
import os
from datetime import datetime, timedelta

FILE_NAME = "tasks.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("600x820")
root.title("Goal Manager (Daily/Weekly/Monthly)")

all_tasks = {}
current_date = datetime.now().date()
current_week_start = current_date
current_month_start = current_date.replace(day=1)
current_view = "daily"


# ---------------- DATE HELPERS ----------------

def date_str(date):
    return date.strftime("%Y-%m-%d")


def week_of_month(date):
    return ((date.day - 1) // 7) + 1


def month_week_str(date):
    return f"{date.year}-{date.month:02}-W{week_of_month(date)}"


def month_str(date):
    return f"{date.year}-{date.month:02}"


# ---------------- FILE SYSTEM ----------------

def load_tasks():
    global all_tasks
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                today_key = date_str(current_date)
                all_tasks = {today_key: data}
                save_tasks()
            else:
                all_tasks = data
    else:
        all_tasks = {}


def save_tasks():
    with open(FILE_NAME, "w") as f:
        json.dump(all_tasks, f, indent=4)


# ---------------- TASK FUNCTIONS ----------------

def mark_frame(frame, task, done_btn):
    task["done"] = True
    save_tasks()
    frame.configure(fg_color="#2ecc71")
    done_btn.configure(fg_color="#2ecc71", hover_color="#27ae60")


def delete_frame(frame, task, key):
    all_tasks[key].remove(task)
    frame.destroy()
    save_tasks()


def create_task_ui(task, parent_frame, key):
    color = "#2ecc71" if task["done"] else "#1f6aa5"

    frame = ctk.CTkFrame(parent_frame,
                         height=120,
                         corner_radius=20,
                         fg_color=color)
    frame.pack(fill="x", padx=10, pady=8)
    frame.pack_propagate(False)

    title = ctk.CTkLabel(frame,
                         text=task["name"],
                         font=ctk.CTkFont(size=18, weight="bold"))
    title.pack(pady=(15, 5))

    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack()

    done_btn_color = "#2ecc71" if task["done"] else "#3498db"
    hover_color = "#27ae60" if task["done"] else "#1abc9c"

    done_btn = ctk.CTkButton(
        btn_frame,
        text="Done",
        width=100,
        height=40,
        corner_radius=20,
        fg_color=done_btn_color,
        hover_color=hover_color,
        command=lambda: mark_frame(frame, task, done_btn)
    )
    done_btn.pack(side="left", padx=10)

    del_btn = ctk.CTkButton(
        btn_frame,
        text="Delete",
        width=100,
        height=40,
        corner_radius=20,
        fg_color="#e74c3c",
        hover_color="#ff4d4d",
        command=lambda: delete_frame(frame, task, key)
    )
    del_btn.pack(side="right", padx=10)


# ---------------- UI SETUP ----------------

main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

tasks_frame = ctk.CTkFrame(main_frame)
tasks_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

sidebar_frame = ctk.CTkFrame(main_frame, width=180)
sidebar_frame.pack(side="right", fill="y")

# Task entry
entry_frame = ctk.CTkFrame(tasks_frame)
entry_frame.pack(fill="x", pady=(0, 10))

task_entry = ctk.CTkEntry(entry_frame, placeholder_text="Enter task...", height=40)
task_entry.pack(side="left", padx=10, fill="x", expand=True)

add_btn = ctk.CTkButton(entry_frame, text="Add", width=80, height=40, corner_radius=15)
add_btn.pack(side="right", padx=10)

# Scrollable frame
scrollable_frame = ctk.CTkScrollableFrame(tasks_frame, corner_radius=15)
scrollable_frame.pack(fill="both", expand=True)

# Date label + nav
date_frame = ctk.CTkFrame(tasks_frame)
date_frame.pack(fill="x", pady=5)

date_label = ctk.CTkLabel(date_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
date_label.pack(side="left", expand=True)

prev_btn = ctk.CTkButton(date_frame, text="◀", width=50, height=40, corner_radius=15)
prev_btn.pack(side="left", padx=5)
next_btn = ctk.CTkButton(date_frame, text="▶", width=50, height=40, corner_radius=15)
next_btn.pack(side="right", padx=5)


# ---------------- VIEW FUNCTIONS ----------------

def refresh_tasks():
    for w in scrollable_frame.winfo_children():
        w.destroy()

    global current_view
    if current_view == "daily":
        key = date_str(current_date)
        prev_btn.configure(command=prev_day)
        next_btn.configure(command=next_day)
    elif current_view == "weekly":
        key = month_week_str(current_week_start)
        prev_btn.configure(command=prev_week)
        next_btn.configure(command=next_week)
    else:  # monthly
        key = month_str(current_month_start)
        prev_btn.configure(command=prev_month)
        next_btn.configure(command=next_month)

    if key not in all_tasks:
        all_tasks[key] = []

    for task in all_tasks[key]:
        create_task_ui(task, scrollable_frame, key)

    date_label.configure(text=key)


def add_task():
    text = task_entry.get().strip()
    if not text:
        return
    if current_view == "daily":
        key = date_str(current_date)
    elif current_view == "weekly":
        key = month_week_str(current_week_start)
    else:
        key = month_str(current_month_start)

    new_task = {"name": text, "done": False}
    all_tasks[key].append(new_task)
    save_tasks()
    create_task_ui(new_task, scrollable_frame, key)
    task_entry.delete(0, "end")


# ---------------- NAVIGATION ----------------

def prev_day():
    global current_date
    current_date -= timedelta(days=1)
    refresh_tasks()


def next_day():
    global current_date
    current_date += timedelta(days=1)
    refresh_tasks()


def prev_week():
    global current_week_start
    current_week_start -= timedelta(days=7)
    refresh_tasks()


def next_week():
    global current_week_start
    current_week_start += timedelta(days=7)
    refresh_tasks()


def prev_month():
    global current_month_start
    year = current_month_start.year
    month = current_month_start.month - 1
    if month == 0:
        month = 12
        year -= 1
    current_month_start = current_month_start.replace(year=year, month=month, day=1)
    refresh_tasks()


def next_month():
    global current_month_start
    year = current_month_start.year
    month = current_month_start.month + 1
    if month == 13:
        month = 1
        year += 1
    current_month_start = current_month_start.replace(year=year, month=month, day=1)
    refresh_tasks()


# ---------------- SIDEBAR ----------------

def switch_to_daily():
    global current_view
    current_view = "daily"
    refresh_tasks()


def switch_to_weekly():
    global current_view
    current_view = "weekly"
    refresh_tasks()


def switch_to_monthly():
    global current_view
    current_view = "monthly"
    refresh_tasks()


daily_btn = ctk.CTkButton(
    sidebar_frame,
    text="Daily Planner",
    width=150,
    height=50,
    corner_radius=25,
    command=switch_to_daily
)
daily_btn.pack(pady=20, padx=10)

weekly_btn = ctk.CTkButton(
    sidebar_frame,
    text="Weekly Planner",
    width=150,
    height=50,
    corner_radius=25,
    command=switch_to_weekly
)
weekly_btn.pack(pady=20, padx=10)

monthly_btn = ctk.CTkButton(
    sidebar_frame,
    text="Monthly Planner",
    width=150,
    height=50,
    corner_radius=25,
    command=switch_to_monthly
)
monthly_btn.pack(pady=20, padx=10)


# ---------------- STARTUP ----------------

load_tasks()
add_btn.configure(command=add_task)
root.bind("<Return>", lambda e: add_task())
refresh_tasks()

root.mainloop()
