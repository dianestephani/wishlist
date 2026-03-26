from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PurchaseForm, RegistrationForm, UndoPurchaseForm
from .models import Purchase, WishlistItem

SORT_OPTIONS = {
    "price_asc": "price",
    "price_desc": "-price",
    "category": "category",
    "brand": "brand",
    "store": "store",
}


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
def mark_purchased(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id)

    if item.status == WishlistItem.Status.PURCHASED:
        return redirect("wishlist:index")

    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            Purchase.objects.create(
                item=item,
                purchased_by=request.user,
                message=form.cleaned_data["message"],
            )
            item.status = WishlistItem.Status.PURCHASED
            item.save()
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
            Purchase.objects.filter(item=item).delete()
            item.status = WishlistItem.Status.AVAILABLE
            item.save()
            return redirect("wishlist:index")
    else:
        form = UndoPurchaseForm()

    return render(request, "wishlist/undo_purchase.html", {"form": form, "item": item})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("wishlist:index")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("wishlist:index")
    else:
        form = RegistrationForm()

    return render(request, "wishlist/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("wishlist:index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("wishlist:index")
    else:
        form = AuthenticationForm()

    return render(request, "wishlist/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("wishlist:login")
