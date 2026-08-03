# Aptura ERP — API Documentation

Base URL (local): `http://127.0.0.1:8000/api`
All endpoints (except register/login/refresh) require a JWT access token:
`Authorization: Bearer <access_token>`

Roles: `admin` (full access) · `manager` (employees + reports + logs) ·
`sales` (sales module) · `inventory` (inventory module) · `employee`
(default self-registration role, read-only)

---

## Authentication — `/api/auth/`

### `POST /register/`
Public. Always creates an `employee`-role account.

Request:
```json
{ "username": "jdoe", "email": "jdoe@example.com", "first_name": "John", "last_name": "Doe", "password": "SecurePass123" }
```
Response `201`: the created user object (no password).

### `POST /login/`
Public. Returns JWT tokens + user info, and writes a `login` entry to the Activity Log.

Request: `{ "username": "jdoe", "password": "SecurePass123" }`

Response `200`:
```json
{
  "access": "<jwt>", "refresh": "<jwt>",
  "user": { "id": 1, "username": "jdoe", "email": "...", "role": "employee", "is_staff": false }
}
```

### `POST /refresh/`
Request: `{ "refresh": "<jwt>" }` → Response: `{ "access": "<new jwt>" }`

### `POST /logout/`
Auth required. Request: `{ "refresh": "<jwt>" }` → blacklists the refresh token so it can't be reused.

### `GET /me/`
Auth required. Returns the current user's profile (id, username, email, role).

### `GET /activity-logs/`
**Admin/Manager only.** Supports `?search=` (module, action, object, username).
Returns paginated audit trail: `{ count, next, previous, results: [{ id, username, action, module, object_repr, description, ip_address, created_at }] }`

---

## Employees — `/api/employees/`, `/api/departments/`

**Admin/Manager write access; any authenticated user can read.**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/employees/` | List, paginated. Supports `?search=`, `?department=`, `?status=`, `?ordering=` |
| POST | `/employees/` | Create |
| GET | `/employees/{id}/` | Retrieve |
| PATCH | `/employees/{id}/` | Update |
| DELETE | `/employees/{id}/` | Delete |
| GET/POST | `/departments/` | List / create departments |

Employee object:
```json
{
  "id": 1, "first_name": "Ayesha", "last_name": "Khan", "full_name": "Ayesha Khan",
  "email": "ayesha.khan@aptura.test", "phone": "0300-1234567",
  "department": 1, "department_name": "Engineering", "position": "Backend Developer",
  "salary": "150000.00", "hire_date": "2023-03-01", "status": "active",
  "created_at": "...", "updated_at": "..."
}
```

---

## Inventory — `/api/products/`, `/api/categories/`, `/api/stock-movements/`

**Admin/Inventory write access; any authenticated user can read** (sales
staff need read access to check stock before selling).

| Method | Endpoint | Description |
|---|---|---|
| GET | `/products/` | List. Supports `?search=`, `?category=`, `?is_active=`, `?ordering=` |
| POST | `/products/` | Create |
| GET/PATCH/DELETE | `/products/{id}/` | Retrieve / update / delete |
| GET/POST | `/categories/` | List / create categories |
| GET | `/stock-movements/` | Full movement ledger, filter by `?product=`, `?movement_type=` |
| POST | `/stock-movements/` | Record a movement (see below) — atomically updates the product's stock |

Product object includes a computed `is_low_stock` boolean
(`quantity_in_stock <= reorder_level`). `quantity_in_stock` is **read-only**
on the Product endpoint — it can only change via a stock movement or a sale,
never a direct PATCH, so the ledger stays authoritative.

`POST /stock-movements/` request:
```json
{ "product": 3, "movement_type": "in", "quantity": 50, "notes": "Restocked from supplier" }
```
- `movement_type`: `in` | `out` | `adjustment`
- For `in`/`out`, `quantity` must be a positive number (sign is applied automatically).
- For `adjustment`, `quantity` can be positive or negative directly.
- Returns `400` if an `out`/negative movement would make stock go below zero.

---

## Sales — `/api/sales/`, `/api/customers/`

**Admin/Sales write access; any authenticated user can read.**
Sales are only ever created through `/sales/checkout/`, never a plain POST
to `/sales/`, because checkout has side effects (price lookup, stock
deduction) that must not be bypassable by a client.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/sales/` | List. Supports `?status=`, `?customer=`, `?ordering=` |
| GET | `/sales/{id}/` | Retrieve (includes line items + subtotals) |
| POST | `/sales/checkout/` | Create a sale from a cart of items |
| POST | `/sales/{id}/cancel/` | Cancel a completed sale and restock every item |
| GET/POST | `/customers/` | List / create customers |

`POST /sales/checkout/` request:
```json
{
  "customer": 2,
  "notes": "Walk-in sale",
  "items": [
    { "product": 1, "quantity": 5 },
    { "product": 3, "quantity": 2 }
  ]
}
```
The client supplies only `product` + `quantity` — **price and total are
always computed server-side** from the live Product record inside a single
DB transaction (with row-level locking), so a client can never influence
the price or oversell a product. Returns `400` with a clear message if
stock is insufficient for any line item.

---

## Reports — `/api/reports/`

**Admin/Manager only.**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/reports/dashboard/` | Top-level KPIs: active employees, active products, low-stock count, total sales amount/count, inventory value |
| GET | `/reports/sales/` | Top 10 products by quantity sold + 10 most recent sales |
| GET | `/reports/inventory/` | Low-stock product list + stock value grouped by category |
| GET | `/reports/employees/` | Headcount grouped by department and by status |

---

## Common conventions

- **Pagination**: list endpoints return `{ count, next, previous, results }`, 10 per page.
- **Errors**: `400` validation errors return `{ "field_name": ["message"] }`; `401` means the access token is missing/expired; `403` means the authenticated role isn't allowed to do that action.
- **Filtering/search/ordering**: any endpoint listing `?search=` supports partial, case-insensitive text search across the fields noted above; `?ordering=field` or `?ordering=-field` sorts ascending/descending.
- **Rate limiting**: 20 requests/minute for anonymous (login/register) calls, 180/minute for authenticated calls, to slow down brute-force and abuse.
