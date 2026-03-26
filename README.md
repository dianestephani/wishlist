# Wishlist App

A web application for creating and managing wishlists, built with Python and Django. Users can register, log in, browse wishlist items, mark items as purchased, and undo purchases.

## Prerequisites

- Python 3.10+
- pip

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/wishlist.git
cd wishlist
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`. The admin panel is at `http://127.0.0.1:8000/admin/`.

## Features

- **User authentication** — Register, login, and logout with a custom User model (email, phone number)
- **Wishlist display** — Items shown as cards with title, image, price, category, brand, store, and product link
- **Sorting** — Sort items by price, category, brand, or store via query params
- **Mark as purchased** — Confirm purchase with a required checkbox disclaimer and optional message
- **Undo purchase** — "Just kidding!" button reverts a purchased item back to available

## Project Structure

```
wishlist/
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── wishlist_app/           # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── wishlist/               # Main application
│   ├── apps.py
│   ├── models.py           # User, WishlistItem, Purchase
│   ├── views.py            # Index, auth, purchase, undo views
│   ├── forms.py            # Registration, Purchase, UndoPurchase forms
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py            # Unit tests
│   └── migrations/
├── templates/              # Global templates
│   ├── base.html
│   └── wishlist/
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── purchase.html
│       └── undo_purchase.html
└── static/                 # Static assets
    ├── css/
    │   └── style.css
    ├── js/
    └── images/
```

## Configuration

- **Database:** SQLite (default for development)
- **Static files:** Served from `static/`, collected to `staticfiles/`
- **Templates:** Project-level templates in `templates/`, app-level templates in `templates/wishlist/`
- **Auth:** Custom user model (`wishlist.User`), login required for wishlist pages

## URL Routes

| URL | View | Description |
|---|---|---|
| `/` | `index` | Wishlist page (login required) |
| `/register/` | `register_view` | User registration |
| `/login/` | `login_view` | User login |
| `/logout/` | `logout_view` | User logout |
| `/item/<id>/purchase/` | `mark_purchased` | Mark item as purchased |
| `/item/<id>/undo-purchase/` | `undo_purchase` | Revert to available |
| `/admin/` | Django admin | Admin panel |

## Testing

This project uses Django's built-in test framework (`django.test`), which is based on Python's `unittest`. If you're coming from JavaScript, it's similar to Jest — `TestCase` classes group related tests, `setUp` works like `beforeEach`, and assertions like `assertEqual`/`assertContains` replace `expect().toBe()`.

### Running tests

Run the full test suite:

```bash
python manage.py test
```

Run tests for the wishlist app only:

```bash
python manage.py test wishlist
```

Run a specific test class:

```bash
python manage.py test wishlist.tests.IndexViewTests
```

Run a single test method:

```bash
python manage.py test wishlist.tests.IndexViewTests.test_sort_by_price_asc
```

Run with verbose output:

```bash
python manage.py test --verbosity=2
```

### Test coverage

Tests are in `wishlist/tests.py` and cover:

| Area | What's tested |
|---|---|
| **Models** | User creation, email uniqueness, WishlistItem defaults/ordering/cascade, Purchase one-to-one constraint/cascade |
| **Forms** | RegistrationForm validation (required fields, duplicate email, password mismatch), PurchaseForm confirm checkbox, UndoPurchaseForm optional message |
| **Auth views** | Register (success, auto-login, errors, redirect if authenticated), Login (success, failure, redirect), Logout (redirect, session cleared) |
| **Index view** | Login required, displays user items only, empty state, all sort options, purchased badge/styling, purchase/undo buttons |
| **Purchase view** | Login required, form display, successful purchase, missing confirm rejected, already-purchased redirect, 404, optional message |
| **Undo view** | Login required, form display, successful undo, without message, available-item redirect, 404 |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
