# Wishlist App

A multi-user web application for creating and managing wishlists, events, and activities. Built with Python and Django, featuring a dark glassmorphism UI with a disco ball background, email notifications via Resend, and cloud storage via Supabase.

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

- **Personalized dashboard** — Welcome message with first name, 3 clickable cards (Wishlists, Events, Activities), friends row with avatars, "Create +" dropdown with modals, all scoped to the logged-in user
- **User authentication** — Register, login, logout with custom User model (email, phone number)
- **User profiles** — View/edit profile (username, name, email, phone), seafoam avatar with initials, delete account with cascade
- **Wishlists** — Create multiple wishlists, each with their own items. Full CRUD on wishlists and items
- **Events** — Create events with title, date, start/end times, address, notes. Full CRUD
- **Activities** — Track activities with title, location, notes. Full CRUD
- **Friend system** — Friendship model (directional), auto-friend admin on registration
- **Friends page** — Search bar for finding users, friend cards with avatars, links to public profiles
- **Public profiles** — `/users/<username>/` shows name, avatar, and public wishlists/events/activities. No email or phone exposed
- **Visibility system** — `is_public` boolean on Wishlists, Events, and Activities. Only public items shown on profiles. Defaults to public
- **Mark as purchased** — Confirm with checkbox disclaimer and optional message
- **Undo purchase** — "Just kidding!" reverts item to available
- **Email notifications** — Resend API emails on purchase/undo with user contact info
- **Admin activity logs** — Superusers see per-item purchase/undo logs, page view counts, store click logs (Pacific Time)
- **Store click tracking** — Every "Visit Store" click logged per user
- **OG meta tags** — Open Graph and Twitter Card tags with per-item overrides
- **Supabase Storage** — Product images stored in S3-compatible cloud storage
- **Responsive design** — Hamburger menu on mobile, sticky navbar, dark glassmorphism theme
- **Success messages** — Flash messages after every action

## Project Structure

```
wishlist/
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment config
├── .env.example            # Environment variable template
├── .python-version         # Python version for deployment
├── wishlist_app/           # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── wishlist/               # Main application
│   ├── apps.py
│   ├── models.py           # User, Wishlist, WishlistItem, Event, Activity, Friendship, Purchase, ItemEvent, ItemView, StoreClick
│   ├── views.py            # Dashboard, CRUD, auth, profile, friends, purchase views
│   ├── forms.py            # Profile, Registration, Wishlist, WishlistItem, Event, Activity, Purchase forms
│   ├── email.py            # Resend email notifications
│   ├── signals.py          # Auto-friend admin on registration
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py            # 240 unit tests
│   └── migrations/
├── templates/              # Global templates
│   ├── base.html           # Layout with nav, modals, OG tags, dark theme
│   └── wishlist/
│       ├── dashboard.html
│       ├── index.html          # Wishlists list
│       ├── wishlist_detail.html
│       ├── item_detail.html
│       ├── events.html
│       ├── event_detail.html
│       ├── activities.html
│       ├── friends.html
│       ├── profile.html
│       ├── edit_profile.html
│       ├── login.html
│       ├── register.html
│       ├── create_*.html       # Create forms
│       ├── edit_*.html         # Edit forms
│       ├── add_item.html
│       ├── confirm_delete.html
│       ├── confirm_delete_account.html
│       ├── purchase.html
│       └── undo_purchase.html
├── static/
│   ├── css/style.css       # Dark glassmorphism theme
│   └── images/
└── media/                  # User-uploaded files (gitignored)
    └── wishlist_images/
```

## Configuration

- **Database:** Postgres via Supabase in production, SQLite for local development
- **Static files:** Served via WhiteNoise from `staticfiles/`
- **Media files:** Supabase Storage (S3-compatible) in production, local filesystem in dev
- **Auth:** Custom user model (`wishlist.User`), login required for all app pages
- **Timezone:** `America/Los_Angeles` (Pacific Time)
- **Email:** Resend API
- **Deployment:** Vercel with `@vercel/python`

## URL Routes

| URL | View | Description |
| --- | --- | --- |
| `/` | `dashboard` | Personalized dashboard (login required) |
| `/wishlist/` | `index` | All user's wishlists |
| `/wishlist/<id>/` | `wishlist_detail` | Wishlist with items, purchase/undo modals |
| `/wishlist/<id>/edit/` | `edit_wishlist` | Edit wishlist |
| `/wishlist/<id>/delete/` | `delete_wishlist` | Delete wishlist |
| `/wishlist/<id>/add-item/` | `add_item` | Add item to wishlist |
| `/item/<id>/` | `item_detail` | Item detail with admin logs |
| `/item/<id>/edit/` | `edit_item` | Edit item |
| `/item/<id>/delete/` | `delete_item` | Delete item |
| `/item/<id>/visit-store/` | `visit_store` | Tracked redirect to store |
| `/item/<id>/purchase/` | `mark_purchased` | Mark purchased + email |
| `/item/<id>/undo-purchase/` | `undo_purchase` | Undo purchase + email |
| `/events/` | `events_list` | All user's events |
| `/events/<id>/` | `event_detail` | Event detail |
| `/events/<id>/edit/` | `edit_event` | Edit event |
| `/events/<id>/delete/` | `delete_event` | Delete event |
| `/activities/` | `activities_list` | All user's activities |
| `/activities/<id>/edit/` | `edit_activity` | Edit activity |
| `/activities/<id>/delete/` | `delete_activity` | Delete activity |
| `/create/wishlist/` | `create_wishlist` | Create wishlist (+ optional first item) |
| `/create/event/` | `create_event` | Create event |
| `/create/activity/` | `create_activity` | Create activity |
| `/profile/` | `profile` | User profile |
| `/profile/edit/` | `edit_profile` | Edit profile (including username) |
| `/profile/delete/` | `delete_account` | Delete account |
| `/friends/` | `friends` | Friends page with search |
| `/users/<username>/` | `public_profile` | Public user profile |
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
python manage.py test wishlist.tests.DashboardViewTests
```

Run a single test method:

```bash
python manage.py test wishlist.tests.DashboardViewTests.test_welcome_shows_first_name
```

Run with verbose output:

```bash
python manage.py test --verbosity=2
```

### Test coverage

261 tests in `wishlist/tests.py` covering:

| Area | What's tested |
| --- | --- |
| **Models** | User, Wishlist, WishlistItem, Event, Activity, Purchase, ItemEvent, ItemView, StoreClick, Friendship — creation, defaults, ordering, cascade delete, unique constraints |
| **Forms** | ProfileForm (username/email uniqueness), RegistrationForm, EventForm (time validation), ActivityForm, WishlistForm, WishlistItemForm, PurchaseForm, UndoPurchaseForm |
| **Auth views** | Register (success, auto-login, message, errors, redirect), Login (success, message, failure, redirect), Logout (redirect, message, session cleared) |
| **Dashboard** | Login required, personalized welcome (first name / username fallback), 3 sections + friends row, data display, empty states, user isolation for wishlists/events/activities/friends, card links |
| **Profile** | View profile, edit (username change, email uniqueness), delete account with cascade |
| **Friends** | Page renders, search input, empty state, shows friend list, hides non-friends |
| **Public profiles** | Login required, displays name/username (no email/phone), avatar, friend badge, public wishlists/events/activities shown, private items hidden, empty states, 404 |
| **CRUD views** | Create/edit/delete for wishlists, items, events, activities — login required, form display, success, validation, messages, user isolation (404 for other users) |
| **Wishlists index** | Shows user's wishlists, item counts, action buttons, links to detail, empty state, isolation |
| **Item detail** | Displays info, OG meta tags, purchase/undo buttons, edit/delete, view counter, superuser-only logs |
| **Purchase/Undo** | Login required, form, success + event + email, validation, redirects |
| **Visit store** | Redirects, click tracking, no-URL fallback |
| **Friendship** | Create, duplicate rejected, reverse allowed, ordering, cascade delete |
| **Auto-friend signal** | New user auto-friends admin, admin doesn't self-friend, no duplicate on save, skips if admin missing, works via registration |
| **Email utilities** | Correct content, skips when not configured, handles API failures |
| **OG meta tags** | Present on all pages, item detail overrides |
| **Mobile layout** | Viewport meta, sticky header, nav elements |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
