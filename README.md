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

- **User dashboard** — Homepage with 3 clickable cards (Wishlists, Events, Activities) and a "Create +" dropdown menu
- **User authentication** — Register, login, and logout with a custom User model (email, phone number)
- **Wishlists** — Create and manage wishlists with item cards, sorting, purchase/undo actions
- **Events** — Create events with title, date, start/end times, address, and notes
- **Activities** — Track activities with title, location (city/state), and notes
- **Item notes** — Optional notes displayed on the item detail page
- **Mark as purchased** — Confirm purchase with a required checkbox disclaimer and optional message
- **Undo purchase** — "Just kidding!" button reverts a purchased item back to available
- **Email notifications** — Sends an email via Resend API when an item is purchased or undone
- **Admin activity logs** — Superusers see per-item activity logs, page view counts, and store click logs in Pacific Time
- **Store click tracking** — Every "Visit Store" click is logged with user and timestamp
- **OG meta tags** — Open Graph and Twitter Card tags for link previews
- **Supabase Storage** — Product images stored in Supabase S3-compatible storage
- **Responsive design** — Hamburger menu on mobile, sticky navbar, glassmorphism dark theme
- **Success messages** — Flash messages after every action (login, register, purchase, undo, create)

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
│   ├── models.py           # User, Wishlist, Event, Activity, WishlistItem, Purchase, ItemEvent, ItemView, StoreClick
│   ├── views.py            # Dashboard, CRUD, auth, purchase, undo, visit-store views
│   ├── forms.py            # Registration, Wishlist, Event, Activity, Purchase, UndoPurchase forms
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
| `/` | `dashboard` | User dashboard (login required) |
| `/wishlist/` | `index` | Wishlist items page |
| `/wishlist/<id>/` | `wishlist_detail` | Individual wishlist |
| `/events/` | `events_list` | All events |
| `/events/<id>/` | `event_detail` | Individual event |
| `/activities/` | `activities_list` | All activities |
| `/create/wishlist/` | `create_wishlist` | Create a new wishlist |
| `/create/event/` | `create_event` | Create a new event |
| `/create/activity/` | `create_activity` | Create a new activity |
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
| **Models** | User creation/uniqueness, Wishlist/WishlistItem defaults/ordering/cascade, Event fields/ordering/cascade, Activity fields/ordering/cascade, Purchase one-to-one/cascade, ItemEvent types/ordering/cascade, ItemView unique constraint/cascade, StoreClick records/ordering/cascade |
| **Forms** | RegistrationForm (required fields, duplicate email, password mismatch), EventForm (required fields, end_time after start_time validation), ActivityForm (title/location required, notes optional), PurchaseForm confirm checkbox, UndoPurchaseForm optional message |
| **Auth views** | Register (success, auto-login, message, errors, redirect), Login (success, message, failure, redirect), Logout (redirect, message, session cleared) |
| **Dashboard** | Login required, template, welcome message, 3 sections, wishlists/events/activities display, empty states, user isolation, card links |
| **Create views** | Create wishlist (login, form, success, message), Create event (login, form, success, time validation, message), Create activity (login, form, success, location required, message) |
| **Events/Activities lists** | Login required, template, user items, isolation, empty state, back link |
| **Index view** | Login required, displays user items only, empty state, all sort options, purchased badge/styling, purchase/undo buttons |
| **Item detail view** | Login required, displays info, OG meta tags, purchase/undo buttons, view counter, superuser logs, 404 |
| **Purchase view** | Login required, form, success + event + email, confirm required, already-purchased redirect, 404 |
| **Undo view** | Login required, form, success + event + email, available-item redirect, 404 |
| **Visit store view** | Login required, redirects, click records, no-URL fallback, 404 |
| **OG meta tags** | Present on index, login, register; item detail overrides |
| **Email utilities** | Purchased/undo email content, skips when not configured, handles API failures |
| **Mobile layout** | Viewport meta on all pages, sticky header, nav elements for auth/anon |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
