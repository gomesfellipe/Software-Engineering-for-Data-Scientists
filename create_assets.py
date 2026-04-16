"""
Script to generate:
1. employee_events.db - SQLite database with sample data
2. assets/model.pkl   - Pre-trained scikit-learn model for recruitment risk prediction

Run from the project root:
    python create_assets.py
"""
import sqlite3
import pickle
import random
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier

# ─── Paths ────────────────────────────────────────────────────────────────────
project_root = Path(__file__).parent
db_path = project_root / "python-package" / "employee_events" / "employee_events.db"
model_path = project_root / "assets" / "model.pkl"

db_path.parent.mkdir(parents=True, exist_ok=True)
model_path.parent.mkdir(parents=True, exist_ok=True)


# ─── 1. Create SQLite Database ────────────────────────────────────────────────
print("Creating employee_events.db ...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.executescript("""
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS employee_events;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS team;

CREATE TABLE team (
    team_id      INTEGER PRIMARY KEY,
    team_name    TEXT,
    shift        TEXT,
    manager_name TEXT
);

CREATE TABLE employee (
    employee_id INTEGER PRIMARY KEY,
    first_name  TEXT,
    last_name   TEXT,
    team_id     INTEGER REFERENCES team(team_id)
);

CREATE TABLE employee_events (
    event_date       TEXT,
    employee_id      INTEGER REFERENCES employee(employee_id),
    team_id          INTEGER REFERENCES team(team_id),
    positive_events  INTEGER,
    negative_events  INTEGER
);

CREATE TABLE notes (
    employee_id INTEGER,
    team_id     INTEGER,
    note        TEXT,
    note_date   TEXT,
    PRIMARY KEY (employee_id, team_id, note_date)
);
""")

# Teams
teams = [
    (1, "Alpha Team",   "Morning",   "Sandra Lee"),
    (2, "Beta Team",    "Afternoon", "James Park"),
    (3, "Gamma Team",   "Night",     "Maria Costa"),
]
cursor.executemany("INSERT INTO team VALUES (?, ?, ?, ?)", teams)

# Employees
employees = [
    (1,  "Alice",   "Johnson",  1),
    (2,  "Bob",     "Smith",    1),
    (3,  "Carol",   "White",    1),
    (4,  "David",   "Brown",    2),
    (5,  "Eva",     "Davis",    2),
    (6,  "Frank",   "Wilson",   2),
    (7,  "Grace",   "Martinez", 3),
    (8,  "Henry",   "Anderson", 3),
    (9,  "Isabela", "Taylor",   3),
    (10, "Jack",    "Thomas",   3),
]
cursor.executemany("INSERT INTO employee VALUES (?, ?, ?, ?)", employees)

# Employee events — 12 months of data
random.seed(42)
events = []
dates = [f"2024-{m:02d}-01" for m in range(1, 13)]

for emp_id, _, _, team_id in employees:
    # Employees 1–3 (Alpha): high-performers → low recruitment risk
    # Employees 4–6 (Beta):  mixed             → medium risk
    # Employees 7–10 (Gamma): stressed          → high recruitment risk
    if team_id == 1:
        pos_range, neg_range = (4, 8), (0, 2)
    elif team_id == 2:
        pos_range, neg_range = (3, 6), (1, 4)
    else:
        pos_range, neg_range = (1, 3), (3, 7)

    for date in dates:
        pos = random.randint(*pos_range)
        neg = random.randint(*neg_range)
        events.append((date, emp_id, team_id, pos, neg))

cursor.executemany(
    "INSERT INTO employee_events VALUES (?, ?, ?, ?, ?)", events
)

# Notes
notes_data = [
    (1, 1, "Excellent project delivery ahead of schedule.", "2024-03-15"),
    (1, 1, "Led team standup effectively while manager was away.", "2024-06-20"),
    (2, 1, "Completed certification in process optimization.", "2024-04-10"),
    (4, 2, "Missed two deadlines this quarter.", "2024-05-05"),
    (4, 2, "Showed improvement after coaching session.", "2024-08-12"),
    (5, 2, "Strong collaboration with cross-functional teams.", "2024-07-18"),
    (7, 3, "Raised concerns about workload in last review.", "2024-02-28"),
    (7, 3, "Requested transfer to day shift.", "2024-09-01"),
    (8, 3, "Attendance issues over the past two months.", "2024-10-05"),
    (9, 3, "Exceptional technical skills noted by peers.", "2024-11-20"),
]
cursor.executemany("INSERT INTO notes VALUES (?, ?, ?, ?)", notes_data)

conn.commit()
conn.close()
print(f"  OK Database created at: {db_path}")


# ─── 2. Train and Save ML Model ───────────────────────────────────────────────
print("Training recruitment risk model ...")

# Features: [positive_events, negative_events] aggregated per employee
# Label: 1 = recruited away (high risk), 0 = retained (low risk)
#
# Logic: employees with consistently low positive & high negative events
# are flagged as high recruitment risk in the synthetic training data.

rng = np.random.default_rng(42)

n_low_risk  = 300
n_high_risk = 300

# Low-risk employees: more positives, fewer negatives
X_low  = np.column_stack([
    rng.integers(40, 100, n_low_risk),   # positive_events (sum)
    rng.integers(0,   25, n_low_risk),   # negative_events (sum)
])
y_low = np.zeros(n_low_risk, dtype=int)

# High-risk employees: fewer positives, more negatives
X_high = np.column_stack([
    rng.integers(5,  35, n_high_risk),   # positive_events (sum)
    rng.integers(20, 80, n_high_risk),   # negative_events (sum)
])
y_high = np.ones(n_high_risk, dtype=int)

X = np.vstack([X_low, X_high])
y = np.concatenate([y_low, y_high])

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

with open(model_path, "wb") as f:
    pickle.dump(model, f)

print(f"  OK Model saved at: {model_path}")
print("\nDone! Both assets have been created.")
