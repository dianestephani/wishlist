from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .forms import PurchaseForm, RegistrationForm, UndoPurchaseForm
from .models import ItemEvent, Purchase, WishlistItem

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
        self.assertRedirects(response, reverse("wishlist:index"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

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
        self.assertRedirects(response, reverse("wishlist:index"))


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
        self.assertRedirects(response, reverse("wishlist:index"))

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
        self.assertRedirects(response, reverse("wishlist:index"))


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

    def test_logout_redirects_to_login(self):
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("wishlist:logout"))
        self.assertRedirects(response, reverse("wishlist:login"))

    def test_logout_clears_session(self):
        self.client.login(username="testuser", password="pass123")
        self.client.get(reverse("wishlist:logout"))
        response = self.client.get(reverse("wishlist:index"))
        self.assertRedirects(response, f"{reverse('wishlist:login')}?next=/")


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
        self.assertRedirects(response, f"{reverse('wishlist:login')}?next=/")

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

    def test_nonexistent_item_returns_404(self):
        self.client.login(username="owner", password="pass123")
        url = reverse("wishlist:item_detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
