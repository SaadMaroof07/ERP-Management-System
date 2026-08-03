# Aptura ERP System

Internship Batch 02 · Week 03 Task · Full Stack Development
**Stack:** Django REST Framework (backend) · Nuxt 3 / Vue (frontend) · PostgreSQL (database)

## Modules
- **Employee Management** — departments + employees, full CRUD, search/filter
- **Inventory Management** — categories + products + a full stock-movement ledger (in/out/adjustment)
- **Sales Module** — POS-style checkout that **automatically deducts inventory** in the same transaction, with cancellation that restocks
- **Reports** — dashboard KPIs, sales, inventory, and employee summaries (admin/manager only)
- **Role-Based Access Control** — 5 roles: admin, manager, sales, inventory, employee, enforced server-side on every endpoint
- **Activity Logs** — every login and every create/update/delete anywhere in the system is recorded with who/what/when
- **REST API** — fully documented in `docs/API_DOCUMENTATION.md`

## Project layout
```
erp/
├── backend/     Django + DRF API (accounts, employees, inventory, sales, reports apps)
├── frontend/    Nuxt 3 SPA
├── database/    schema.sql + setup instructions
└── docs/        API docs, architecture diagram, technical report, demo video script
```

## Quick start

### 1. Database
See `database/README.md`.

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # edit with your DB credentials
python manage.py migrate
python manage.py seed_demo_data  # creates one demo login per role
python manage.py runserver       # http://127.0.0.1:8000
```

### 3. Frontend
```bash
cd frontend
npm install --legacy-peer-deps   # some npm versions need this flag for this Nuxt/Vite dependency tree
npm run dev                      # http://localhost:3000
```

Demo logins (after `seed_demo_data`) — see `database/README.md` for the full table:
`admin / Admin@12345`, `manager / Manager@12345`, `sales_user / Sales@12345`,
`inventory_user / Inventory@12345`, `employee_user / Employee@12345`.

## Documentation
- `docs/API_DOCUMENTATION.md` — every endpoint, request/response shapes, permissions
- `database/README.md` + `database/schema.sql` — database design
- `docs/architecture-diagram.svg` — high-availability architecture for 100,000 concurrent users
- `docs/Aptura_ERP_Technical_Report.docx` — full write-up: Q1 (scaling architecture) and Q2 (deployment strategy)
- `docs/DEMO_VIDEO_SCRIPT.md` — scene-by-scene script for the required demo video
- `docs/SCREENSHOTS.md` — list of screens to capture for the submission
