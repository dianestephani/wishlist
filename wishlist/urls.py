from django.urls import path

from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.index, name="index"),
    path("item/<int:item_id>/", views.item_detail, name="item_detail"),
    path("item/<int:item_id>/purchase/", views.mark_purchased, name="mark_purchased"),
    path("item/<int:item_id>/undo-purchase/", views.undo_purchase, name="undo_purchase"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
