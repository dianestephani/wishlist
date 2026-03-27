# Wishlist App

A social platform for creating wishlists, events, and activities — and sharing them with friends. Built with Python/Django.

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. Admin panel at `/admin/`.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Production | Postgres connection string (SQLite locally) |
| `DJANGO_SECRET_KEY` | Production | Django secret key |
| `DEBUG` | No | Defaults to `True` |
| `ALLOWED_HOSTS` | Production | Comma-separated hostnames |
| `SUPABASE_S3_ACCESS_KEY` | For images | Supabase Storage access key |
| `SUPABASE_S3_SECRET_KEY` | For images | Supabase Storage secret key |

## Features

### Wishlists, Events & Activities
- Create multiple wishlists with items (title, price, URL, category, brand, store, image, notes)
- Create events with date, start/end times, address, notes
- Create activities with location and notes
- Full CRUD on all entities. `is_public` visibility toggle
- Mark items as purchased (with disclaimer checkbox), undo with "Just kidding!"
- Store click tracking, item view counts, activity logs (superuser only)

### Social
- **Friends** — Search by username/email/phone, send requests, accept/deny, remove. Mutual friendships
- **Friend profiles** — View a friend's wishlists (with items + purchase buttons), events, and activities. Friends list visible. Non-friends see "Add Friend"
- **Direct messaging** — Threaded conversations between friends. New Message page to pick a friend. Subject + content per message
- **Activity feed** — Notifications for purchases/undos with Reply button. Separate pages for Messages, Activity, and Friend Requests
- **Notification badge** — Unread count (messages + notifications + friend requests) shown on bell icon across all pages
- **Auto-friend** — New users automatically befriend admin + admin receives signup notification (temporary)

### Auth & Profiles
- Registration, login, logout with custom User model (email, phone)
- User profiles with edit (including username), delete account with cascade
- Auto-generated avatar icons — circular with initials, random color from palette

### UI
- Dark glassmorphism theme with disco ball background, Poppins font
- Responsive — hamburger menu + bell icon on mobile, sticky navbar
- "Create +" dropdown with modals for wishlists, events, activities
- Flash messages after every action
- OG meta tags for link previews

### Infrastructure
- **Database:** Postgres (Supabase) in production, SQLite locally
- **Static files:** WhiteNoise
- **Images:** Supabase Storage (S3-compatible)
- **Deployment:** Vercel

## Models

User, Wishlist, WishlistItem, Event, Activity, Purchase, Friendship, FriendRequest, Conversation, Message, Notification, ItemEvent, ItemView, StoreClick

## URL Routes

| URL | Description |
| --- | --- |
| `/` | Dashboard |
| `/wishlist/` | All wishlists |
| `/wishlist/<id>/` | Wishlist detail with items |
| `/wishlist/<id>/edit/` | Edit wishlist |
| `/wishlist/<id>/delete/` | Delete wishlist |
| `/wishlist/<id>/add-item/` | Add item |
| `/item/<id>/` | Item detail |
| `/item/<id>/edit/` | Edit item |
| `/item/<id>/delete/` | Delete item |
| `/item/<id>/visit-store/` | Tracked store redirect |
| `/item/<id>/purchase/` | Mark purchased |
| `/item/<id>/undo-purchase/` | Undo purchase |
| `/events/` | All events |
| `/events/<id>/` | Event detail |
| `/events/<id>/edit/` | Edit event |
| `/events/<id>/delete/` | Delete event |
| `/activities/` | All activities |
| `/activities/<id>/edit/` | Edit activity |
| `/activities/<id>/delete/` | Delete activity |
| `/create/wishlist/` | Create wishlist |
| `/create/event/` | Create event |
| `/create/activity/` | Create activity |
| `/inbox/` | Message inbox |
| `/inbox/new/` | New message (pick friend) |
| `/conversation/<id>/` | Conversation thread |
| `/message/<user_id>/` | Start/continue conversation |
| `/activity/` | Activity feed |
| `/profile/` | Your profile |
| `/profile/edit/` | Edit profile |
| `/profile/delete/` | Delete account |
| `/friends/` | Friends + search |
| `/friends/requests/` | Pending friend requests |
| `/friends/add/<id>/` | Send friend request |
| `/friends/request/<id>/accept/` | Accept request |
| `/friends/request/<id>/deny/` | Deny request |
| `/friends/remove/<id>/` | Remove friend |
| `/users/<username>/` | Public profile |
| `/users/<username>/wishlist/<id>/` | Friend's wishlist |
| `/users/<username>/event/<id>/` | Friend's event |
| `/users/<username>/activity/<id>/` | Friend's activity |
| `/api/notifications/` | Item activity JSON |
| `/api/activity/` | Notification feed JSON |
| `/api/messages/` | Unread count JSON |
| `/api/friend-requests/` | Friend requests JSON |
| `/register/` | Registration |
| `/login/` | Login |
| `/logout/` | Logout |

## Testing

351 tests. Run with:

```bash
python manage.py test wishlist
python manage.py test --verbosity=2
```

### Coverage

| Area | Tests |
| --- | --- |
| **Models** | User (avatar, initials), Wishlist, WishlistItem, Event, Activity, Purchase, ItemEvent, ItemView, StoreClick, Friendship, FriendRequest, Conversation, Message, Notification |
| **Forms** | Profile, Registration, Event (time validation), Activity, Wishlist, WishlistItem, Purchase, UndoPurchase, Message |
| **Auth** | Register, login, logout with messages and redirects |
| **Dashboard** | Personalized welcome, sections, friends row, user isolation |
| **Profile** | View, edit (username), delete with cascade |
| **Public profiles** | Friend/non-friend views, restricted content, pending badge, friends list, friend-of-friend |
| **Friend content** | View friend's wishlists/events/activities, non-friend 404 |
| **Friends** | Search, add/accept/deny/remove, badges |
| **Friend requests page** | Pending requests, accept/deny, empty state |
| **Messaging** | Inbox, conversations, replies, mark read, permissions, new message page |
| **Activity feed** | Notifications, reply buttons, user isolation |
| **Unread counts** | Context processor — messages, notifications, friend requests, badge display |
| **Purchase integration** | Creates notification, message only with custom text, self-purchase skipped |
| **Auto-friend signal** | Mutual friendship, admin notification, edge cases |
| **CRUD** | Create/edit/delete for wishlists, items, events, activities — validation, user isolation |
| **Wishlists index** | Wishlist cards, item counts, action buttons |
| **Item detail** | Info, OG tags, purchase/undo, edit/delete, view counter, superuser logs |
| **APIs** | Notifications, activity, messages, friend requests — JSON, auth, isolation |
| **OG meta tags** | Title, description, image on all pages |
| **Mobile** | Viewport meta, nav elements |

## License

MIT — see [LICENSE](LICENSE).
