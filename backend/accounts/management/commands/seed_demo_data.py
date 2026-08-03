from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Profile
from employees.models import Department, Employee
from inventory.models import Category, Product, StockMovement
from sales.models import Customer

User = get_user_model()


class Command(BaseCommand):
    help = "Creates demo users (one per role) and sample ERP data for local testing."

    def handle(self, *args, **options):
        users = {
            "admin": ("Admin@12345", Profile.Role.ADMIN, True),
            "manager": ("Manager@12345", Profile.Role.MANAGER, False),
            "sales_user": ("Sales@12345", Profile.Role.SALES, False),
            "inventory_user": ("Inventory@12345", Profile.Role.INVENTORY, False),
            "employee_user": ("Employee@12345", Profile.Role.EMPLOYEE, False),
        }
        created_users = {}
        for username, (password, role, is_super) in users.items():
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                if is_super:
                    user = User.objects.create_superuser(username=username, email=f"{username}@aptura.test", password=password)
                else:
                    user = User.objects.create_user(username=username, email=f"{username}@aptura.test", password=password)
                Profile.objects.create(user=user, role=role)
                self.stdout.write(self.style.SUCCESS(f"Created {role} user -> {username} / {password}"))
            created_users[username] = user

        admin = created_users["admin"]

        # --- Departments & Employees -----------------------------------
        dept_names = ["Engineering", "Warehouse", "Sales", "Finance"]
        depts = {name: Department.objects.get_or_create(name=name)[0] for name in dept_names}

        sample_employees = [
            ("Ayesha", "Khan", "ayesha.khan@aptura.test", "0300-1234567", "Engineering", "Backend Developer", 150000, date(2023, 3, 1)),
            ("Bilal", "Ahmed", "bilal.ahmed@aptura.test", "0301-2345678", "Warehouse", "Warehouse Supervisor", 90000, date(2022, 7, 15)),
            ("Sana", "Malik", "sana.malik@aptura.test", "0302-3456789", "Sales", "Sales Executive", 95000, date(2021, 1, 10)),
            ("Usman", "Tariq", "usman.tariq@aptura.test", "0333-4567890", "Finance", "Accountant", 110000, date(2023, 9, 5)),
        ]
        for first, last, email, phone, dept, position, salary, hire_date in sample_employees:
            Employee.objects.get_or_create(
                email=email,
                defaults=dict(first_name=first, last_name=last, phone=phone, department=depts[dept],
                              position=position, salary=salary, hire_date=hire_date, created_by=admin),
            )

        # --- Inventory ---------------------------------------------------
        cat_names = ["Electronics", "Office Supplies", "Furniture"]
        cats = {name: Category.objects.get_or_create(name=name)[0] for name in cat_names}

        sample_products = [
            ("Wireless Mouse", "SKU-001", "Electronics", 800, 1500, 60, 10),
            ("Mechanical Keyboard", "SKU-002", "Electronics", 3500, 6000, 25, 5),
            ("A4 Paper Ream", "SKU-003", "Office Supplies", 400, 650, 200, 30),
            ("Office Chair", "SKU-004", "Furniture", 8000, 14000, 8, 5),
            ("Desk Lamp", "SKU-005", "Furniture", 1200, 2200, 3, 5),  # deliberately low stock
        ]
        for name, sku, cat, cost, price, qty, reorder in sample_products:
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults=dict(name=name, category=cats[cat], cost_price=cost, unit_price=price,
                              quantity_in_stock=qty, reorder_level=reorder),
            )
            if created:
                StockMovement.objects.create(
                    product=product, movement_type=StockMovement.MovementType.IN,
                    quantity=qty, reference="Initial stock", created_by=admin,
                )

        # --- Customers -----------------------------------------------------
        for name, email, phone in [
            ("Retail Customer A", "customerA@example.com", "0311-1111111"),
            ("Retail Customer B", "customerB@example.com", "0322-2222222"),
        ]:
            Customer.objects.get_or_create(name=name, defaults=dict(email=email, phone=phone))

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
