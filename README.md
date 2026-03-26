# Wishlist App

A web application for creating and managing wishlists, built with Python and Django. Users can register, log in, browse wishlist items, mark items as purchased, and undo purchases. Features a dark glassy UI with a disco ball background and email notifications via Resend.

## Prerequisites

- Python 3.10+
- pip
- A [Resend](https://resend.com) account (for email notifications)

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

### 6. Set environment variables and start the server

```bash
export RESEND_API_KEY=re_your_api_key_here
export RESEND_FROM_EMAIL=onboarding@resend.dev
export NOTIFICATION_TO_EMAIL=your@email.com
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`. The admin panel is at `http://127.0.0.1:8000/admin/`.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Production | Postgres connection string (falls back to SQLite locally) |
| `DJANGO_SECRET_KEY` | Production | Secret key for cryptographic signing |
| `DEBUG` | No | `True`/`False` (defaults to `True`) |
| `ALLOWED_HOSTS` | Production | Comma-separated hostnames |
| `RESEND_API_KEY` | For emails | Your Resend API key |
| `RESEND_FROM_EMAIL` | For emails | Sender address (must be verified in Resend) |
| `NOTIFICATION_TO_EMAIL` | For emails | Recipient address for purchase/undo notifications |
| `SUPABASE_S3_ACCESS_KEY` | For images | Supabase Storage S3 access key ID |
| `SUPABASE_S3_SECRET_KEY` | For images | Supabase Storage S3 secret access key |

If email or storage variables are missing, the app works normally — emails are silently skipped and images use local filesystem storage.

See `.env.example` for a template.

## Features

- **User authentication** — Register, login, and logout with a custom User model (email, phone number)
- **Wishlist display** — Items shown as glassmorphism cards with title, image, price, category, brand, store, and product link
- **Item notes** — Optional notes displayed on the item detail page
- **Sorting** — Sort items by price, category, brand, or store via query params
- **Mark as purchased** — Confirm purchase with a required checkbox disclaimer and optional message
- **Undo purchase** — "Just kidding!" button reverts a purchased item back to available
- **Email notifications** — Sends an email via Resend API when an item is purchased or undone, including the user's name, contact info, and optional message
- **Item detail page** — View full item info, notes, tracked "Visit Store" link, and purchase/undo buttons
- **Admin activity logs** — Superusers see per-item activity logs (purchase/undo events), page view counts per user, and store click logs with timestamps in Pacific Time
- **Store click tracking** — Every "Visit Store" click is logged with user and timestamp
- **OG meta tags** — Open Graph and Twitter Card tags for link previews, with per-item overrides on detail pages
- **Supabase Storage** — Product images stored in Supabase S3-compatible storage for persistent cloud hosting
- **Dark theme** — Disco ball background, dark glassmorphism UI with pink/purple accents, Poppins font

## Project Structure

```
wishlist/
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── wishlist_app/           # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── wishlist/               # Main application
│   ├── apps.py
│   ├── models.py           # User, WishlistItem, Purchase, ItemEvent, ItemView, StoreClick
│   ├── views.py            # Index, detail, auth, purchase, undo, visit-store views
│   ├── forms.py            # Registration, Purchase, UndoPurchase forms
│   ├── email.py            # Resend email notifications
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py            # Unit tests
│   └── migrations/
├── templates/              # Global templates
│   ├── base.html           # Layout with OG meta tags, dark theme, background
│   └── wishlist/
│       ├── index.html
│       ├── item_detail.html
│       ├── login.html
│       ├── register.html
│       ├── purchase.html
│       └── undo_purchase.html
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css       # Dark glassmorphism theme
│   ├── js/
│   └── images/
│       └── disco-ball.jpeg # Background image
└── media/                  # User-uploaded files (gitignored)
    └── wishlist_images/
```

## Configuration

- **Database:** Postgres via Supabase in production, SQLite for local development
- **Static files:** Served from `static/`, collected to `staticfiles/`
- **Media files:** Uploaded images served from `media/` in development
- **Templates:** Project-level templates in `templates/`, app-level templates in `templates/wishlist/`
- **Auth:** Custom user model (`wishlist.User`), login required for wishlist pages
- **Timezone:** `America/Los_Angeles` (Pacific Time) for admin log timestamps
- **Email:** Resend API, configured via environment variables
- **Image storage:** Supabase Storage (S3-compatible), falls back to local filesystem

## URL Routes

| URL | View | Description |
| --- | --- | --- |
| `/` | `index` | Wishlist page (login required) |
| `/item/<id>/` | `item_detail` | Item detail with admin logs |
| `/item/<id>/visit-store/` | `visit_store` | Tracked redirect to store URL |
| `/item/<id>/purchase/` | `mark_purchased` | Mark item as purchased + email |
| `/item/<id>/undo-purchase/` | `undo_purchase` | Revert to available + email |
| `/register/` | `register_view` | User registration |
| `/login/` | `login_view` | User login |
| `/logout/` | `logout_view` | User logout |
| `/admin/` | Django admin | Admin panel |

## Testing

This project uses Django's built-in test framework (`django.test`), which is based on Python's `unittest`. If you're coming from JavaScript, it's similar to Jest — `TestCase` classes group related tests, `setUp` works like `beforeEach`, and assertions like `assertEqual`/`assertContains` replace `expect().toBe()`.

Email tests use `unittest.mock.patch` to mock the Resend API — no real emails are sent during testing.

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
| --- | --- |
| **Models** | User creation/uniqueness, WishlistItem defaults/ordering/cascade, Purchase one-to-one/cascade, ItemEvent types/ordering/cascade, ItemView unique constraint/cascade, StoreClick multiple records/ordering/cascade |
| **Forms** | RegistrationForm validation (required fields, duplicate email, password mismatch), PurchaseForm confirm checkbox, UndoPurchaseForm optional message |
| **Auth views** | Register (success, auto-login, errors, redirect if authenticated), Login (success, failure, redirect), Logout (redirect, session cleared) |
| **Index view** | Login required, displays user items only, empty state, all sort options, purchased badge/styling, purchase/undo buttons |
| **Item detail view** | Login required, displays info, OG meta tags with price/store, purchase/undo buttons per status, view counter increments, superuser sees activity log/view stats/store click log, regular users see none of these, 404 |
| **Purchase view** | Login required, form display, successful purchase + event creation, email sent on success, email not sent on failure, missing confirm rejected, already-purchased redirect, 404, optional message |
| **Undo view** | Login required, form display, successful undo + event creation, email sent on success, email not sent when item is available, without message, available-item redirect, 404 |
| **Visit store view** | Login required, redirects to product URL, creates click record, multiple clicks logged, no-URL fallback, 404 |
| **OG meta tags** | Present on index, login, and register pages; item detail overrides with item-specific title/description/image |
| **Email utilities** | Purchased email content (name, contact, message, phone handling), undo email content (name, contact, message), skips when not configured, handles API failures gracefully |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
