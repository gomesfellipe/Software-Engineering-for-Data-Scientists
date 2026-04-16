# Employee Events Dashboard

A FastHTML dashboard that allows managers to monitor employee performance and predicted recruitment risk, backed by a local Python package (`employee_events`) that exposes SQL queries over the `employee_events` SQLite database.

---

## Prerequisites

- Python 3.11 or higher
- `pip`
- `git`

---

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/Software-Engineering-for-Data-Scientists.git
   cd Software-Engineering-for-Data-Scientists
   ```

2. **Create and activate a virtual environment**

   ```bash
   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate

   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install all dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   This command installs every library listed in `requirements.txt`, including the local `employee_events` package in editable mode (via the `-e python-package/` entry at the bottom of the file). No separate `pip install` for the package is needed.

---

## Running the Tests

```bash
pytest tests/ -v
```

All tests live in `tests/test_employee_events.py` and cover the `employee_events` Python package.

---

## Running the Dashboard

```bash
python report/dashboard.py
```

Open your browser at **http://localhost:5001**.

Use the **Employee / Team** radio button to switch between views, then select a name from the dropdown to load that entity's performance chart, recruitment-risk bar, and notes table.

---

## Project Structure

```
├── assets/
│   ├── model.pkl          # Pre-trained recruitment-risk model
│   └── report.css         # Dashboard stylesheet
├── python-package/
│   ├── employee_events/   # Python package source
│   │   ├── employee_events.db
│   │   ├── employee.py
│   │   ├── team.py
│   │   ├── query_base.py
│   │   └── sql_execution.py
│   └── setup.py
├── report/
│   ├── base_components/   # Reusable FastHTML component base classes
│   ├── combined_components/
│   ├── dashboard.py       # Main application entry point
│   └── utils.py           # Helper utilities (e.g. load_model)
├── tests/
│   └── test_employee_events.py
├── requirements.txt
└── README.md
```

---

## CI/CD

A GitHub Actions workflow (`.github/workflows/test.yml`) automatically runs the full test suite with `pytest tests/ -v` on every push or pull request to the `main` branch.