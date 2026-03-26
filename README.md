# Wishlist App

A web application for creating and managing wishlists, built with Django.

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
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   └── migrations/
├── templates/              # Global templates
│   ├── base.html
│   └── wishlist/
│       └── index.html
└── static/                 # Static assets
    ├── css/
    ├── js/
    └── images/
```

## Configuration

- **Database:** SQLite (default for development)
- **Static files:** Served from `static/`, collected to `staticfiles/`
- **Templates:** Project-level templates in `templates/`, app-level templates in `templates/wishlist/`

## Testing

Run the test suite with:

```bash
python manage.py test
```

To run tests for the wishlist app only:

```bash
python manage.py test wishlist
```

Tests are located in `wishlist/tests.py`. This section will be updated as test coverage expands.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
