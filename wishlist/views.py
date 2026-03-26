from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import RegistrationForm


@login_required
def index(request):
    return render(request, "wishlist/index.html")


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
