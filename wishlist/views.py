from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from .email import send_purchased_email, send_undo_email
from .forms import ActivityForm, EventForm, PurchaseForm, RegistrationForm, UndoPurchaseForm, WishlistForm, WishlistItemForm
from .models import Activity, Event, ItemEvent, ItemView, Purchase, StoreClick, Wishlist, WishlistItem

SORT_OPTIONS = {
    "price_asc": "price",
    "price_desc": "-price",
    "category": "category",
    "brand": "brand",
    "store": "store",
}


@login_required
def dashboard(request):
    wishlists = Wishlist.objects.filter(user=request.user)[:5]
    events = Event.objects.filter(created_by=request.user)[:5]
    activities = Activity.objects.filter(created_by=request.user)[:5]

    context = {
        "wishlists": wishlists,
        "events": events,
        "activities": activities,
    }
    return render(request, "wishlist/dashboard.html", context)


@login_required
def create_wishlist(request):
    if request.method == "POST":
        form = WishlistForm(request.POST)
        item_form = WishlistItemForm(request.POST, request.FILES, prefix="item")
        if form.is_valid() and item_form.is_valid():
            wl = form.save(commit=False)
            wl.user = request.user
            wl.save()
            if item_form.cleaned_data.get("title"):
                item = item_form.save(commit=False)
                item.user = request.user
                item.save()
            messages.success(request, f'Wishlist "{wl.title}" created!')
            return redirect("wishlist:wishlist_detail", wishlist_id=wl.pk)
    else:
        form = WishlistForm()
        item_form = WishlistItemForm(prefix="item")
    return render(request, "wishlist/create_wishlist.html", {"form": form, "item_form": item_form})


@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created!')
            return redirect("wishlist:dashboard")
    else:
        form = EventForm()
    return render(request, "wishlist/create_event.html", {"form": form})


@login_required
def create_activity(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            messages.success(request, f'Activity "{activity.title}" created!')
            return redirect("wishlist:dashboard")
    else:
        form = ActivityForm()
    return render(request, "wishlist/create_activity.html", {"form": form})


@login_required
def wishlist_detail(request, wishlist_id):
    wl = get_object_or_404(Wishlist, pk=wishlist_id, user=request.user)
    items = WishlistItem.objects.filter(user=request.user).select_related("purchase")
    context = {"wishlist_obj": wl, "items": items}
    return render(request, "wishlist/wishlist_detail.html", context)


@login_required
def edit_wishlist(request, wishlist_id):
    wl = get_object_or_404(Wishlist, pk=wishlist_id, user=request.user)
    if request.method == "POST":
        form = WishlistForm(request.POST, instance=wl)
        if form.is_valid():
            form.save()
            messages.success(request, f'Wishlist "{wl.title}" updated!')
            return redirect("wishlist:wishlist_detail", wishlist_id=wl.pk)
    else:
        form = WishlistForm(instance=wl)
    return render(request, "wishlist/edit_wishlist.html", {"form": form, "wishlist_obj": wl})


@login_required
def delete_wishlist(request, wishlist_id):
    wl = get_object_or_404(Wishlist, pk=wishlist_id, user=request.user)
    if request.method == "POST":
        title = wl.title
        wl.delete()
        messages.success(request, f'Wishlist "{title}" deleted.')
        return redirect("wishlist:dashboard")
    return render(request, "wishlist/confirm_delete.html", {"object": wl, "type": "wishlist"})


@login_required
def add_item(request, wishlist_id):
    wl = get_object_or_404(Wishlist, pk=wishlist_id, user=request.user)
    if request.method == "POST":
        form = WishlistItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'"{item.title}" added to your wishlist!')
            return redirect("wishlist:wishlist_detail", wishlist_id=wl.pk)
    else:
        form = WishlistItemForm()
    return render(request, "wishlist/add_item.html", {"form": form, "wishlist_obj": wl})


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id, user=request.user)
    if request.method == "POST":
        form = WishlistItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{item.title}" updated!')
            return redirect("wishlist:item_detail", item_id=item.pk)
    else:
        form = WishlistItemForm(instance=item)
    return render(request, "wishlist/edit_item.html", {"form": form, "item": item})


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id, user=request.user)
    if request.method == "POST":
        title = item.title
        item.delete()
        messages.success(request, f'"{title}" deleted.')
        return redirect("wishlist:index")
    return render(request, "wishlist/confirm_delete.html", {"object": item, "type": "item"})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id, created_by=request.user)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated!')
            return redirect("wishlist:event_detail", event_id=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, "wishlist/edit_event.html", {"form": form, "event": event})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id, created_by=request.user)
    if request.method == "POST":
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect("wishlist:events")
    return render(request, "wishlist/confirm_delete.html", {"object": event, "type": "event"})


@login_required
def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id, created_by=request.user)
    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, f'Activity "{activity.title}" updated!')
            return redirect("wishlist:activities")
    else:
        form = ActivityForm(instance=activity)
    return render(request, "wishlist/edit_activity.html", {"form": form, "activity": activity})


@login_required
def delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id, created_by=request.user)
    if request.method == "POST":
        title = activity.title
        activity.delete()
        messages.success(request, f'Activity "{title}" deleted.')
        return redirect("wishlist:activities")
    return render(request, "wishlist/confirm_delete.html", {"object": activity, "type": "activity"})


@login_required
def friends(request):
    return render(request, "wishlist/friends.html")


@login_required
def events_list(request):
    events = Event.objects.filter(created_by=request.user)
    return render(request, "wishlist/events.html", {"events": events})


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id, created_by=request.user)
    return render(request, "wishlist/event_detail.html", {"event": event})


@login_required
def activities_list(request):
    activities = Activity.objects.filter(created_by=request.user)
    return render(request, "wishlist/activities.html", {"activities": activities})


@login_required
def index(request):
    sort = request.GET.get("sort", "")
    order_by = SORT_OPTIONS.get(sort, "-created_at")

    items = WishlistItem.objects.filter(user=request.user).select_related("purchase").order_by(order_by)

    context = {
        "items": items,
        "current_sort": sort,
        "sort_options": [
            ("", "Newest"),
            ("price_asc", "Price: Low to High"),
            ("price_desc", "Price: High to Low"),
            ("category", "Category"),
            ("brand", "Brand"),
            ("store", "Store"),
        ],
    }
    return render(request, "wishlist/index.html", context)


@login_required
def item_detail(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id)

    view_record, _ = ItemView.objects.get_or_create(item=item, user=request.user)
    view_record.count += 1
    view_record.save()

    events = None
    view_stats = None
    store_click_stats = None
    if request.user.is_superuser:
        events = item.events.select_related("user").all()
        view_stats = item.views.select_related("user").order_by("-count")
        store_click_stats = item.store_clicks.select_related("user").all()

    context = {
        "item": item,
        "events": events,
        "view_stats": view_stats,
        "store_click_stats": store_click_stats,
    }
    return render(request, "wishlist/item_detail.html", context)


@login_required
def visit_store(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id)

    if not item.product_url:
        return redirect("wishlist:item_detail", item_id=item.pk)

    StoreClick.objects.create(item=item, user=request.user)
    return redirect(item.product_url)


@login_required
def mark_purchased(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id)

    if item.status == WishlistItem.Status.PURCHASED:
        return redirect("wishlist:index")

    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data["message"]
            Purchase.objects.create(
                item=item,
                purchased_by=request.user,
                message=message,
            )
            ItemEvent.objects.create(
                item=item,
                event_type=ItemEvent.EventType.PURCHASED,
                user=request.user,
                message=message,
            )
            item.status = WishlistItem.Status.PURCHASED
            item.save()
            send_purchased_email(request.user, item, message)
            messages.success(request, f'"{item.title}" has been marked as purchased. Thank you!')
            return redirect("wishlist:index")
    else:
        form = PurchaseForm()

    return render(request, "wishlist/purchase.html", {"form": form, "item": item})


@login_required
def undo_purchase(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id)

    if item.status != WishlistItem.Status.PURCHASED:
        return redirect("wishlist:index")

    if request.method == "POST":
        form = UndoPurchaseForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data["message"]
            Purchase.objects.filter(item=item).delete()
            ItemEvent.objects.create(
                item=item,
                event_type=ItemEvent.EventType.UNDONE,
                user=request.user,
                message=message,
            )
            item.status = WishlistItem.Status.AVAILABLE
            item.save()
            send_undo_email(request.user, item, message)
            messages.info(request, f'"{item.title}" has been reverted to available.')
            return redirect("wishlist:index")
    else:
        form = UndoPurchaseForm()

    return render(request, "wishlist/undo_purchase.html", {"form": form, "item": item})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("wishlist:dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}! Your account has been created.")
            return redirect("wishlist:dashboard")
    else:
        form = RegistrationForm()

    return render(request, "wishlist/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("wishlist:dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect("wishlist:dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "wishlist/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("wishlist:login")
