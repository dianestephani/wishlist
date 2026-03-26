from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import ActivityForm, EventForm, ProfileForm, PurchaseForm, RegistrationForm, UndoPurchaseForm, WishlistForm, WishlistItemForm
from .models import Activity, Event, FriendRequest, Friendship, ItemEvent, ItemView, Purchase, StoreClick, Wishlist, WishlistItem

User = get_user_model()


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------
class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone_number="555-1234",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.phone_number, "555-1234")
        self.assertEqual(str(user), "test@example.com")

    def test_email_is_unique(self):
        User.objects.create_user(
            username="user1", email="dupe@example.com", password="pass123"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="user2", email="dupe@example.com", password="pass123"
            )

    def test_phone_number_blank_by_default(self):
        user = User.objects.create_user(
            username="nophone", email="no@phone.com", password="pass123"
        )
        self.assertEqual(user.phone_number, "")


class WishlistItemModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass123"
        )

    def test_create_item_defaults(self):
        item = WishlistItem.objects.create(user=self.user, title="Test Item")
        self.assertEqual(item.status, WishlistItem.Status.AVAILABLE)
        self.assertEqual(str(item), "Test Item")

    def test_item_ordering_newest_first(self):
        item1 = WishlistItem.objects.create(user=self.user, title="First")
        item2 = WishlistItem.objects.create(user=self.user, title="Second")
        items = list(WishlistItem.objects.all())
        self.assertEqual(items[0], item2)
        self.assertEqual(items[1], item1)

    def test_item_optional_fields(self):
        item = WishlistItem.objects.create(
            user=self.user,
            title="Minimal",
        )
        self.assertEqual(item.product_url, "")
        self.assertIsNone(item.price)
        self.assertEqual(item.category, "")
        self.assertEqual(item.brand, "")
        self.assertEqual(item.store, "")

    def test_item_cascade_delete_with_user(self):
        WishlistItem.objects.create(user=self.user, title="Gone soon")
        self.user.delete()
        self.assertEqual(WishlistItem.objects.count(), 0)


class PurchaseModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass123"
        )
        self.buyer = User.objects.create_user(
            username="buyer", email="buyer@example.com", password="pass123"
        )
        self.item = WishlistItem.objects.create(
            user=self.owner, title="Gift"
        )

    def test_create_purchase(self):
        purchase = Purchase.objects.create(
            item=self.item,
            purchased_by=self.buyer,
            message="Happy birthday!",
        )
        self.assertEqual(purchase.purchased_by, self.buyer)
        self.assertIn("Gift", str(purchase))
        self.assertIn("buyer@example.com", str(purchase))

    def test_purchase_is_one_to_one(self):
        Purchase.objects.create(item=self.item, purchased_by=self.buyer)
        with self.assertRaises(Exception):
            Purchase.objects.create(item=self.item, purchased_by=self.owner)

    def test_purchase_cascade_delete_with_item(self):
        Purchase.objects.create(item=self.item, purchased_by=self.buyer)
        self.item.delete()
        self.assertEqual(Purchase.objects.count(), 0)


class ItemEventModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass123"
        )
        self.actor = User.objects.create_user(
            username="actor", email="actor@example.com", password="pass123"
        )
        self.item = WishlistItem.objects.create(user=self.owner, title="Gift")

    def test_create_purchased_event(self):
        event = ItemEvent.objects.create(
            item=self.item,
            event_type=ItemEvent.EventType.PURCHASED,
            user=self.actor,
            message="Got it!",
        )
        self.assertEqual(event.event_type, "purchased")
        self.assertIn("Gift", str(event))
        self.assertIn("actor@example.com", str(event))

    def test_create_undone_event(self):
        event = ItemEvent.objects.create(
            item=self.item,
            event_type=ItemEvent.EventType.UNDONE,
            user=self.actor,
        )
        self.assertEqual(event.event_type, "undone")

    def test_events_ordered_newest_first(self):
        e1 = ItemEvent.objects.create(
            item=self.item, event_type=ItemEvent.EventType.PURCHASED, user=self.actor,
        )
        e2 = ItemEvent.objects.create(
            item=self.item, event_type=ItemEvent.EventType.UNDONE, user=self.actor,
        )
        events = list(ItemEvent.objects.all())
        self.assertEqual(events[0], e2)
        self.assertEqual(events[1], e1)

    def test_cascade_delete_with_item(self):
        ItemEvent.objects.create(
            item=self.item, event_type=ItemEvent.EventType.PURCHASED, user=self.actor,
        )
        self.item.delete()
        self.assertEqual(ItemEvent.objects.count(), 0)


class ItemViewModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass123"
        )
        self.viewer = User.objects.create_user(
            username="viewer", email="viewer@example.com", password="pass123"
        )
        self.item = WishlistItem.objects.create(user=self.owner, title="Watched")

    def test_create_view_record(self):
        view = ItemView.objects.create(item=self.item, user=self.viewer, count=3)
        self.assertEqual(view.count, 3)
        self.assertIn("Watched", str(view))
        self.assertIn("3x", str(view))

    def test_unique_per_user_per_item(self):
        ItemView.objects.create(item=self.item, user=self.viewer, count=1)
        with self.assertRaises(Exception):
            ItemView.objects.create(item=self.item, user=self.viewer, count=1)

    def test_multiple_users_can_view_same_item(self):
        ItemView.objects.create(item=self.item, user=self.owner, count=2)
        ItemView.objects.create(item=self.item, user=self.viewer, count=5)
        self.assertEqual(ItemView.objects.filter(item=self.item).count(), 2)

    def test_cascade_delete_with_item(self):
        ItemView.objects.create(item=self.item, user=self.viewer, count=1)
        self.item.delete()
        self.assertEqual(ItemView.objects.count(), 0)


class StoreClickModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass123"
        )
        self.clicker = User.objects.create_user(
            username="clicker", email="clicker@example.com", password="pass123"
        )
        self.item = WishlistItem.objects.create(
            user=self.owner, title="Clickable", product_url="https://example.com"
        )

    def test_create_store_click(self):
        click = StoreClick.objects.create(item=self.item, user=self.clicker)
        self.assertIn("Clickable", str(click))
        self.assertIn("clicker@example.com", str(click))

    def test_multiple_clicks_create_multiple_records(self):
        StoreClick.objects.create(item=self.item, user=self.clicker)
        StoreClick.objects.create(item=self.item, user=self.clicker)
        StoreClick.objects.create(item=self.item, user=self.owner)
        self.assertEqual(StoreClick.objects.filter(item=self.item).count(), 3)

    def test_ordered_newest_first(self):
        c1 = StoreClick.objects.create(item=self.item, user=self.clicker)
        c2 = StoreClick.objects.create(item=self.item, user=self.clicker)
        clicks = list(StoreClick.objects.all())
        self.assertEqual(clicks[0], c2)
        self.assertEqual(clicks[1], c1)

    def test_cascade_delete_with_item(self):
        StoreClick.objects.create(item=self.item, user=self.clicker)
        self.item.delete()
        self.assertEqual(StoreClick.objects.count(), 0)


class EventModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="creator", email="creator@example.com", password="pass123"
        )

    def test_create_event(self):
        from datetime import date, time
        event = Event.objects.create(
            owner=self.user,
            title="Birthday Party",
            date=date(2026, 7, 15),
            start_time=time(18, 0),
            end_time=time(22, 0),
            address="123 Main St",
            notes="Bring cake",
        )
        self.assertEqual(str(event), "Birthday Party")
        self.assertEqual(event.owner, self.user)

    def test_optional_fields(self):
        from datetime import date
        event = Event.objects.create(
            owner=self.user, title="Simple Event", date=date.today()
        )
        self.assertIsNone(event.start_time)
        self.assertIsNone(event.end_time)
        self.assertEqual(event.address, "")
        self.assertEqual(event.notes, "")

    def test_ordering_by_date_desc(self):
        from datetime import date
        e1 = Event.objects.create(owner=self.user, title="Old", date=date(2026, 1, 1))
        e2 = Event.objects.create(owner=self.user, title="New", date=date(2026, 12, 1))
        events = list(Event.objects.all())
        self.assertEqual(events[0], e2)
        self.assertEqual(events[1], e1)

    def test_cascade_delete_with_user(self):
        from datetime import date
        Event.objects.create(owner=self.user, title="Gone", date=date.today())
        self.user.delete()
        self.assertEqual(Event.objects.count(), 0)


class ActivityModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="creator", email="creator@example.com", password="pass123"
        )

    def test_create_activity(self):
        activity = Activity.objects.create(
            owner=self.user,
            title="Hiking",
            location="Seattle, WA",
            notes="Bring water",
        )
        self.assertEqual(str(activity), "Hiking")
        self.assertEqual(activity.owner, self.user)

    def test_optional_fields(self):
        activity = Activity.objects.create(
            owner=self.user, title="Reading"
        )
        self.assertEqual(activity.location, "")
        self.assertEqual(activity.notes, "")

    def test_ordering_newest_first(self):
        a1 = Activity.objects.create(owner=self.user, title="First")
        a2 = Activity.objects.create(owner=self.user, title="Second")
        activities = list(Activity.objects.all())
        self.assertEqual(activities[0], a2)
        self.assertEqual(activities[1], a1)

    def test_cascade_delete_with_user(self):
        Activity.objects.create(owner=self.user, title="Gone")
        self.user.delete()
        self.assertEqual(Activity.objects.count(), 0)


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------
class RegistrationFormTests(TestCase):
    def get_valid_data(self):
        return {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "phone_number": "555-0000",
            "password1": "securePass99!",
            "password2": "securePass99!",
        }

    def test_valid_form(self):
        form = RegistrationForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid())

    def test_missing_required_fields(self):
        form = RegistrationForm(data={})
        self.assertFalse(form.is_valid())
        for field in ["username", "first_name", "last_name", "email", "password1", "password2"]:
            self.assertIn(field, form.errors)

    def test_phone_number_optional(self):
        data = self.get_valid_data()
        data["phone_number"] = ""
        form = RegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            username="existing", email="taken@example.com", password="pass123"
        )
        data = self.get_valid_data()
        data["email"] = "taken@example.com"
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_password_mismatch(self):
        data = self.get_valid_data()
        data["password2"] = "differentPass99!"
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())


class PurchaseFormTests(TestCase):
    def test_valid_with_confirm(self):
        form = PurchaseForm(data={"confirm": True, "message": ""})
        self.assertTrue(form.is_valid())

    def test_invalid_without_confirm(self):
        form = PurchaseForm(data={"confirm": False, "message": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("confirm", form.errors)

    def test_message_optional(self):
        form = PurchaseForm(data={"confirm": True})
        self.assertTrue(form.is_valid())

    def test_valid_with_message(self):
        form = PurchaseForm(data={"confirm": True, "message": "Got it!"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["message"], "Got it!")


class UndoPurchaseFormTests(TestCase):
    def test_valid_empty(self):
        form = UndoPurchaseForm(data={})
        self.assertTrue(form.is_valid())

    def test_valid_with_message(self):
        form = UndoPurchaseForm(data={"message": "Oops, sorry!"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["message"], "Oops, sorry!")


class EventFormTests(TestCase):
    def get_valid_data(self):
        return {
            "title": "Birthday Party",
            "date": "2026-07-15",
            "start_time": "18:00",
            "end_time": "22:00",
            "address": "123 Main St",
            "notes": "",
        }

    def test_valid_form(self):
        form = EventForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid())

    def test_title_required(self):
        data = self.get_valid_data()
        data["title"] = ""
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_date_required(self):
        data = self.get_valid_data()
        data["date"] = ""
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_start_time_required(self):
        data = self.get_valid_data()
        data["start_time"] = ""
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("start_time", form.errors)

    def test_end_time_required(self):
        data = self.get_valid_data()
        data["end_time"] = ""
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("end_time", form.errors)

    def test_address_required(self):
        data = self.get_valid_data()
        data["address"] = ""
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("address", form.errors)

    def test_notes_optional(self):
        data = self.get_valid_data()
        data["notes"] = ""
        form = EventForm(data=data)
        self.assertTrue(form.is_valid())

    def test_end_time_before_start_time_invalid(self):
        data = self.get_valid_data()
        data["start_time"] = "22:00"
        data["end_time"] = "18:00"
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("end_time", form.errors)

    def test_end_time_equal_to_start_time_invalid(self):
        data = self.get_valid_data()
        data["start_time"] = "18:00"
        data["end_time"] = "18:00"
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("end_time", form.errors)


class ActivityFormTests(TestCase):
    def test_valid_form(self):
        form = ActivityForm(data={
            "title": "Hiking",
            "location": "Seattle, WA",
            "notes": "",
        })
        self.assertTrue(form.is_valid())

    def test_title_required(self):
        form = ActivityForm(data={"title": "", "location": "Seattle, WA"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_location_required(self):
        form = ActivityForm(data={"title": "Hiking", "location": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("location", form.errors)

    def test_notes_optional(self):
        form = ActivityForm(data={
            "title": "Hiking",
            "location": "Seattle, WA",
        })
        self.assertTrue(form.is_valid())

    def test_valid_with_notes(self):
        form = ActivityForm(data={
            "title": "Hiking",
            "location": "Seattle, WA",
            "notes": "Bring water",
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["notes"], "Bring water")


# ---------------------------------------------------------------------------
# Auth view tests
# ---------------------------------------------------------------------------
class RegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse("wishlist:register")

    def test_get_register_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/register.html")

    def test_successful_registration(self):
        response = self.client.post(self.url, {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "password1": "securePass99!",
            "password2": "securePass99!",
        })
        self.assertRedirects(response, reverse("wishlist:dashboard"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_successful_registration_shows_message(self):
        response = self.client.post(self.url, {
            "username": "msguser",
            "first_name": "Msg",
            "last_name": "User",
            "email": "msg@example.com",
            "password1": "securePass99!",
            "password2": "securePass99!",
        }, follow=True)
        self.assertContains(response, "Welcome")

    def test_registration_logs_user_in(self):
        self.client.post(self.url, {
            "username": "autouser",
            "first_name": "Auto",
            "last_name": "Login",
            "email": "auto@example.com",
            "password1": "securePass99!",
            "password2": "securePass99!",
        })
        response = self.client.get(reverse("wishlist:index"))
        self.assertEqual(response.status_code, 200)

    def test_invalid_registration_shows_errors(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/register.html")

    def test_authenticated_user_redirected(self):
        User.objects.create_user(username="u", email="u@e.com", password="pass123")
        self.client.login(username="u", password="pass123")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("wishlist:dashboard"))


class LoginViewTests(TestCase):
    def setUp(self):
        self.url = reverse("wishlist:login")
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

    def test_get_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/login.html")

    def test_successful_login(self):
        response = self.client.post(self.url, {
            "username": "testuser",
            "password": "pass123",
        })
        self.assertRedirects(response, reverse("wishlist:dashboard"))

    def test_successful_login_shows_message(self):
        response = self.client.post(self.url, {
            "username": "testuser",
            "password": "pass123",
        }, follow=True)
        self.assertContains(response, "Welcome back")

    def test_invalid_login(self):
        response = self.client.post(self.url, {
            "username": "testuser",
            "password": "wrong",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/login.html")

    def test_authenticated_user_redirected(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("wishlist:dashboard"))


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

    def test_logout_redirects_to_login(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("wishlist:logout"))
        self.assertRedirects(response, reverse("wishlist:login"))

    def test_logout_shows_message(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("wishlist:logout"), follow=True)
        self.assertContains(response, "logged out")

    def test_logout_clears_session(self):
        self.client.login(username="testuser", password="pass123")
        self.client.get(reverse("wishlist:logout"))
        response = self.client.get(reverse("wishlist:dashboard"))
        self.assertRedirects(response, f"{reverse('wishlist:login')}?next={reverse('wishlist:dashboard')}")


# ---------------------------------------------------------------------------
# Dashboard view tests
# ---------------------------------------------------------------------------
class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:dashboard")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('wishlist:login')}?next={self.url}")

    def test_renders_dashboard_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/dashboard.html")

    def test_shows_welcome_message(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Welcome")

    def test_shows_three_sections(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Wishlists")
        self.assertContains(response, "Events")
        self.assertContains(response, "Activities")

    def test_shows_wishlist_title_and_date(self):
        wl = Wishlist.objects.create(owner=self.user, name="My Birthday List")
        response = self.client.get(self.url)
        self.assertContains(response, "My Birthday List")

    def test_shows_empty_wishlists(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No wishlists yet")

    def test_shows_event_title_and_date(self):
        from datetime import date
        Event.objects.create(
            owner=self.user, title="Birthday Party", date=date.today()
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Birthday Party")

    def test_shows_empty_events(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No events yet")

    def test_shows_recent_activities(self):
        Activity.objects.create(owner=self.user, title="Hiking Trip")
        response = self.client.get(self.url)
        self.assertContains(response, "Hiking Trip")

    def test_shows_empty_activities(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No activities yet")

    def test_does_not_show_other_users_wishlists(self):
        other = User.objects.create_user(
            username="other", email="other@example.com", password="pass123"
        )
        Wishlist.objects.create(owner=other, name="Not My List")
        response = self.client.get(self.url)
        self.assertNotContains(response, "Not My List")

    def test_welcome_shows_first_name(self):
        self.user.first_name = "Diane"
        self.user.save()
        response = self.client.get(self.url)
        self.assertContains(response, "Welcome, Diane")

    def test_welcome_falls_back_to_username(self):
        self.user.first_name = ""
        self.user.save()
        response = self.client.get(self.url)
        self.assertContains(response, f"Welcome, {self.user.username}")

    def test_does_not_show_other_users_events(self):
        from datetime import date
        other = User.objects.create_user(
            username="other2", email="other2@example.com", password="pass123"
        )
        Event.objects.create(owner=other, title="Secret Party", date=date.today())
        response = self.client.get(self.url)
        self.assertNotContains(response, "Secret Party")

    def test_does_not_show_other_users_activities(self):
        other = User.objects.create_user(
            username="other3", email="other3@example.com", password="pass123"
        )
        Activity.objects.create(owner=other, title="Private Hike")
        response = self.client.get(self.url)
        self.assertNotContains(response, "Private Hike")

    def test_cards_link_to_correct_pages(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("wishlist:index"))
        self.assertContains(response, reverse("wishlist:events"))
        self.assertContains(response, reverse("wishlist:activities"))

    def test_shows_friends_section(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Friends")

    def test_shows_friends_in_dashboard(self):
        friend = User.objects.create_user(
            username="buddy", email="buddy@example.com", password="pass123",
            first_name="Best", last_name="Friend",
        )
        Friendship.objects.create(user=self.user, friend=friend)
        response = self.client.get(self.url)
        self.assertContains(response, "Best Friend")
        self.assertContains(response, reverse("wishlist:public_profile", args=[friend.username]))

    def test_does_not_show_non_friends(self):
        stranger = User.objects.create_user(
            username="stranger", email="stranger@example.com", password="pass123",
            first_name="Some", last_name="Stranger",
        )
        response = self.client.get(self.url)
        self.assertNotContains(response, "Some Stranger")

    def test_shows_empty_friends(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No friends yet")


# ---------------------------------------------------------------------------
# Events list view tests
# ---------------------------------------------------------------------------
class EventsListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:events")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_renders_events_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/events.html")

    def test_shows_user_events(self):
        from datetime import date
        Event.objects.create(owner=self.user, title="My Party", date=date.today())
        response = self.client.get(self.url)
        self.assertContains(response, "My Party")

    def test_does_not_show_other_users_events(self):
        from datetime import date
        other = User.objects.create_user(
            username="other", email="other@example.com", password="pass123"
        )
        Event.objects.create(owner=other, title="Not My Party", date=date.today())
        response = self.client.get(self.url)
        self.assertNotContains(response, "Not My Party")

    def test_shows_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No events yet")

    def test_has_back_link(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("wishlist:dashboard"))


# ---------------------------------------------------------------------------
# Activities list view tests
# ---------------------------------------------------------------------------
class ActivitiesListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:activities")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_renders_activities_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/activities.html")

    def test_shows_user_activities(self):
        Activity.objects.create(
            owner=self.user, title="Beach Day", location="Santa Cruz, CA"
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Beach Day")
        self.assertContains(response, "Santa Cruz, CA")

    def test_shows_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No activities yet")

    def test_has_back_link(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("wishlist:dashboard"))


# ---------------------------------------------------------------------------
# Create view tests
# ---------------------------------------------------------------------------
class CreateWishlistViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:create_wishlist")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/create_wishlist.html")

    def test_successful_create(self):
        response = self.client.post(self.url, {
            "name": "New List", "description": "Test",
            "item-title": "", "item-product_url": "", "item-price": "",
            "item-category": "", "item-brand": "", "item-store": "", "item-notes": "",
        })
        self.assertEqual(Wishlist.objects.count(), 1)
        wl = Wishlist.objects.first()
        self.assertEqual(wl.name, "New List")
        self.assertEqual(wl.owner, self.user)

    def test_shows_success_message(self):
        response = self.client.post(self.url, {
            "name": "New List",
            "item-title": "", "item-product_url": "", "item-price": "",
            "item-category": "", "item-brand": "", "item-store": "", "item-notes": "",
        }, follow=True)
        self.assertContains(response, "created")


class CreateEventViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:create_event")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/create_event.html")

    def test_successful_create(self):
        response = self.client.post(self.url, {
            "title": "My Party",
            "date": "2026-07-15",
            "start_time": "18:00",
            "end_time": "22:00",
            "address": "123 Main St",
        })
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.title, "My Party")
        self.assertEqual(event.owner, self.user)
        self.assertRedirects(response, reverse("wishlist:dashboard"))

    def test_invalid_times_rejected(self):
        response = self.client.post(self.url, {
            "title": "Bad Party",
            "date": "2026-07-15",
            "start_time": "22:00",
            "end_time": "18:00",
            "address": "123 Main St",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)

    def test_shows_success_message(self):
        response = self.client.post(self.url, {
            "title": "My Party",
            "date": "2026-07-15",
            "start_time": "18:00",
            "end_time": "22:00",
            "address": "123 Main St",
        }, follow=True)
        self.assertContains(response, "created")


class CreateActivityViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:create_activity")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/create_activity.html")

    def test_successful_create(self):
        response = self.client.post(self.url, {
            "title": "Beach Day",
            "location": "Santa Cruz, CA",
        })
        self.assertEqual(Activity.objects.count(), 1)
        activity = Activity.objects.first()
        self.assertEqual(activity.title, "Beach Day")
        self.assertEqual(activity.owner, self.user)
        self.assertRedirects(response, reverse("wishlist:dashboard"))

    def test_missing_location_rejected(self):
        response = self.client.post(self.url, {"title": "Hiking"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Activity.objects.count(), 0)

    def test_shows_success_message(self):
        response = self.client.post(self.url, {
            "title": "Beach Day",
            "location": "Santa Cruz, CA",
        }, follow=True)
        self.assertContains(response, "created")


# ---------------------------------------------------------------------------
# Wishlist index view tests
# ---------------------------------------------------------------------------
class IndexViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:index")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('wishlist:login')}?next={self.url}")

    def test_displays_user_wishlists(self):
        Wishlist.objects.create(owner=self.user, name="Birthday List")
        response = self.client.get(self.url)
        self.assertContains(response, "Birthday List")

    def test_does_not_display_other_users_wishlists(self):
        other = User.objects.create_user(
            username="other", email="other@example.com", password="pass123"
        )
        Wishlist.objects.create(owner=other, name="Not Mine")
        response = self.client.get(self.url)
        self.assertNotContains(response, "Not Mine")

    def test_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No wishlists yet")

    def test_shows_item_count(self):
        wl = Wishlist.objects.create(owner=self.user, name="My List")
        WishlistItem.objects.create(user=self.user, wishlist=wl, title="Item 1")
        WishlistItem.objects.create(user=self.user, wishlist=wl, title="Item 2")
        response = self.client.get(self.url)
        self.assertContains(response, "2 items")

    def test_has_action_buttons(self):
        wl = Wishlist.objects.create(owner=self.user, name="My List")
        response = self.client.get(self.url)
        self.assertContains(response, "Add Item")
        self.assertContains(response, "Edit")
        self.assertContains(response, "Delete")

    def test_wishlist_links_to_detail(self):
        wl = Wishlist.objects.create(owner=self.user, name="My List")
        response = self.client.get(self.url)
        self.assertContains(response, reverse("wishlist:wishlist_detail", args=[wl.pk]))


# ---------------------------------------------------------------------------
# Mark purchased view tests
# ---------------------------------------------------------------------------
class MarkPurchasedViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.item = WishlistItem.objects.create(
            user=self.user, title="Buy Me", price=Decimal("50.00")
        )
        self.url = reverse("wishlist:mark_purchased", args=[self.item.pk])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url, {"confirm": True})
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/purchase.html")

    def test_successful_purchase(self):
        response = self.client.post(self.url, {"confirm": True, "message": "Got it!"})
        self.assertRedirects(response, reverse("wishlist:index"))
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, WishlistItem.Status.PURCHASED)
        purchase = Purchase.objects.get(item=self.item)
        self.assertEqual(purchase.purchased_by, self.user)
        self.assertEqual(purchase.message, "Got it!")

    def test_successful_purchase_shows_message(self):
        response = self.client.post(self.url, {"confirm": True}, follow=True)
        self.assertContains(response, "marked as purchased")

    def test_purchase_creates_event(self):
        self.client.post(self.url, {"confirm": True, "message": "Bought it"})
        event = ItemEvent.objects.get(item=self.item)
        self.assertEqual(event.event_type, ItemEvent.EventType.PURCHASED)
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.message, "Bought it")

    def test_purchase_without_confirm_fails(self):
        response = self.client.post(self.url, {"confirm": False})
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, WishlistItem.Status.AVAILABLE)

    def test_already_purchased_redirects(self):
        self.item.status = WishlistItem.Status.PURCHASED
        self.item.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("wishlist:index"))

    def test_nonexistent_item_returns_404(self):
        url = reverse("wishlist:mark_purchased", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_purchase_with_optional_message(self):
        self.client.post(self.url, {"confirm": True})
        purchase = Purchase.objects.get(item=self.item)
        self.assertEqual(purchase.message, "")



# ---------------------------------------------------------------------------
# Undo purchase view tests
# ---------------------------------------------------------------------------
class UndoPurchaseViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.item = WishlistItem.objects.create(
            user=self.user,
            title="Undo Me",
            status=WishlistItem.Status.PURCHASED,
        )
        Purchase.objects.create(item=self.item, purchased_by=self.user, message="oops")
        self.url = reverse("wishlist:undo_purchase", args=[self.item.pk])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/undo_purchase.html")

    def test_successful_undo(self):
        response = self.client.post(self.url, {"message": "Sorry!"})
        self.assertRedirects(response, reverse("wishlist:index"))
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, WishlistItem.Status.AVAILABLE)
        self.assertFalse(Purchase.objects.filter(item=self.item).exists())

    def test_successful_undo_shows_message(self):
        response = self.client.post(self.url, {"message": "Sorry!"}, follow=True)
        self.assertContains(response, "reverted to available")

    def test_undo_creates_event(self):
        self.client.post(self.url, {"message": "My bad"})
        event = ItemEvent.objects.get(item=self.item, event_type=ItemEvent.EventType.UNDONE)
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.message, "My bad")

    def test_undo_without_message(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, reverse("wishlist:index"))
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, WishlistItem.Status.AVAILABLE)

    def test_undo_on_available_item_redirects(self):
        self.item.status = WishlistItem.Status.AVAILABLE
        self.item.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("wishlist:index"))

    def test_nonexistent_item_returns_404(self):
        url = reverse("wishlist:undo_purchase", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Item detail view tests
# ---------------------------------------------------------------------------
class ItemDetailViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass123"
        )
        self.item = WishlistItem.objects.create(
            user=self.owner,
            title="Detail Item",
            price=Decimal("75.00"),
            category="Tech",
            product_url="https://example.com/product",
        )
        self.url = reverse("wishlist:item_detail", args=[self.item.pk])

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_displays_item_info(self):
        self.client.login(username="owner", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/item_detail.html")
        self.assertContains(response, "Detail Item")
        self.assertContains(response, "75.00")
        self.assertContains(response, "Tech")
        self.assertContains(response, "Visit Store")

    def test_available_item_shows_purchase_button(self):
        self.client.login(username="owner", password="pass123")
        response = self.client.get(self.url)
        self.assertContains(response, "purchased this!")
        self.assertContains(response, reverse("wishlist:mark_purchased", args=[self.item.pk]))

    def test_purchased_item_shows_undo_button(self):
        self.item.status = WishlistItem.Status.PURCHASED
        self.item.save()
        self.client.login(username="owner", password="pass123")
        response = self.client.get(self.url)
        self.assertContains(response, "Just kidding!")
        self.assertContains(response, reverse("wishlist:undo_purchase", args=[self.item.pk]))

    def test_purchased_item_does_not_show_purchase_button(self):
        self.item.status = WishlistItem.Status.PURCHASED
        self.item.save()
        self.client.login(username="owner", password="pass123")
        response = self.client.get(self.url)
        self.assertNotContains(response, reverse("wishlist:mark_purchased", args=[self.item.pk]))

    def test_og_meta_tags_present(self):
        self.client.login(username="owner", password="pass123")
        response = self.client.get(self.url)
        content = response.content.decode()
        self.assertIn('og:title', content)
        self.assertIn('Detail Item', content)
        self.assertIn('og:description', content)
        self.assertIn('og:image', content)

    def test_og_description_includes_price_and_store(self):
        self.item.store = "TestStore"
        self.item.save()
        self.client.login(username="owner", password="pass123")
        response = self.client.get(self.url)
        content = response.content.decode()
        self.assertIn("75.00", content)
        self.assertIn("TestStore", content)

    def test_regular_user_cannot_see_event_log(self):
        regular = User.objects.create_user(
            username="regular", email="regular@example.com", password="pass123"
        )
        ItemEvent.objects.create(
            item=self.item,
            event_type=ItemEvent.EventType.PURCHASED,
            user=regular,
            message="Bought it",
        )
        self.client.login(username="regular", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Activity Log")
        self.assertNotContains(response, "Bought it")

    def test_superuser_can_see_event_log(self):
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass123"
        )
        ItemEvent.objects.create(
            item=self.item,
            event_type=ItemEvent.EventType.PURCHASED,
            user=self.owner,
            message="Got this one",
        )
        ItemEvent.objects.create(
            item=self.item,
            event_type=ItemEvent.EventType.UNDONE,
            user=self.owner,
            message="Never mind",
        )
        self.client.login(username="admin", password="pass123")
        response = self.client.get(self.url)
        self.assertContains(response, "Activity Log")
        self.assertContains(response, "Got this one")
        self.assertContains(response, "Never mind")
        self.assertContains(response, "Marked as Purchased")
        self.assertContains(response, "Purchase Undone")

    def test_superuser_sees_empty_log(self):
        User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass123"
        )
        self.client.login(username="admin", password="pass123")
        response = self.client.get(self.url)
        self.assertContains(response, "Activity Log")
        self.assertContains(response, "No activity yet")

    def test_view_increments_counter(self):
        self.client.login(username="owner", password="pass123")
        self.client.get(self.url)
        self.client.get(self.url)
        self.client.get(self.url)
        view = ItemView.objects.get(item=self.item, user=self.owner)
        self.assertEqual(view.count, 3)

    def test_regular_user_cannot_see_view_stats(self):
        regular = User.objects.create_user(
            username="regular", email="regular@example.com", password="pass123"
        )
        self.client.login(username="regular", password="pass123")
        self.client.get(self.url)
        response = self.client.get(self.url)
        self.assertNotContains(response, "View Count")

    def test_superuser_can_see_view_stats(self):
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass123"
        )
        # Regular user views the item
        self.client.login(username="owner", password="pass123")
        self.client.get(self.url)
        self.client.get(self.url)
        # Admin views the item
        self.client.login(username="admin", password="pass123")
        response = self.client.get(self.url)
        self.assertContains(response, "View Count")
        self.assertContains(response, "owner")

    def test_regular_user_cannot_see_store_click_log(self):
        regular = User.objects.create_user(
            username="regular", email="regular@example.com", password="pass123"
        )
        StoreClick.objects.create(item=self.item, user=regular)
        self.client.login(username="regular", password="pass123")
        response = self.client.get(self.url)
        self.assertNotContains(response, "Store Click Log")

    def test_superuser_can_see_store_click_log(self):
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass123"
        )
        StoreClick.objects.create(item=self.item, user=self.owner)
        self.client.login(username="admin", password="pass123")
        response = self.client.get(self.url)
        self.assertContains(response, "Store Click Log")
        self.assertContains(response, "owner")

    def test_nonexistent_item_returns_404(self):
        self.client.login(username="owner", password="pass123")
        url = reverse("wishlist:item_detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Visit store view tests
# ---------------------------------------------------------------------------
class VisitStoreViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.item = WishlistItem.objects.create(
            user=self.user,
            title="Store Item",
            product_url="https://example.com/product",
        )
        self.url = reverse("wishlist:visit_store", args=[self.item.pk])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_product_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://example.com/product")

    def test_creates_store_click_record(self):
        self.client.get(self.url)
        self.assertEqual(StoreClick.objects.filter(item=self.item, user=self.user).count(), 1)

    def test_multiple_clicks_create_multiple_records(self):
        self.client.get(self.url)
        self.client.get(self.url)
        self.client.get(self.url)
        self.assertEqual(StoreClick.objects.filter(item=self.item, user=self.user).count(), 3)

    def test_no_product_url_redirects_to_detail(self):
        item_no_url = WishlistItem.objects.create(user=self.user, title="No URL")
        url = reverse("wishlist:visit_store", args=[item_no_url.pk])
        response = self.client.get(url)
        self.assertRedirects(response, reverse("wishlist:item_detail", args=[item_no_url.pk]))
        self.assertEqual(StoreClick.objects.count(), 0)

    def test_nonexistent_item_returns_404(self):
        url = reverse("wishlist:visit_store", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# OG meta tag tests
# ---------------------------------------------------------------------------
class OGMetaTagTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

    def test_base_template_has_og_tags(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("wishlist:index"))
        content = response.content.decode()
        self.assertIn('og:title', content)
        self.assertIn('Wishlist App', content)
        self.assertIn('og:description', content)
        self.assertIn('social platform', content)
        self.assertIn('og:image', content)
        self.assertIn('disco-ball.jpeg', content)
        self.assertIn('twitter:card', content)

    def test_login_page_has_og_tags(self):
        response = self.client.get(reverse("wishlist:login"))
        content = response.content.decode()
        self.assertIn('Wishlist App', content)
        self.assertIn('disco-ball.jpeg', content)

    def test_register_page_has_og_tags(self):
        response = self.client.get(reverse("wishlist:register"))
        content = response.content.decode()
        self.assertIn('Wishlist App', content)
        self.assertIn('disco-ball.jpeg', content)


# ---------------------------------------------------------------------------
# Mobile / responsive layout tests
# ---------------------------------------------------------------------------
class MobileLayoutTests(TestCase):
    """Verify that templates include proper mobile/responsive markup."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

    def test_viewport_meta_tag_present(self):
        response = self.client.get(reverse("wishlist:login"))
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, "width=device-width")

    def test_viewport_on_index_page(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("wishlist:index"))
        self.assertContains(response, 'name="viewport"')

    def test_viewport_on_register_page(self):
        response = self.client.get(reverse("wishlist:register"))
        self.assertContains(response, 'name="viewport"')

    def test_viewport_on_item_detail(self):
        self.client.login(username="testuser", password="pass123")
        item = WishlistItem.objects.create(user=self.user, title="Mobile Test")
        url = reverse("wishlist:item_detail", args=[item.pk])
        response = self.client.get(url)
        self.assertContains(response, 'name="viewport"')

    def test_sticky_header_class(self):
        """Verify the header element is present so sticky CSS applies."""
        response = self.client.get(reverse("wishlist:login"))
        self.assertContains(response, "<header>")

    def test_nav_links_present_for_anonymous(self):
        response = self.client.get(reverse("wishlist:login"))
        self.assertContains(response, "nav-links")
        self.assertContains(response, "nav-brand")

    def test_nav_links_present_for_authenticated(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("wishlist:index"))
        self.assertContains(response, "nav-links")
        self.assertContains(response, "nav-avatar")
        self.assertContains(response, "Logout")


# ---------------------------------------------------------------------------
# Profile form tests
# ---------------------------------------------------------------------------
class ProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123",
            first_name="Test", last_name="User",
        )

    def test_valid_form(self):
        form = ProfileForm(data={
            "username": "testuser",
            "first_name": "Updated",
            "last_name": "Name",
            "email": "test@example.com",
            "phone_number": "555-1234",
        }, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_change_username(self):
        form = ProfileForm(data={
            "username": "newname",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        }, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_duplicate_username_rejected(self):
        User.objects.create_user(username="taken", email="taken@example.com", password="pass123")
        form = ProfileForm(data={
            "username": "taken",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(username="other", email="taken@example.com", password="pass123")
        form = ProfileForm(data={
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "taken@example.com",
        }, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_own_email_allowed(self):
        form = ProfileForm(data={
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        }, instance=self.user)
        self.assertTrue(form.is_valid())


# ---------------------------------------------------------------------------
# Profile view tests
# ---------------------------------------------------------------------------
class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123",
            first_name="Diane", last_name="Stephani", phone_number="555-1234",
        )
        self.client.login(username="testuser", password="pass123")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("wishlist:profile"))
        self.assertEqual(response.status_code, 302)

    def test_renders_profile(self):
        response = self.client.get(reverse("wishlist:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/profile.html")
        self.assertContains(response, "Diane")
        self.assertContains(response, "Stephani")
        self.assertContains(response, "test@example.com")
        self.assertContains(response, "555-1234")
        self.assertContains(response, "testuser")

    def test_shows_avatar_initials(self):
        response = self.client.get(reverse("wishlist:profile"))
        self.assertContains(response, "profile-avatar")

    def test_has_edit_and_delete_links(self):
        response = self.client.get(reverse("wishlist:profile"))
        self.assertContains(response, reverse("wishlist:edit_profile"))
        self.assertContains(response, reverse("wishlist:delete_account"))


class EditProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123",
            first_name="Old", last_name="Name",
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:edit_profile")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/edit_profile.html")

    def test_successful_update(self):
        response = self.client.post(self.url, {
            "username": "testuser",
            "first_name": "New",
            "last_name": "Name",
            "email": "new@example.com",
            "phone_number": "555-9999",
        })
        self.assertRedirects(response, reverse("wishlist:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.email, "new@example.com")

    def test_change_username(self):
        self.client.post(self.url, {
            "username": "newname",
            "first_name": "Old",
            "last_name": "Name",
            "email": "test@example.com",
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newname")

    def test_shows_success_message(self):
        response = self.client.post(self.url, {
            "username": "testuser",
            "first_name": "New",
            "last_name": "Name",
            "email": "test@example.com",
        }, follow=True)
        self.assertContains(response, "updated")


class DeleteAccountViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123",
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:delete_account")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_confirmation(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete")
        self.assertContains(response, "cannot be undone")

    def test_successful_delete(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("wishlist:login"))
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_cascades_user_data(self):
        Wishlist.objects.create(owner=self.user, name="My List")
        WishlistItem.objects.create(user=self.user, title="My Item")
        self.client.post(self.url)
        self.assertEqual(Wishlist.objects.count(), 0)
        self.assertEqual(WishlistItem.objects.count(), 0)


# ---------------------------------------------------------------------------
# Friends view tests
# ---------------------------------------------------------------------------
class FriendsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:friends")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_renders_friends_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/friends.html")
        self.assertContains(response, "Friends")
        self.assertContains(response, "My Friends")

    def test_has_search_input(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Search")
        self.assertContains(response, 'name="q"')

    def test_shows_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No friends added yet")

    def test_shows_friend_list(self):
        friend = User.objects.create_user(
            username="buddy", email="buddy@example.com", password="pass123",
            first_name="Jane", last_name="Doe",
        )
        Friendship.objects.create(user=self.user, friend=friend)
        response = self.client.get(self.url)
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, reverse("wishlist:public_profile", args=[friend.username]))

    def test_does_not_show_non_friends(self):
        User.objects.create_user(
            username="stranger", email="stranger@example.com", password="pass123",
            first_name="Not", last_name="Friend",
        )
        response = self.client.get(self.url)
        self.assertNotContains(response, "Not Friend")


# ---------------------------------------------------------------------------
# Public profile view tests
# ---------------------------------------------------------------------------
class PublicProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123",
        )
        self.friend = User.objects.create_user(
            username="buddy", email="buddy@example.com", password="pass123",
            first_name="Jane", last_name="Doe", phone_number="555-9999",
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:public_profile", args=[self.friend.username])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_renders_public_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishlist/public_profile.html")
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "@buddy")

    def test_does_not_expose_email(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "buddy@example.com")

    def test_does_not_expose_phone(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "555-9999")

    def test_shows_friend_badge_if_friends(self):
        Friendship.objects.create(user=self.user, friend=self.friend)
        response = self.client.get(self.url)
        self.assertContains(response, "You are friends")

    def test_no_friend_badge_if_not_friends(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "You are friends")

    def test_shows_avatar_initials(self):
        response = self.client.get(self.url)
        self.assertContains(response, "profile-avatar")

    def test_nonexistent_user_returns_404(self):
        url = reverse("wishlist:public_profile", args=["nonexistent_user"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_non_friend_cannot_see_wishlists(self):
        Wishlist.objects.create(owner=self.friend, name="Public List", is_public=True)
        response = self.client.get(self.url)
        self.assertNotContains(response, "Public List")
        self.assertContains(response, "Add")

    def test_non_friend_sees_restricted_message(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Add")
        self.assertContains(response, "friend to see their")

    def test_non_friend_with_pending_request(self):
        FriendRequest.objects.create(from_user=self.user, to_user=self.friend)
        response = self.client.get(self.url)
        self.assertContains(response, "pending")

    def test_friend_sees_public_wishlists(self):
        Friendship.objects.create(user=self.user, friend=self.friend)
        Wishlist.objects.create(owner=self.friend, name="Public List", is_public=True)
        response = self.client.get(self.url)
        self.assertContains(response, "Public List")

    def test_friend_sees_empty_wishlists(self):
        Friendship.objects.create(user=self.user, friend=self.friend)
        response = self.client.get(self.url)
        self.assertContains(response, "No public wishlists")

    def test_friend_hides_private_wishlists(self):
        Friendship.objects.create(user=self.user, friend=self.friend)
        Wishlist.objects.create(owner=self.friend, name="Secret List", is_public=False)
        response = self.client.get(self.url)
        self.assertNotContains(response, "Secret List")

    def test_friend_sees_public_events(self):
        from datetime import date
        Friendship.objects.create(user=self.user, friend=self.friend)
        Event.objects.create(owner=self.friend, title="Public Party", date=date.today(), is_public=True)
        response = self.client.get(self.url)
        self.assertContains(response, "Public Party")

    def test_friend_hides_private_events(self):
        from datetime import date
        Friendship.objects.create(user=self.user, friend=self.friend)
        Event.objects.create(owner=self.friend, title="Secret Party", date=date.today(), is_public=False)
        response = self.client.get(self.url)
        self.assertNotContains(response, "Secret Party")

    def test_friend_sees_public_activities(self):
        Friendship.objects.create(user=self.user, friend=self.friend)
        Activity.objects.create(owner=self.friend, title="Public Hike", is_public=True)
        response = self.client.get(self.url)
        self.assertContains(response, "Public Hike")

    def test_friend_hides_private_activities(self):
        Friendship.objects.create(user=self.user, friend=self.friend)
        Activity.objects.create(owner=self.friend, title="Secret Hike", is_public=False)
        response = self.client.get(self.url)
        self.assertNotContains(response, "Secret Hike")

    def test_friend_sees_empty_sections(self):
        Friendship.objects.create(user=self.user, friend=self.friend)
        response = self.client.get(self.url)
        self.assertContains(response, "No public wishlists")
        self.assertContains(response, "No public events")
        self.assertContains(response, "No public activities")


# ---------------------------------------------------------------------------
# Edit/delete wishlist view tests
# ---------------------------------------------------------------------------
class EditWishlistViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.wl = Wishlist.objects.create(owner=self.user, name="Old Title")
        self.url = reverse("wishlist:edit_wishlist", args=[self.wl.pk])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Old Title")

    def test_successful_update(self):
        response = self.client.post(self.url, {"name": "New Title"})
        self.wl.refresh_from_db()
        self.assertEqual(self.wl.name, "New Title")

    def test_other_user_gets_404(self):
        other = User.objects.create_user(username="other", email="other@example.com", password="pass123")
        self.client.login(username="other", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


class DeleteWishlistViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.wl = Wishlist.objects.create(owner=self.user, name="Delete Me")
        self.url = reverse("wishlist:delete_wishlist", args=[self.wl.pk])

    def test_get_shows_confirmation(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Delete Me")

    def test_successful_delete(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("wishlist:dashboard"))
        self.assertEqual(Wishlist.objects.count(), 0)

    def test_shows_success_message(self):
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, "deleted")


# ---------------------------------------------------------------------------
# Add/edit/delete item view tests
# ---------------------------------------------------------------------------
class AddItemViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.wl = Wishlist.objects.create(owner=self.user, name="My List")
        self.url = reverse("wishlist:add_item", args=[self.wl.pk])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Item")

    def test_successful_add(self):
        response = self.client.post(self.url, {"title": "New Item", "price": "29.99"})
        self.assertEqual(WishlistItem.objects.count(), 1)
        item = WishlistItem.objects.first()
        self.assertEqual(item.title, "New Item")
        self.assertEqual(item.user, self.user)

    def test_shows_success_message(self):
        response = self.client.post(self.url, {"title": "New Item"}, follow=True)
        self.assertContains(response, "added")


class EditItemViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.item = WishlistItem.objects.create(user=self.user, title="Old Item")
        self.url = reverse("wishlist:edit_item", args=[self.item.pk])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Old Item")

    def test_successful_update(self):
        response = self.client.post(self.url, {"title": "Updated Item"})
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, "Updated Item")

    def test_other_user_gets_404(self):
        other = User.objects.create_user(username="other", email="other@example.com", password="pass123")
        self.client.login(username="other", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


class DeleteItemViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.item = WishlistItem.objects.create(user=self.user, title="Delete Me")
        self.url = reverse("wishlist:delete_item", args=[self.item.pk])

    def test_get_shows_confirmation(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Delete Me")

    def test_successful_delete(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("wishlist:index"))
        self.assertEqual(WishlistItem.objects.count(), 0)


# ---------------------------------------------------------------------------
# Edit/delete event view tests
# ---------------------------------------------------------------------------
class EditEventViewTests(TestCase):
    def setUp(self):
        from datetime import date, time
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.event = Event.objects.create(
            owner=self.user, title="Old Event", date=date(2026, 7, 15),
            start_time=time(18, 0), end_time=time(22, 0), address="123 Main St",
        )
        self.url = reverse("wishlist:edit_event", args=[self.event.pk])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Old Event")

    def test_successful_update(self):
        response = self.client.post(self.url, {
            "title": "New Event",
            "date": "2026-08-01",
            "start_time": "19:00",
            "end_time": "23:00",
            "address": "456 Oak Ave",
        })
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "New Event")

    def test_other_user_gets_404(self):
        other = User.objects.create_user(username="other", email="other@example.com", password="pass123")
        self.client.login(username="other", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


class DeleteEventViewTests(TestCase):
    def setUp(self):
        from datetime import date
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.event = Event.objects.create(owner=self.user, title="Delete Me", date=date.today())
        self.url = reverse("wishlist:delete_event", args=[self.event.pk])

    def test_get_shows_confirmation(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Delete Me")

    def test_successful_delete(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("wishlist:events"))
        self.assertEqual(Event.objects.count(), 0)


# ---------------------------------------------------------------------------
# Edit/delete activity view tests
# ---------------------------------------------------------------------------
class EditActivityViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.activity = Activity.objects.create(
            owner=self.user, title="Old Activity", location="Seattle, WA",
        )
        self.url = reverse("wishlist:edit_activity", args=[self.activity.pk])

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_shows_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Old Activity")

    def test_successful_update(self):
        response = self.client.post(self.url, {
            "title": "New Activity",
            "location": "Portland, OR",
        })
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.title, "New Activity")

    def test_other_user_gets_404(self):
        other = User.objects.create_user(username="other", email="other@example.com", password="pass123")
        self.client.login(username="other", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


class DeleteActivityViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.client.login(username="testuser", password="pass123")
        self.activity = Activity.objects.create(
            owner=self.user, title="Delete Me", location="Seattle, WA",
        )
        self.url = reverse("wishlist:delete_activity", args=[self.activity.pk])

    def test_get_shows_confirmation(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Delete Me")

    def test_successful_delete(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("wishlist:activities"))
        self.assertEqual(Activity.objects.count(), 0)


# ---------------------------------------------------------------------------
# Friendship model tests
# ---------------------------------------------------------------------------
class FriendshipModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass123"
        )

    def test_create_friendship(self):
        f = Friendship.objects.create(user=self.user1, friend=self.user2)
        self.assertEqual(f.user, self.user1)
        self.assertEqual(f.friend, self.user2)
        self.assertIn("user1", str(f))
        self.assertIn("user2", str(f))

    def test_duplicate_friendship_rejected(self):
        Friendship.objects.create(user=self.user1, friend=self.user2)
        with self.assertRaises(Exception):
            Friendship.objects.create(user=self.user1, friend=self.user2)

    def test_reverse_friendship_allowed(self):
        Friendship.objects.create(user=self.user1, friend=self.user2)
        Friendship.objects.create(user=self.user2, friend=self.user1)
        self.assertEqual(Friendship.objects.count(), 2)

    def test_ordering_newest_first(self):
        f1 = Friendship.objects.create(user=self.user1, friend=self.user2)
        f2 = Friendship.objects.create(user=self.user2, friend=self.user1)
        friendships = list(Friendship.objects.all())
        self.assertEqual(friendships[0], f2)
        self.assertEqual(friendships[1], f1)

    def test_cascade_delete_user(self):
        Friendship.objects.create(user=self.user1, friend=self.user2)
        self.user1.delete()
        self.assertEqual(Friendship.objects.count(), 0)

    def test_cascade_delete_friend(self):
        Friendship.objects.create(user=self.user1, friend=self.user2)
        self.user2.delete()
        self.assertEqual(Friendship.objects.count(), 0)


# ---------------------------------------------------------------------------
# Auto-friend signal tests
# ---------------------------------------------------------------------------
class AutoFriendSignalTests(TestCase):
    def setUp(self):
        self.diane = User.objects.create_user(
            username="diane", email="diane.stephani@gmail.com", password="pass123"
        )

    def test_new_user_auto_friends_diane(self):
        new_user = User.objects.create_user(
            username="newuser", email="new@example.com", password="pass123"
        )
        self.assertTrue(
            Friendship.objects.filter(user=new_user, friend=self.diane).exists()
        )

    def test_diane_does_not_self_friend(self):
        self.assertFalse(
            Friendship.objects.filter(user=self.diane, friend=self.diane).exists()
        )

    def test_no_duplicate_on_save(self):
        new_user = User.objects.create_user(
            username="newuser", email="new@example.com", password="pass123"
        )
        new_user.first_name = "Updated"
        new_user.save()
        self.assertEqual(
            Friendship.objects.filter(user=new_user, friend=self.diane).count(), 1
        )

    def test_signal_skips_if_diane_not_found(self):
        self.diane.delete()
        new_user = User.objects.create_user(
            username="newuser", email="new@example.com", password="pass123"
        )
        self.assertEqual(Friendship.objects.count(), 0)

    def test_registration_auto_friends_diane(self):
        response = self.client.post(reverse("wishlist:register"), {
            "username": "reguser",
            "first_name": "Reg",
            "last_name": "User",
            "email": "reg@example.com",
            "password1": "securePass99!",
            "password2": "securePass99!",
        })
        reg_user = User.objects.get(username="reguser")
        self.assertTrue(
            Friendship.objects.filter(user=reg_user, friend=self.diane).exists()
        )


# ---------------------------------------------------------------------------
# Notifications API tests
# ---------------------------------------------------------------------------
class NotificationsApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.other = User.objects.create_user(
            username="buyer", email="buyer@example.com", password="pass123",
            first_name="Jane",
        )
        self.client.login(username="testuser", password="pass123")
        self.item = WishlistItem.objects.create(user=self.user, title="My Item")
        self.url = reverse("wishlist:notifications_api")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_returns_json(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")

    def test_returns_empty_when_no_activity(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data["notifications"], [])

    def test_returns_item_events(self):
        ItemEvent.objects.create(
            item=self.item, event_type=ItemEvent.EventType.PURCHASED,
            user=self.other, message="Got it!",
        )
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(len(data["notifications"]), 1)
        self.assertEqual(data["notifications"][0]["item_title"], "My Item")
        self.assertEqual(data["notifications"][0]["user"], "Jane")
        self.assertIn("Purchased", data["notifications"][0]["event_type"])
        self.assertEqual(data["notifications"][0]["message"], "Got it!")

    def test_ordered_newest_first(self):
        e1 = ItemEvent.objects.create(
            item=self.item, event_type=ItemEvent.EventType.PURCHASED, user=self.other,
        )
        e2 = ItemEvent.objects.create(
            item=self.item, event_type=ItemEvent.EventType.UNDONE, user=self.other,
        )
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data["notifications"][0]["id"], e2.pk)
        self.assertEqual(data["notifications"][1]["id"], e1.pk)

    def test_only_shows_own_items_activity(self):
        other_item = WishlistItem.objects.create(user=self.other, title="Not Mine")
        ItemEvent.objects.create(
            item=other_item, event_type=ItemEvent.EventType.PURCHASED, user=self.user,
        )
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(len(data["notifications"]), 0)

    def test_limits_to_20(self):
        for i in range(25):
            ItemEvent.objects.create(
                item=self.item, event_type=ItemEvent.EventType.PURCHASED, user=self.other,
            )
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(len(data["notifications"]), 20)


# ---------------------------------------------------------------------------
# FriendRequest model tests
# ---------------------------------------------------------------------------
class FriendRequestModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", email="u1@example.com", password="pass123")
        self.user2 = User.objects.create_user(username="u2", email="u2@example.com", password="pass123")

    def test_create_request(self):
        fr = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        self.assertEqual(fr.status, FriendRequest.Status.PENDING)
        self.assertIn("u1", str(fr))
        self.assertIn("u2", str(fr))

    def test_duplicate_rejected(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        with self.assertRaises(Exception):
            FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)

    def test_reverse_allowed(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        self.assertEqual(FriendRequest.objects.count(), 2)


# ---------------------------------------------------------------------------
# Friend search tests
# ---------------------------------------------------------------------------
class FriendSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.target = User.objects.create_user(
            username="jane_doe", email="jane@example.com", password="pass123",
            first_name="Jane", last_name="Doe", phone_number="555-1234",
        )
        self.client.login(username="testuser", password="pass123")

    def test_search_by_username(self):
        response = self.client.get(reverse("wishlist:friends") + "?q=jane_doe")
        self.assertContains(response, "Jane Doe")

    def test_search_by_email(self):
        response = self.client.get(reverse("wishlist:friends") + "?q=jane@example")
        self.assertContains(response, "Jane Doe")

    def test_search_by_phone(self):
        response = self.client.get(reverse("wishlist:friends") + "?q=555-1234")
        self.assertContains(response, "Jane Doe")

    def test_excludes_self(self):
        response = self.client.get(reverse("wishlist:friends") + "?q=testuser")
        self.assertContains(response, "No users found")

    def test_no_results(self):
        response = self.client.get(reverse("wishlist:friends") + "?q=nonexistent")
        self.assertContains(response, "No users found")

    def test_shows_add_friend_button(self):
        response = self.client.get(reverse("wishlist:friends") + "?q=jane")
        self.assertContains(response, "Add Friend")

    def test_shows_already_friends_badge(self):
        Friendship.objects.create(user=self.user, friend=self.target)
        response = self.client.get(reverse("wishlist:friends") + "?q=jane")
        self.assertContains(response, "Friends")
        self.assertNotContains(response, "Add Friend")

    def test_shows_pending_badge(self):
        FriendRequest.objects.create(from_user=self.user, to_user=self.target)
        response = self.client.get(reverse("wishlist:friends") + "?q=jane")
        self.assertContains(response, "Pending")


# ---------------------------------------------------------------------------
# Send friend request tests
# ---------------------------------------------------------------------------
class SendFriendRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.target = User.objects.create_user(
            username="target", email="target@example.com", password="pass123",
            first_name="Target",
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:send_friend_request", args=[self.target.pk])

    def test_creates_pending_request(self):
        response = self.client.get(self.url)
        self.assertTrue(
            FriendRequest.objects.filter(
                from_user=self.user, to_user=self.target, status=FriendRequest.Status.PENDING
            ).exists()
        )

    def test_redirects_to_friends(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("wishlist:friends"))

    def test_no_duplicate(self):
        FriendRequest.objects.create(from_user=self.user, to_user=self.target)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user, to_user=self.target).count(), 1)

    def test_cannot_send_to_self(self):
        url = reverse("wishlist:send_friend_request", args=[self.user.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(FriendRequest.objects.count(), 0)

    def test_already_friends_skips(self):
        Friendship.objects.create(user=self.user, friend=self.target)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(FriendRequest.objects.count(), 0)


# ---------------------------------------------------------------------------
# Accept/deny friend request tests
# ---------------------------------------------------------------------------
class AcceptFriendRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.requester = User.objects.create_user(
            username="requester", email="req@example.com", password="pass123"
        )
        self.fr = FriendRequest.objects.create(from_user=self.requester, to_user=self.user)
        self.client.login(username="testuser", password="pass123")

    def test_accept_creates_mutual_friendship(self):
        url = reverse("wishlist:accept_friend_request", args=[self.fr.pk])
        self.client.get(url)
        self.assertTrue(Friendship.objects.filter(user=self.user, friend=self.requester).exists())
        self.assertTrue(Friendship.objects.filter(user=self.requester, friend=self.user).exists())

    def test_accept_updates_status(self):
        url = reverse("wishlist:accept_friend_request", args=[self.fr.pk])
        self.client.get(url)
        self.fr.refresh_from_db()
        self.assertEqual(self.fr.status, FriendRequest.Status.ACCEPTED)

    def test_accept_redirects(self):
        url = reverse("wishlist:accept_friend_request", args=[self.fr.pk])
        response = self.client.get(url)
        self.assertRedirects(response, reverse("wishlist:friends"))

    def test_cannot_accept_others_request(self):
        other = User.objects.create_user(username="other", email="o@e.com", password="pass123")
        self.client.login(username="other", password="pass123")
        url = reverse("wishlist:accept_friend_request", args=[self.fr.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DenyFriendRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.requester = User.objects.create_user(
            username="requester", email="req@example.com", password="pass123"
        )
        self.fr = FriendRequest.objects.create(from_user=self.requester, to_user=self.user)
        self.client.login(username="testuser", password="pass123")

    def test_deny_deletes_request(self):
        url = reverse("wishlist:deny_friend_request", args=[self.fr.pk])
        self.client.get(url)
        self.assertFalse(FriendRequest.objects.filter(pk=self.fr.pk).exists())

    def test_deny_does_not_create_friendship(self):
        url = reverse("wishlist:deny_friend_request", args=[self.fr.pk])
        self.client.get(url)
        self.assertEqual(Friendship.objects.count(), 0)

    def test_deny_redirects(self):
        url = reverse("wishlist:deny_friend_request", args=[self.fr.pk])
        response = self.client.get(url)
        self.assertRedirects(response, reverse("wishlist:friends"))

    def test_cannot_deny_others_request(self):
        other = User.objects.create_user(username="other", email="o@e.com", password="pass123")
        self.client.login(username="other", password="pass123")
        url = reverse("wishlist:deny_friend_request", args=[self.fr.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Friend requests API tests
# ---------------------------------------------------------------------------
class FriendRequestsApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        self.requester = User.objects.create_user(
            username="requester", email="req@example.com", password="pass123",
            first_name="Jane",
        )
        self.client.login(username="testuser", password="pass123")
        self.url = reverse("wishlist:friend_requests_api")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_returns_json(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")

    def test_returns_pending_requests(self):
        FriendRequest.objects.create(from_user=self.requester, to_user=self.user)
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(len(data["friend_requests"]), 1)
        self.assertEqual(data["friend_requests"][0]["from_user"], "Jane")

    def test_excludes_accepted_requests(self):
        FriendRequest.objects.create(
            from_user=self.requester, to_user=self.user, status=FriendRequest.Status.ACCEPTED
        )
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(len(data["friend_requests"]), 0)

    def test_excludes_requests_to_others(self):
        other = User.objects.create_user(username="other", email="o@e.com", password="pass123")
        FriendRequest.objects.create(from_user=self.requester, to_user=other)
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(len(data["friend_requests"]), 0)
