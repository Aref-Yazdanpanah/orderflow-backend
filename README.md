# OrderFlow

OrderFlow is a Django-based backend system designed for managing customer orders with **role-based access control (RBAC)**.  
It provides a secure and structured way for **admins** to manage all orders and products, while **customers** can create and view only their own orders.  
Through its RESTful API, OrderFlow supports order creation, editing, filtering by price and date, and robust permission enforcement at both the view and object levels.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Quickstart](#quickstart)
  - [1) Clone](#1-clone)
  - [2) Create the Environment File](#2-create-the-environment-file)
  - [3) Run with Docker](#3-run-with-docker)
- [RBAC (Role-Based Access Control)](#rbac-role-based-access-control)
- [API Endpoints](#api-endpoints)
  - [User Authentication](#user-authentication)
  - [Order Management](#order-management)
- [API Docs (Swagger / Redoc)](#api-docs-swagger--redoc)
- [Running Tests](#running-tests)
- [License](#license)

---

## Features

- **Two user roles with strict access control:**
  - **Admin**
    - View, edit, and delete *all* orders.
    - Filter orders by date and total price.
    - Manage products and pricing.
  - **Customer**
    - Create new orders.
    - View and edit *only their own* orders.
    - Cannot view or modify other users’ data.

- **Order lifecycle management:**
  - Create, update, delete, and list orders.
  - Each order can include one or more `OrderItem` entries linked to products.

- **Filtering & Ordering:**
  - Filter orders by creation date and total price.
  - Order lists by creation time or price.

- **RBAC enforcement at object level:**
  - Implemented via custom DRF permission classes.
  - Combines `IsAuthenticated` with per-object ownership checks and admin privileges.

---

## Architecture Overview

The system is structured around clean separation of concerns:

- **Models:**  
  - `Product` — defines available products with name, unit price, and active status.  
  - `OrderItem` — represents a specific product snapshot and quantity within an order.  
  - `Order` — aggregates one or more `OrderItem` objects and links to the customer who placed it.  

- **Serializers:**  
  Handle request validation and response formatting for order creation, updates, and nested order items.

- **Selectors & Services:**  
  Contain query logic and business rules, keeping views minimal and declarative.

- **Permissions:**  
  Implement fine-grained Role-Based Access Control.  
  The `IsOwnerOrHasOrderPerms` class ensures users only access what they’re authorized for.

- **Filters:**  
  Support filtering orders by price and date through Django Filter Backend.

- **Views:**  
  A single `OrderViewSetV1` handles all CRUD operations and integrates filtering, ordering, and permissions.

---

## Tech Stack

- **Backend**: Django 5 + Django REST Framework  
- **Database**: PostgreSQL 16  
- **Authentication**: JWT (via `djangorestframework-simplejwt`)  
- **Filtering**: `django-filter`  
- **Documentation**: `drf-spectacular` (Swagger + Redoc)  
- **Containerization**: Docker & Docker Compose  

---

## Quickstart

> Prerequisites: **Docker**, **Docker Compose**, and **GNU Make ≥ 4.0** (`make --version`).  
> The provided Makefile already wires everything—no manual Compose flags needed.

### 1) Clone

```bash
git clone <your-repo-url> orderflow
cd orderflow
````

### 2) Create the Environment File

Create a `.env` file in the project root (same directory as the `Makefile`), and copy the contents from `.env.example`:

```bash
cp .env.example .env
```

Then, open the `.env` file and configure the following values according to your environment:

```dotenv
# --- Django ---
SECRET_KEY=your-secret-key
DEBUG=True
DJANGO_SETTINGS_MODULE=orderflow.settings.local

# --- Postgres (matches docker-compose service names) ---
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

> For production, ensure `DEBUG=False` and replace the `SECRET_KEY` with a secure value.

### 3) Run with Docker

The following command runs the project stack (web + database):

```bash
make local-stack-up
```

Once the services are running:

* **API** → [http://localhost:8000/](http://localhost:8000/)
* **Swagger UI** → [http://localhost:8000/schema/swagger-ui/](http://localhost:8000/schema/swagger-ui/)
* **Redoc** → [http://localhost:8000/schema/redoc/](http://localhost:8000/schema/redoc/)

To stop the stack:

```bash
make local-stack-down
```

---

## RBAC (Role-Based Access Control)

OrderFlow uses Django’s permission framework to enforce **Role-Based Access Control** (RBAC).

### Roles and Permissions

| Role         | Access Scope                                                            |
| ------------ | ----------------------------------------------------------------------- |
| **Admin**    | Full CRUD on all orders and products. Can filter and manage globally.   |
| **Customer** | CRUD only on their own orders. Cannot access or edit other users’ data. |

### Implementation

* Custom permission class:
  `IsOwnerOrHasOrderPerms` combines user ownership checks with Django’s built-in `is_staff` flag or assigned custom permissions.
* Object-level checks ensure each request is validated against the user’s identity and privileges.

---

## API Endpoints

### User Authentication

The `users` app manages authentication and user profiles using JWT via **djangorestframework-simplejwt**.  
It supports both **password** and **OTP (two-step)** flows for sign-in and sign-up.

| Method | Endpoint | Description |
| ------- | -------- | ----------- |
| `POST` | `/api/v1/auth/sign-in/password/` | Sign in with mobile and password. |
| `POST` | `/api/v1/auth/sign-up/password/` | Register a new user (password-based). |
| `POST` | `/api/v1/auth/sign-in/mobile/step1/` | Request OTP for mobile sign-in. |
| `POST` | `/api/v1/auth/sign-in/otp/step2/` | Verify OTP and complete sign-in. |
| `POST` | `/api/v1/auth/sign-up/mobile/step1/` | Request OTP for mobile sign-up. |
| `POST` | `/api/v1/auth/sign-up/otp/step2/` | Verify OTP and complete registration. |
| `POST` | `/api/v1/auth/refresh-jwt/` | Refresh expired access tokens. |
| `GET`  | `/api/v1/users/i/` | Retrieve authenticated user profile. |
| `PATCH` | `/api/v1/users/i/` | Update profile details. |

All protected endpoints require a valid `Authorization: Bearer <access_token>` header.  
Authentication views are implemented in `AuthenticationViewSetV1` and `UserViewSetV1`.

---

### Order Management

| Method   | Endpoint               | Description                                      | Access         |
| -------- | ---------------------- | ------------------------------------------------ | -------------- |
| `GET`    | `/api/v1/orders/`      | List all orders (admin) or own orders (customer) | Authenticated  |
| `POST`   | `/api/v1/orders/`      | Create a new order with one or more items        | Authenticated  |
| `GET`    | `/api/v1/orders/{id}/` | Retrieve order details with its items            | Owner or Admin |
| `PATCH`  | `/api/v1/orders/{id}/` | Edit an existing order                           | Owner or Admin |
| `DELETE` | `/api/v1/orders/{id}/` | Delete an order                                  | Owner or Admin |
| `GET`    | `/api/v1/products/`    | List active products                             | Authenticated  |
| `POST`   | `/api/v1/products/`    | Create a new product                             | Admin only     |

Filtering parameters available for `/orders/`:

```
?created_at__gte=YYYY-MM-DD
?created_at__lte=YYYY-MM-DD
?total_price__gte=100
?total_price__lte=1000
```

Ordering:

```
?ordering=created_at        # oldest first
?ordering=-total_price      # highest price first
```

---

## API Docs (Swagger / Redoc)

Interactive API documentation is available after running the stack:

* **Swagger UI** → `/schema/swagger-ui/`
* **Redoc** → `/schema/redoc/`

Example (local):

* `http://localhost:8000/schema/swagger-ui/`
* `http://localhost:8000/schema/redoc/`

Both documentation views are powered by **drf-spectacular**, ensuring schema accuracy and real-time introspection of endpoints, parameters, and responses.

---

## Running Tests

All tests are written with **pytest** and **pytest-django**, following a modular structure with test factories, APIClient usage, and selector/service layer coverage.

Run tests with:

```bash
make test
```

or directly via Docker:

```bash
docker-compose -f deployment/dev/docker-compose.yml exec web pytest
```

---

## License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.

---