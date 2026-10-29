# Aptura ERP

## Overview

Aptura ERP (Enterprise Resource Planning System) is a business management application for handling employee records, inventory, sales, and reporting from a single platform. It provides a web-based interface connected to a REST API, with access to system modules controlled by user roles.

## Features

- Role-based authentication and access control for administrators, managers, sales users, inventory users, and employees.
- Employee and department management, including employee details, job titles, salary, hire dates, and employment status.
- Product and category management with stock levels, reorder thresholds, and stock movement history.
- Sales and customer management, including checkout, sale details, cancellation, and stock updates.
- Dashboard and reports for sales, inventory, low-stock products, and employee statistics.
- Activity logs for reviewing recorded system actions.

## Technologies

- **Frontend:** Nuxt 3, Vue 3, TypeScript, Tailwind CSS, Pinia
- **Backend:** Python, Django 5, Django REST Framework
- **Authentication:** SimpleJWT
- **Database:** SQLite or PostgreSQL
- **Additional backend packages:** django-filter, django-cors-headers
