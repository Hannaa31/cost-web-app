# Enterprise CPQ Cost Estimation & Benchmarking Platform

> ⚠️ **STRICT SECURITY & CONFIDENTIALITY NOTICE**: All engineering specifications, cost parameters, vendor quotations, and financial models within this application are strictly confidential. Do not introduce real vendor names or corporate specifications into seed files or test workbooks.

An enterprise-grade Full-Stack Configure, Price, Quote (CPQ) and Benchmarking application designed for engineering estimators. Built with robust PostgreSQL/JSONB dynamic specification schemas, JWT authentication, cascading technical filters, and dynamic time-elapsed rate escalation.

---

## 🏛️ System Architecture & Tech Stack

* **Database:** PostgreSQL (with native `JSONB` support for dynamic equipment specification schemas; falls back seamlessly to SQLite `JSON` for local demo execution).
* **Backend:** Python 3.10+, FastAPI, SQLAlchemy (ORM), Pydantic v2, Passlib (Bcrypt hashing), Python-JOSE (JWT).
* **Frontend:** React 18+ (via Vite), React Router DOM v6, Tailwind CSS v4, TanStack Table v8, TanStack Query v5, Axios, Lucide Icons.
* **ETL Pipeline:** Python, Pandas, OpenPyXL, and SQLAlchemy for ingestion of complex concatenated Excel engineering sheets.

---

## 📁 Directory Structure

```text
d:/Cost Web app/
├── backend/
│   ├── requirements.txt         # Backend and ETL dependencies
│   ├── database.py              # SQLAlchemy Engine & SessionLocal setup
│   ├── models.py                # ORM models (User, Project, EquipmentCategory, MasterRate, EstimateLineItem)
│   ├── schemas.py               # Pydantic request/response validation schemas
│   ├── auth.py                  # JWT Auth & Bcrypt compatibility layer
│   ├── main.py                  # FastAPI application entrypoint & CORS setup
│   ├── seed.py                  # Initial Database Seeder (Admin/Estimator & generic benchmarks)
│   └── routers/
│       ├── auth_router.py       # Authentication & JWT token endpoints
│       ├── project_router.py    # Estimator workspace & line items API
│       └── cpq_router.py        # Cascading dropdown validation & escalation calculation API
├── frontend/
│   ├── package.json             # React Vite project configuration
│   ├── vite.config.js           # Vite + Tailwind CSS v4 configuration
│   └── src/
│       ├── services/api.js      # Axios API client with JWT interception
│       ├── context/AuthContext.jsx # React Authentication State Provider
│       ├── components/Navbar.jsx   # Sleek glassmorphic navigation bar
│       └── pages/
│           ├── Login.jsx        # Glassmorphic Login page with 1-click demo credentials
│           ├── Dashboard.jsx    # Projects list & New Workspace modal
│           └── Workspace.jsx    # Dynamic cascading selectors, TanStack Table & line items
└── scripts/
    ├── generate_sample_excel.py # Generates confidential dummy workbook for ETL testing
    └── import_excel.py          # Pandas -> SQLAlchemy ETL ingestion script
```

---

## 🚀 Getting Started Guide

### 1. Backend Setup & Running API Server

Open your terminal in the workspace root (`d:/Cost Web app`):

```powershell
# Create virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install required Python packages
pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### Database Configuration (PostgreSQL vs Local Demo SQLite)
By default, the application runs out-of-the-box using a local SQLite database (`cpq_enterprise.db`).
To connect to an enterprise **PostgreSQL** database with native `JSONB`:
```powershell
$env:DATABASE_URL="postgresql://username:password@localhost:5432/cpq_db"
```

#### Database Migrations & Initial Admin User Seeding
Run the seed script to initialize database tables and create the first **Admin** and **Estimator** users:

```powershell
python backend/seed.py
```

* **Admin User:** `admin@enterprise.local` / `AdminSecret123!`
* **Estimator User:** `estimator@enterprise.local` / `EstSecret123!`

#### Start the FastAPI Server
```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive API Documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2. Frontend Setup & Running Local UI

Open a second terminal window inside `/frontend`:

```powershell
cd frontend

# Install Node dependencies
npm install

# Start local React development server
npm run dev
```
* Access the CPQ Portal at: [http://localhost:5173](http://localhost:5173)

---

### 3. Running the ETL Excel Ingestion Script

The ETL script ingests legacy spreadsheet rates into the dynamic JSONB database schema.

#### Generate Sample Workbook (Optional)
Create a clean, confidential sample workbook for testing:
```powershell
python scripts/generate_sample_excel.py
```
This produces `sample_cpq_data.xlsx` containing sheet `Category_A_Conveyance`.

#### Run the ETL Pipeline
Extract standalone columns (`Type_Code`, `BW_mm`), split concatenated string columns (`Specifications` delimited by `x`), combine into JSON mapping to category schema keys, and insert into PostgreSQL:
```powershell
python scripts/import_excel.py sample_cpq_data.xlsx Category_A_Conveyance
```

---

## 🔬 Core CPQ Mathematical Models

### 1. Dynamic Annual Cost Escalation
When viewing benchmark quotes, current pricing is calculated dynamically based on historical quotation dates:
$$\text{Years Elapsed} = \frac{\text{Current Date} - \text{Quotation Date}}{365.25}$$
$$\text{Multiplier} = (1 + \text{Default Annual Escalation Rate})^{\text{Years Elapsed}}$$
$$\text{Escalated Rate} = \text{Base Rate} \times \text{Multiplier}$$

### 2. Cascading JSONB Dropdown Filtering
When selecting specifications (`POST /api/categories/{id}/valid-specs`), the system queries `MasterRate.specifications` JSONB for records matching currently selected attributes and extracts all unique valid values for remaining parameters. This ensures zero "empty" or invalid combinations.
