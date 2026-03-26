# Wishlist App

A multi-user social platform for creating and managing wishlists, events, and activities. Built with Python and Django, featuring direct messaging, activity notifications, a friend system, and a dark glassmorphism UI.

## Prerequisites

- Python 3.10+
- pip

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/dianestephani/wishlist.git
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

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Set environment variables and start the server

```bash
export DATABASE_URL=postgres://...  # or omit for SQLite
export DJANGO_SECRET_KEY=your-secret-key
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
| `SUPABASE_S3_ACCESS_KEY` | For images | Supabase Storage S3 access key ID |
| `SUPABASE_S3_SECRET_KEY` | For images | Supabase Storage S3 secret access key |

See `.env.example` for a template.

## Features

### Core
- **Personalized dashboard** — Welcome message, 3 section cards (Wishlists, Events, Activities), friends row, "Create +" dropdown with modals
- **Wishlists** — Create multiple wishlists with items (title, price, URL, category, brand, store, image, notes). Full CRUD
- **Events** — Create events with date, start/end times, address, notes. Full CRUD
- **Activities** — Track activities with location and notes. Full CRUD
- **Items** — Mark as purchased with disclaimer checkbox, undo with "Just kidding!", tracked store clicks

### Social
- **Friend system** — Search by username/email/phone, send friend requests, accept/deny via notifications. Mutual friendships
- **Direct messaging** — Threaded conversations between friends with subject + content. Only friends can message
- **Activity feed** — Notification system for wishlist actions (purchase/undo). Reply button opens conversation with prefilled subject
- **Notifications panel** — 3 tabs (Messages, Activity, Friends) with real-time AJAX loading
- **Public profiles** — `/users/<username>/` shows name, avatar, and public content. Friends see wishlists/events/activities; non-friends see "Add Friend"
- **Visibility system** — `is_public` toggle on wishlists, events, and activities

### Profile & Auth
- **User profiles** — View/edit profile (username, name, email, phone), delete account with cascade
- **Profile icons** — Auto-generated circular avatars with initials and random color from palette
- **Registration** — New users auto-friend admin (Diane) + admin receives signup notification

### UI
- **Dark glassmorphism theme** — Disco ball background, frosted glass cards, pink/purple accents, Poppins font
- **Responsive design** — Hamburger menu on mobile, sticky navbar
- **Success messages** — Flash messages after every action
- **OG meta tags** — "Wishlist App" title, disco ball image, social description

### Infrastructure
- **Database:** Postgres via Supabase (production), SQLite (local)
- **Static files:** WhiteNoise
- **Image storage:** Supabase Storage (S3-compatible)
- **Deployment:** Vercel with `@vercel/python`

## Models

| Model | Key Fields |
| --- | --- |
| **User** | username, email, phone_number, avatar_color, initials |
| **Wishlist** | owner, name, description, is_public |
| **WishlistItem** | user, wishlist, title, price, product_url, category, brand, store, image, notes, status |
| **Event** | owner, title, date, start_time, end_time, address, notes, is_public |
| **Activity** | owner, title, location, notes, is_public |
| **Purchase** | item, purchased_by, message |
| **Friendship** | user, friend (mutual — both directions) |
| **FriendRequest** | from_user, to_user, status (pending/accepted/denied) |
| **Conversation** | participants (M2M), one per user pair |
| **Message** | conversation, sender, subject, content, is_read |
| **Notification** | recipient, sender, type (wishlist/event/activity), subject, content, is_read |
| **ItemEvent** | item, event_type (purchased/undone), user, message |
| **ItemView** | item, user, count |
| **StoreClick** | item, user |

## URL Routes

| URL | View | Description |
| --- | --- | --- |
| `/` | `dashboard` | Personalized dashboard |
| `/wishlist/` | `index` | All user's wishlists |
| `/wishlist/<id>/` | `wishlist_detail` | Wishlist with items + purchase modals |
| `/wishlist/<id>/edit/` | `edit_wishlist` | Edit wishlist |
| `/wishlist/<id>/delete/` | `delete_wishlist` | Delete wishlist |
| `/wishlist/<id>/add-item/` | `add_item` | Add item to wishlist |
| `/item/<id>/` | `item_detail` | Item detail with admin logs |
| `/item/<id>/edit/` | `edit_item` | Edit item |
| `/item/<id>/delete/` | `delete_item` | Delete item |
| `/item/<id>/visit-store/` | `visit_store` | Tracked redirect to store |
| `/item/<id>/purchase/` | `mark_purchased` | Mark purchased + notification |
| `/item/<id>/undo-purchase/` | `undo_purchase` | Undo purchase + notification |
| `/events/` | `events_list` | All user's events |
| `/events/<id>/` | `event_detail` | Event detail |
| `/events/<id>/edit/` | `edit_event` | Edit event |
| `/events/<id>/delete/` | `delete_event` | Delete event |
| `/activities/` | `activities_list` | All user's activities |
| `/activities/<id>/edit/` | `edit_activity` | Edit activity |
| `/activities/<id>/delete/` | `delete_activity` | Delete activity |
| `/create/wishlist/` | `create_wishlist` | Create wishlist + optional first item |
| `/create/event/` | `create_event` | Create event |
| `/create/activity/` | `create_activity` | Create activity |
| `/inbox/` | `inbox` | Message inbox |
| `/conversation/<id>/` | `conversation_detail` | Conversation thread |
| `/message/<user_id>/` | `start_conversation` | Start/continue conversation |
| `/activity/` | `activity_feed` | Full activity feed with Reply buttons |
| `/profile/` | `profile` | User profile |
| `/profile/edit/` | `edit_profile` | Edit profile |
| `/profile/delete/` | `delete_account` | Delete account |
| `/friends/` | `friends` | Friends page with search |
| `/friends/add/<id>/` | `send_friend_request` | Send friend request |
| `/friends/request/<id>/accept/` | `accept_friend_request` | Accept request |
| `/friends/request/<id>/deny/` | `deny_friend_request` | Deny request |
| `/users/<username>/` | `public_profile` | Public user profile |
| `/api/notifications/` | `notifications_api` | Item activity JSON |
| `/api/activity/` | `activity_feed_api` | Notification feed JSON |
| `/api/messages/` | `messages_api` | Unread message count JSON |
| `/api/friend-requests/` | `friend_requests_api` | Pending friend requests JSON |
| `/register/` | `register_view` | User registration |
| `/login/` | `login_view` | User login |
| `/logout/` | `logout_view` | User logout |
| `/admin/` | Django admin | Admin panel |

## Testing

327 tests in `wishlist/tests.py` using Django's built-in test framework.

```bash
python manage.py test                    # full suite
python manage.py test wishlist           # app only
python manage.py test --verbosity=2      # verbose
```

### Test coverage

| Area | What's tested |
| --- | --- |
| **Models** | User (avatar_color, initials), Wishlist, WishlistItem, Event, Activity, Purchase, ItemEvent, ItemView, StoreClick, Friendship, FriendRequest, Conversation, Message, Notification — creation, defaults, ordering, constraints, cascade |
| **Forms** | ProfileForm (username/email uniqueness), RegistrationForm, EventForm (time validation), ActivityForm, WishlistForm, WishlistItemForm, PurchaseForm, UndoPurchaseForm, MessageForm |
| **Auth views** | Register (success, auto-login, message), Login (success, message, failure), Logout (redirect, message, session) |
| **Dashboard** | Personalized welcome, 3 sections + friends row, data display, empty states, user isolation |
| **Profile** | View, edit (username change), delete with cascade |
| **Public profiles** | Friends see public content, non-friends see restricted view + Add Friend, pending badge, no email/phone exposed |
| **Friends** | Search (username/email/phone), add friend button, already-friends badge, pending badge, empty state |
| **Friend requests** | Send, accept (mutual friendship), deny (deletes), can't accept others', can't self-add |
| **Messaging** | Inbox (conversations, unread), conversation (thread, reply, marks read, non-participant 404), start conversation (friends only, prefill subject) |
| **Activity feed** | Shows notifications, reply button, empty state, user isolation |
| **Purchase integration** | Purchase creates notification, creates message only with custom text, undo same logic, self-purchase no notification |
| **Messaging helpers** | `notify()` creates notification only, `send_message()` creates message only, `get_or_create_conversation()` idempotent |
| **Auto-friend signal** | New user gets mutual friendship with admin, admin notified of signup, no self-friend, no duplicate, skips if admin missing |
| **CRUD views** | Create/edit/delete for wishlists, items, events, activities — login required, validation, user isolation (404 for others) |
| **Wishlists index** | Shows wishlists with item counts, action buttons, isolation |
| **Item detail** | Info, OG tags, purchase/undo buttons, edit/delete, view counter, superuser-only logs |
| **Notifications API** | JSON responses, user isolation, limits, correct data |
| **OG meta tags** | "Wishlist App" title, disco ball image, social description |
| **Mobile layout** | Viewport meta, sticky header, nav elements |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
