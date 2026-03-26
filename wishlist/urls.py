from django.urls import path

from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("wishlist/", views.index, name="index"),
    path("wishlist/<int:wishlist_id>/", views.wishlist_detail, name="wishlist_detail"),
    path("events/", views.events_list, name="events"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("activities/", views.activities_list, name="activities"),
    path("item/<int:item_id>/", views.item_detail, name="item_detail"),
    path("item/<int:item_id>/visit-store/", views.visit_store, name="visit_store"),
    path("item/<int:item_id>/purchase/", views.mark_purchased, name="mark_purchased"),
    path("item/<int:item_id>/undo-purchase/", views.undo_purchase, name="undo_purchase"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
