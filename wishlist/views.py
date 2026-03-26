from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActivityForm, EventForm, ProfileForm, PurchaseForm, RegistrationForm, UndoPurchaseForm, WishlistForm, WishlistItemForm
from django.http import JsonResponse

from .models import Activity, Event, FriendRequest, Friendship, ItemEvent, ItemView, Purchase, StoreClick, Wishlist, WishlistItem

SORT_OPTIONS = {
    "price_asc": "price",
    "price_desc": "-price",
    "category": "category",
    "brand": "brand",
    "store": "store",
}


@login_required
def dashboard(request):
    wishlists = Wishlist.objects.filter(owner=request.user)[:5]
    events = Event.objects.filter(owner=request.user)[:5]
    activities = Activity.objects.filter(owner=request.user)[:5]
    friendships = Friendship.objects.filter(user=request.user).select_related("friend")[:10]

    context = {
        "wishlists": wishlists,
        "events": events,
        "activities": activities,
        "friendships": friendships,
    }
    return render(request, "wishlist/dashboard.html", context)


@login_required
def create_wishlist(request):
    if request.method == "POST":
        form = WishlistForm(request.POST)
        item_form = WishlistItemForm(request.POST, request.FILES, prefix="item")
        has_item_data = any(
            request.POST.get(f"item-{f}") for f in ["title", "product_url", "price", "category", "brand", "store"]
        )
        item_valid = item_form.is_valid() if has_item_data else True
        if form.is_valid() and item_valid:
            wl = form.save(commit=False)
            wl.owner = request.user
            wl.save()
            if has_item_data and item_form.cleaned_data.get("title"):
                item = item_form.save(commit=False)
                item.user = request.user
                item.wishlist = wl
                item.save()
            messages.success(request, f'Wishlist "{wl.name}" created!')
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
            event.owner = request.user
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
            activity.owner = request.user
            activity.save()
            messages.success(request, f'Activity "{activity.title}" created!')
            return redirect("wishlist:dashboard")
    else:
        form = ActivityForm()
    return render(request, "wishlist/create_activity.html", {"form": form})


@login_required
def wishlist_detail(request, wishlist_id):
    wl = get_object_or_404(Wishlist, pk=wishlist_id, owner=request.user)
    items = WishlistItem.objects.filter(wishlist=wl).select_related("purchase")
    context = {"wishlist_obj": wl, "items": items}
    return render(request, "wishlist/wishlist_detail.html", context)


@login_required
def edit_wishlist(request, wishlist_id):
    wl = get_object_or_404(Wishlist, pk=wishlist_id, owner=request.user)
    if request.method == "POST":
        form = WishlistForm(request.POST, instance=wl)
        if form.is_valid():
            form.save()
            messages.success(request, f'Wishlist "{wl.name}" updated!')
            return redirect("wishlist:wishlist_detail", wishlist_id=wl.pk)
    else:
        form = WishlistForm(instance=wl)
    return render(request, "wishlist/edit_wishlist.html", {"form": form, "wishlist_obj": wl})


@login_required
def delete_wishlist(request, wishlist_id):
    wl = get_object_or_404(Wishlist, pk=wishlist_id, owner=request.user)
    if request.method == "POST":
        title = wl.name
        wl.delete()
        messages.success(request, f'Wishlist "{title}" deleted.')
        return redirect("wishlist:dashboard")
    return render(request, "wishlist/confirm_delete.html", {"object": wl, "type": "wishlist"})


@login_required
def add_item(request, wishlist_id):
    wl = get_object_or_404(Wishlist, pk=wishlist_id, owner=request.user)
    if request.method == "POST":
        form = WishlistItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.wishlist = wl
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
    event = get_object_or_404(Event, pk=event_id, owner=request.user)
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
    event = get_object_or_404(Event, pk=event_id, owner=request.user)
    if request.method == "POST":
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect("wishlist:events")
    return render(request, "wishlist/confirm_delete.html", {"object": event, "type": "event"})


@login_required
def edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id, owner=request.user)
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
    activity = get_object_or_404(Activity, pk=activity_id, owner=request.user)
    if request.method == "POST":
        title = activity.title
        activity.delete()
        messages.success(request, f'Activity "{title}" deleted.')
        return redirect("wishlist:activities")
    return render(request, "wishlist/confirm_delete.html", {"object": activity, "type": "activity"})


@login_required
def profile(request):
    return render(request, "wishlist/profile.html")


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated!")
            return redirect("wishlist:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "wishlist/edit_profile.html", {"form": form})


@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect("wishlist:login")
    return render(request, "wishlist/confirm_delete_account.html")


@login_required
def notifications_api(request):
    events = (
        ItemEvent.objects.filter(item__user=request.user)
        .select_related("item", "user")
        .order_by("-created_at")[:20]
    )
    data = []
    for event in events:
        data.append({
            "id": event.pk,
            "event_type": event.get_event_type_display(),
            "item_title": event.item.title,
            "user": event.user.first_name or event.user.username,
            "message": event.message,
            "created_at": event.created_at.isoformat(),
            "item_id": event.item.pk,
        })
    return JsonResponse({"notifications": data})


@login_required
def friends(request):
    friendships = Friendship.objects.filter(user=request.user).select_related("friend")
    search_results = None
    query = request.GET.get("q", "").strip()
    if query:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from django.db.models import Q
        search_results = (
            User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(phone_number__icontains=query)
            )
            .exclude(pk=request.user.pk)[:20]
        )
        friend_ids = set(friendships.values_list("friend_id", flat=True))
        pending_ids = set(
            FriendRequest.objects.filter(from_user=request.user, status=FriendRequest.Status.PENDING)
            .values_list("to_user_id", flat=True)
        )
        for user in search_results:
            user.is_already_friend = user.pk in friend_ids
            user.is_pending = user.pk in pending_ids

    context = {
        "friendships": friendships,
        "search_results": search_results,
        "query": query,
    }
    return render(request, "wishlist/friends.html", context)


@login_required
def send_friend_request(request, user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    to_user = get_object_or_404(User, pk=user_id)

    if to_user == request.user:
        messages.error(request, "You can't send a friend request to yourself.")
        return redirect("wishlist:friends")

    if Friendship.objects.filter(user=request.user, friend=to_user).exists():
        messages.info(request, f"You're already friends with {to_user.first_name or to_user.username}.")
        return redirect("wishlist:friends")

    _, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=to_user,
        defaults={"status": FriendRequest.Status.PENDING},
    )
    if created:
        messages.success(request, f"Friend request sent to {to_user.first_name or to_user.username}!")
    else:
        messages.info(request, "Friend request already sent.")
    return redirect("wishlist:friends")


@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user, status=FriendRequest.Status.PENDING)
    fr.status = FriendRequest.Status.ACCEPTED
    fr.save()
    Friendship.objects.get_or_create(user=request.user, friend=fr.from_user)
    Friendship.objects.get_or_create(user=fr.from_user, friend=request.user)
    messages.success(request, f"You are now friends with {fr.from_user.first_name or fr.from_user.username}!")
    return redirect("wishlist:friends")


@login_required
def deny_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user, status=FriendRequest.Status.PENDING)
    fr.delete()
    return redirect("wishlist:friends")


@login_required
def friend_requests_api(request):
    pending = (
        FriendRequest.objects.filter(to_user=request.user, status=FriendRequest.Status.PENDING)
        .select_related("from_user")
        .order_by("-created_at")[:20]
    )
    data = []
    for fr in pending:
        data.append({
            "id": fr.pk,
            "from_user": fr.from_user.first_name or fr.from_user.username,
            "from_username": fr.from_user.username,
            "from_first": fr.from_user.first_name,
            "from_last": fr.from_user.last_name,
            "created_at": fr.created_at.isoformat(),
            "accept_url": f"/friends/request/{fr.pk}/accept/",
            "deny_url": f"/friends/request/{fr.pk}/deny/",
        })
    return JsonResponse({"friend_requests": data})


@login_required
def public_profile(request, username):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)
    is_friend = Friendship.objects.filter(user=request.user, friend=profile_user).exists()
    public_wishlists = Wishlist.objects.filter(owner=profile_user, is_public=True)
    public_events = Event.objects.filter(owner=profile_user, is_public=True)
    public_activities = Activity.objects.filter(owner=profile_user, is_public=True)
    context = {
        "profile_user": profile_user,
        "is_friend": is_friend,
        "public_wishlists": public_wishlists,
        "public_events": public_events,
        "public_activities": public_activities,
    }
    return render(request, "wishlist/public_profile.html", context)


@login_required
def events_list(request):
    events = Event.objects.filter(owner=request.user)
    return render(request, "wishlist/events.html", {"events": events})


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id, owner=request.user)
    return render(request, "wishlist/event_detail.html", {"event": event})


@login_required
def activities_list(request):
    activities = Activity.objects.filter(owner=request.user)
    return render(request, "wishlist/activities.html", {"activities": activities})


@login_required
def index(request):
    wishlists = Wishlist.objects.filter(owner=request.user)
    return render(request, "wishlist/index.html", {"wishlists": wishlists})


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
