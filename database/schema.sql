

CREATE TABLE IF NOT EXISTS auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254) NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS accounts_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'employee'
        CHECK (role IN ('admin', 'manager', 'sales', 'inventory', 'employee')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS accounts_activitylog (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'login')),
    module VARCHAR(50) NOT NULL,
    object_repr VARCHAR(255) NOT NULL,
    description VARCHAR(500) NOT NULL DEFAULT '',
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_activitylog_module_action ON accounts_activitylog(module, action);
CREATE INDEX IF NOT EXISTS idx_activitylog_created ON accounts_activitylog(created_at);

CREATE TABLE IF NOT EXISTS employees_department (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS employees_employee (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    department_id INTEGER REFERENCES employees_department(id) ON DELETE SET NULL,
    position VARCHAR(100) NOT NULL,
    salary NUMERIC(12, 2) NOT NULL CHECK (salary >= 0),
    hire_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'on_leave', 'terminated')),
    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_employee_email ON employees_employee(email);
CREATE INDEX IF NOT EXISTS idx_employee_department ON employees_employee(department_id);
CREATE INDEX IF NOT EXISTS idx_employee_status ON employees_employee(status);

CREATE TABLE IF NOT EXISTS inventory_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    sku VARCHAR(64) UNIQUE NOT NULL,
    category_id INTEGER REFERENCES inventory_category(id) ON DELETE SET NULL,
    description TEXT NOT NULL DEFAULT '',
    unit VARCHAR(20) NOT NULL DEFAULT 'pcs',
    cost_price NUMERIC(12, 2) NOT NULL CHECK (cost_price >= 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    quantity_in_stock INTEGER NOT NULL DEFAULT 0 CHECK (quantity_in_stock >= 0),
    reorder_level INTEGER NOT NULL DEFAULT 10 CHECK (reorder_level >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_product_category_active ON inventory_product(category_id, is_active);
CREATE INDEX IF NOT EXISTS idx_product_sku ON inventory_product(sku);

CREATE TABLE IF NOT EXISTS inventory_stockmovement (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES inventory_product(id) ON DELETE CASCADE,
    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('in', 'out', 'adjustment')),
    quantity INTEGER NOT NULL,          -- signed: positive = increase, negative = decrease
    reference VARCHAR(100) NOT NULL DEFAULT '',
    notes VARCHAR(255) NOT NULL DEFAULT '',
    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_stockmovement_product_date ON inventory_stockmovement(product_id, created_at);

CREATE TABLE IF NOT EXISTS sales_customer (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL DEFAULT '',
    phone VARCHAR(20) NOT NULL DEFAULT '',
    address VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sales_sale (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES sales_customer(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'completed' CHECK (status IN ('completed', 'cancelled')),
    total_amount NUMERIC(14, 2) NOT NULL CHECK (total_amount >= 0),
    notes VARCHAR(255) NOT NULL DEFAULT '',
    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sale_status_date ON sales_sale(status, created_at);
CREATE INDEX IF NOT EXISTS idx_sale_created ON sales_sale(created_at);

CREATE TABLE IF NOT EXISTS sales_saleitem (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales_sale(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES inventory_product(id) ON DELETE SET NULL,
    product_name VARCHAR(200) NOT NULL,   
    unit_price NUMERIC(12, 2) NOT NULL,   
    quantity INTEGER NOT NULL CHECK (quantity >= 1)
);
CREATE INDEX IF NOT EXISTS idx_saleitem_sale ON sales_saleitem(sale_id);


