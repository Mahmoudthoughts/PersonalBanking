

# Project: Family Credit Card Spend Tracker

## 1. Summary

A mobile-first Single Page Application (SPA) using Flask (Python) and Angular to help manage and analyze monthly credit card spending for family members. Transactions are parsed from uploaded PDFs, categorized using flexible hierarchical tags, and visualized through interactive charts.

---

## 2. Core Technologies

| Layer        | Tech                            |
| ------------ | ------------------------------- |
| Backend      | Flask (Python), SQLAlchemy      |
| Frontend     | Angular (SPA), Bootstrap        |
| Auth         | Flask-JWT-Extended              |
| Database     | PostgreSQL (Azure-hosted)       |
| File Parsing | pdfminer.six / PyMuPDF          |
| Visuals      | Chart.js / ngx-charts           |
| Reporting    | ReportLab                       |
| Deployment   | Azure App Services + PostgreSQL |

---

## 3. Entities & Schema (Searchable Fields Marked \*)

### 3.1 User

* id
* email \*
* password (hashed)
* role (default: admin)

### 3.2 Cardholder

* id
* name \*
* color

### 3.3 Transaction

* id
* date \*
* description \*
* amount \*
* cardholder\_id → Cardholder \*
* tags (many-to-many) \*
* source\_file (PDF name)
* created\_at

### 3.4 Tag

* id
* name \*
* parent\_id (nullable)

---

## 4. Functional Features

### 4.1 Authentication

* Email + password login (admin only)
* JWT-based session control

### 4.2 Upload & Parse PDF

* Upload monthly bank/credit PDF
* Parse date, amount, description
* Automatically assign to cardholder if possible (from description or file structure)
* Manual adjustment of transaction metadata (cardholder + tags)

### 4.3 Tag System

* Create/Edit/Delete hierarchical tags
* Support for multi-tag transactions
* UI: Tag cloud or dropdown hierarchy

### 4.4 Search & Filters

* Search transactions by:

  * Amount (range or exact)
  * Tag(s) (multi-select)
  * Cardholder
  * Description keywords
  * Date range

### 4.5 Visualizations

* Pie chart: Spend per category
* Bar/line chart: Monthly spend trends
* Tag-wise drilldown and comparison
* Interactive filtering on chart click

### 4.6 Reports

* HTML report generation
* Export to PDF (per month or custom range)
* Summary of:

  * Total spend
  * Spend per cardholder
  * Top tags/categories
  * Anomalies or high-ticket alerts

---

## 5. Frontend (Angular SPA)

### Pages/Routes

* `/login`
* `/dashboard` (charts + summaries)
* `/upload` (PDF dropzone)
* `/transactions` (table + filters)
* `/tags` (tag manager UI)
* `/report/:month` (HTML report)

### Components

* File uploader (drag & drop)
* Transaction table (sortable + paginated)
* Tag tree with multi-select
* Modal: Tag editor
* Responsive charts (ngx-charts)
* Search bar (multi-field)

### UX Goals

* Mobile-first layout (Bootstrap grid)
* Swipeable filters on mobile
* Loading spinners, toast messages, error states

---

## 6. Backend (Flask)

### API Endpoints

```
POST /auth/login
GET /transactions?amount=...&tag=...&date=...&desc=...
POST /transactions/upload_pdf
PATCH /transactions/:id
GET /tags
POST /tags
DELETE /tags/:id
GET /cardholders
POST /cardholders
GET /reports/:month
```

### Flask Extensions

* flask-cors
* flask-jwt-extended
* flask-sqlalchemy
* flask-marshmallow (for serialization)
* ReportLab (for PDF)

---

## 7. Codex Prompt Hints

### 🧠 Smart Codex Prompts

* Generate SQLAlchemy model for Transaction with searchable fields and many-to-many Tag relationship
* Create Angular form to upload PDF and display extracted transactions
* Create Flask route to parse PDF and insert transactions into PostgreSQL
* Build ngx-chart component for visualizing monthly spending by cardholder
* Angular Bootstrap layout with sidebar filters and responsive cards
* Generate HTML report template and export it to PDF using ReportLab

---

## 8. Deployment Plan

* Use GitHub Actions for CI/CD
* Deploy Flask to Azure App Services
* Use Azure Database for PostgreSQL
* Use Azure Blob Storage for uploaded PDFs (optional)

---

## 9. Starter GitHub Repo Layout

```
family-credit-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── cardholder.py
│   │   │   ├── transaction.py
│   │   │   ├── tag.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── transactions.py
│   │   │   ├── tags.py
│   │   │   ├── reports.py
│   │   ├── services/
│   │   │   ├── pdf_parser.py
│   │   │   ├── tagging.py
│   │   ├── utils/
│   │   │   ├── auth.py
│   │   │   ├── response.py
│   │   ├── config.py
│   │   ├── main.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── services/
│   │   │   ├── models/
│   │   │   └── app-routing.module.ts
│   │   ├── assets/
│   │   └── index.html
│   ├── angular.json
│   └── package.json
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── README.md
└── agent.md
```

---



