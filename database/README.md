# Database (PostgreSQL)

Schema is managed through Django migrations (models are the source of
truth); `schema.sql` here is a plain-SQL reference copy for submission.

## 1. Create the database and user

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE erp_db;
CREATE USER erp_user WITH PASSWORD 'change-this-password';
GRANT ALL PRIVILEGES ON DATABASE erp_db TO erp_user;
\q
```

## 2. Point Django at it

Copy `backend/.env.example` to `backend/.env` and fill in `DB_NAME`,
`DB_USER`, `DB_PASSWORD` to match.

## 3. Create tables + seed demo data

```bash
cd backend
python manage.py migrate
python manage.py seed_demo_data
```

`seed_demo_data` creates one login per role so RBAC is easy to demo:

| Username | Password | Role |
|---|---|---|
| admin | Admin@12345 | admin (full access) |
| manager | Manager@12345 | manager (employees + reports + logs) |
| sales_user | Sales@12345 | sales (sales module) |
| inventory_user | Inventory@12345 | inventory (inventory module) |
| employee_user | Employee@12345 | employee (read-only, default self-registration role) |

Plus 4 departments, 4 employees, 3 categories, 5 products (one deliberately
below its reorder level to demonstrate the low-stock alert), and 2 customers.

## 4. Export your own live schema/data dump (optional, for submission)

```bash
pg_dump -U erp_user -d erp_db --schema-only  > database/schema_live.sql
pg_dump -U erp_user -d erp_db --data-only    > database/data_dump.sql
```

## Entity-Relationship summary

```
auth_user 1───1 accounts_profile (role)
auth_user 1───* accounts_activitylog (audit trail, nullable FK)

employees_department 1───* employees_employee

inventory_category 1───* inventory_product 1───* inventory_stockmovement

sales_customer 1───* sales_sale 1───* sales_saleitem *───1 inventory_product
```

`sales_saleitem` and `inventory_stockmovement` are the two audit-style
ledgers in this schema: every sale automatically writes a `stockmovement`
row (type `out`) linked back to it via `reference = "Sale #<id>"`, and
cancelling a sale writes matching `in` rows to restore stock - so the
ledger is always a complete, replayable history of *why* stock is at its
current level, not just a snapshot.
