from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import RegistrationForm
from .models import WishlistItem

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

    items = WishlistItem.objects.filter(user=request.user).order_by(order_by)

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
