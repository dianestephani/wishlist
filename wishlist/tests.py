from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .email import send_purchased_email, send_undo_email
from .forms import PurchaseForm, RegistrationForm, UndoPurchaseForm
from .models import ItemEvent, ItemView, Purchase, StoreClick, WishlistItem

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

    def test_shows_wishlists_section(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Wishlists")

    def test_shows_events_section(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Events")

    def test_shows_activities_section(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Activities")

    def test_shows_wishlist_items(self):
        WishlistItem.objects.create(user=self.user, title="Dashboard Item")
        response = self.client.get(self.url)
        self.assertContains(response, "Dashboard Item")

    def test_shows_empty_state_when_no_items(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No items yet")

    def test_shows_recent_events(self):
        item = WishlistItem.objects.create(user=self.user, title="Event Item")
        ItemEvent.objects.create(
            item=item, event_type=ItemEvent.EventType.PURCHASED, user=self.user
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Event Item")
        self.assertContains(response, "Marked as Purchased")

    def test_shows_empty_events(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No events yet")

    def test_shows_recent_purchases(self):
        item = WishlistItem.objects.create(user=self.user, title="Bought Item")
        Purchase.objects.create(item=item, purchased_by=self.user, message="Great find")
        response = self.client.get(self.url)
        self.assertContains(response, "Bought Item")
        self.assertContains(response, "Great find")

    def test_shows_empty_activities(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No activities yet")

    def test_does_not_show_other_users_items(self):
        other = User.objects.create_user(
            username="other", email="other@example.com", password="pass123"
        )
        WishlistItem.objects.create(user=other, title="Not My Item")
        response = self.client.get(self.url)
        self.assertNotContains(response, "Not My Item")

    def test_has_view_all_link(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("wishlist:index"))
        self.assertContains(response, "View All")


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

    def test_displays_user_items(self):
        WishlistItem.objects.create(
            user=self.user, title="My Item", price=Decimal("29.99")
        )
        response = self.client.get(self.url)
        self.assertContains(response, "My Item")
        self.assertContains(response, "29.99")

    def test_does_not_display_other_users_items(self):
        other = User.objects.create_user(
            username="other", email="other@example.com", password="pass123"
        )
        WishlistItem.objects.create(user=other, title="Not Mine")
        response = self.client.get(self.url)
        self.assertNotContains(response, "Not Mine")

    def test_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Your wishlist is empty")

    def test_sort_by_price_asc(self):
        WishlistItem.objects.create(user=self.user, title="Expensive", price=Decimal("100.00"))
        WishlistItem.objects.create(user=self.user, title="Cheap", price=Decimal("10.00"))
        response = self.client.get(self.url + "?sort=price_asc")
        content = response.content.decode()
        self.assertLess(content.index("Cheap"), content.index("Expensive"))

    def test_sort_by_price_desc(self):
        WishlistItem.objects.create(user=self.user, title="Expensive", price=Decimal("100.00"))
        WishlistItem.objects.create(user=self.user, title="Cheap", price=Decimal("10.00"))
        response = self.client.get(self.url + "?sort=price_desc")
        content = response.content.decode()
        self.assertLess(content.index("Expensive"), content.index("Cheap"))

    def test_sort_by_category(self):
        WishlistItem.objects.create(user=self.user, title="Zebra", category="Z")
        WishlistItem.objects.create(user=self.user, title="Apple", category="A")
        response = self.client.get(self.url + "?sort=category")
        content = response.content.decode()
        self.assertLess(content.index("Apple"), content.index("Zebra"))

    def test_invalid_sort_falls_back_to_default(self):
        WishlistItem.objects.create(user=self.user, title="Item")
        response = self.client.get(self.url + "?sort=invalid")
        self.assertEqual(response.status_code, 200)

    def test_purchased_item_shows_badge(self):
        WishlistItem.objects.create(
            user=self.user, title="Got It", status=WishlistItem.Status.PURCHASED
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Purchased")
        self.assertContains(response, "card-purchased")

    def test_available_item_shows_purchase_button(self):
        WishlistItem.objects.create(user=self.user, title="Want It")
        response = self.client.get(self.url)
        self.assertContains(response, "purchased this!")

    def test_purchased_item_shows_undo_button(self):
        WishlistItem.objects.create(
            user=self.user, title="Undo Me", status=WishlistItem.Status.PURCHASED
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Just kidding!")


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

    @patch("wishlist.views.send_purchased_email")
    def test_purchase_sends_email(self, mock_send):
        self.client.post(self.url, {"confirm": True, "message": "Here you go!"})
        mock_send.assert_called_once_with(self.user, self.item, "Here you go!")

    @patch("wishlist.views.send_purchased_email")
    def test_failed_purchase_does_not_send_email(self, mock_send):
        self.client.post(self.url, {"confirm": False})
        mock_send.assert_not_called()


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

    @patch("wishlist.views.send_undo_email")
    def test_undo_sends_email(self, mock_send):
        self.client.post(self.url, {"message": "Oops!"})
        mock_send.assert_called_once_with(self.user, self.item, "Oops!")

    @patch("wishlist.views.send_undo_email")
    def test_undo_on_available_item_does_not_send_email(self, mock_send):
        self.item.status = WishlistItem.Status.AVAILABLE
        self.item.save()
        self.client.post(self.url, {})
        mock_send.assert_not_called()

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
        self.assertIn('og:description', content)
        self.assertIn('og:image', content)
        self.assertIn('twitter:card', content)

    def test_login_page_has_og_tags(self):
        response = self.client.get(reverse("wishlist:login"))
        content = response.content.decode()
        self.assertIn('og:title', content)
        self.assertIn('og:image', content)

    def test_register_page_has_og_tags(self):
        response = self.client.get(reverse("wishlist:register"))
        content = response.content.decode()
        self.assertIn('og:title', content)
        self.assertIn('og:image', content)


# ---------------------------------------------------------------------------
# Email utility tests
# ---------------------------------------------------------------------------
class SendPurchasedEmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="pass123",
            first_name="Jane",
            last_name="Doe",
            phone_number="555-1234",
        )
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass123"
        )
        self.item = WishlistItem.objects.create(user=self.owner, title="Cool Gift")

    @override_settings(RESEND_API_KEY="", NOTIFICATION_TO_EMAIL="")
    def test_skips_when_not_configured(self):
        result = send_purchased_email(self.user, self.item)
        self.assertIsNone(result)

    @override_settings(RESEND_API_KEY="test_key", NOTIFICATION_TO_EMAIL="diane@example.com", RESEND_FROM_EMAIL="test@example.com")
    @patch("wishlist.email.resend.Emails.send", return_value={"id": "123"})
    def test_sends_with_correct_content(self, mock_send):
        result = send_purchased_email(self.user, self.item, "Happy birthday!")
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        self.assertEqual(call_args["to"], ["diane@example.com"])
        self.assertIn("Cool Gift", call_args["subject"])
        self.assertIn("Jane Doe", call_args["html"])
        self.assertIn("buyer@example.com", call_args["html"])
        self.assertIn("555-1234", call_args["html"])
        self.assertIn("Happy birthday!", call_args["html"])

    @override_settings(RESEND_API_KEY="test_key", NOTIFICATION_TO_EMAIL="diane@example.com", RESEND_FROM_EMAIL="test@example.com")
    @patch("wishlist.email.resend.Emails.send", return_value={"id": "123"})
    def test_sends_without_phone(self, mock_send):
        self.user.phone_number = ""
        self.user.save()
        send_purchased_email(self.user, self.item)
        call_args = mock_send.call_args[0][0]
        self.assertNotIn("555-1234", call_args["html"])

    @override_settings(RESEND_API_KEY="test_key", NOTIFICATION_TO_EMAIL="diane@example.com", RESEND_FROM_EMAIL="test@example.com")
    @patch("wishlist.email.resend.Emails.send", return_value={"id": "123"})
    def test_sends_without_message(self, mock_send):
        send_purchased_email(self.user, self.item)
        call_args = mock_send.call_args[0][0]
        self.assertNotIn("Their message", call_args["html"])

    @override_settings(RESEND_API_KEY="test_key", NOTIFICATION_TO_EMAIL="diane@example.com", RESEND_FROM_EMAIL="test@example.com")
    @patch("wishlist.email.resend.Emails.send", side_effect=Exception("API error"))
    def test_handles_api_failure_gracefully(self, mock_send):
        result = send_purchased_email(self.user, self.item)
        self.assertIsNone(result)


class SendUndoEmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="liar",
            email="liar@example.com",
            password="pass123",
            first_name="John",
            last_name="Smith",
            phone_number="555-9999",
        )
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass123"
        )
        self.item = WishlistItem.objects.create(user=self.owner, title="Birthday Gift")

    @override_settings(RESEND_API_KEY="", NOTIFICATION_TO_EMAIL="")
    def test_skips_when_not_configured(self):
        result = send_undo_email(self.user, self.item)
        self.assertIsNone(result)

    @override_settings(RESEND_API_KEY="test_key", NOTIFICATION_TO_EMAIL="diane@example.com", RESEND_FROM_EMAIL="test@example.com")
    @patch("wishlist.email.resend.Emails.send", return_value={"id": "456"})
    def test_sends_with_correct_content(self, mock_send):
        result = send_undo_email(self.user, self.item, "Sorry about that")
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        self.assertEqual(call_args["to"], ["diane@example.com"])
        self.assertIn("Birthday Gift", call_args["subject"])
        self.assertIn("John Smith", call_args["html"])
        self.assertIn("lied to you", call_args["html"])
        self.assertIn("liar@example.com", call_args["html"])
        self.assertIn("555-9999", call_args["html"])
        self.assertIn("Sorry about that", call_args["html"])

    @override_settings(RESEND_API_KEY="test_key", NOTIFICATION_TO_EMAIL="diane@example.com", RESEND_FROM_EMAIL="test@example.com")
    @patch("wishlist.email.resend.Emails.send", side_effect=Exception("API error"))
    def test_handles_api_failure_gracefully(self, mock_send):
        result = send_undo_email(self.user, self.item)
        self.assertIsNone(result)


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
        self.assertContains(response, "nav-user")
        self.assertContains(response, "Logout")
