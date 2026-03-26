from django.urls import path

from . import views

app_name = "wishlist"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Create
    path("create/wishlist/", views.create_wishlist, name="create_wishlist"),
    path("create/event/", views.create_event, name="create_event"),
    path("create/activity/", views.create_activity, name="create_activity"),
    # Wishlists
    path("wishlist/", views.index, name="index"),
    path("wishlist/<int:wishlist_id>/", views.wishlist_detail, name="wishlist_detail"),
    path("wishlist/<int:wishlist_id>/edit/", views.edit_wishlist, name="edit_wishlist"),
    path("wishlist/<int:wishlist_id>/delete/", views.delete_wishlist, name="delete_wishlist"),
    path("wishlist/<int:wishlist_id>/add-item/", views.add_item, name="add_item"),
    # Items
    path("item/<int:item_id>/", views.item_detail, name="item_detail"),
    path("item/<int:item_id>/edit/", views.edit_item, name="edit_item"),
    path("item/<int:item_id>/delete/", views.delete_item, name="delete_item"),
    path("item/<int:item_id>/visit-store/", views.visit_store, name="visit_store"),
    path("item/<int:item_id>/purchase/", views.mark_purchased, name="mark_purchased"),
    path("item/<int:item_id>/undo-purchase/", views.undo_purchase, name="undo_purchase"),
    # Events
    path("events/", views.events_list, name="events"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("events/<int:event_id>/edit/", views.edit_event, name="edit_event"),
    path("events/<int:event_id>/delete/", views.delete_event, name="delete_event"),
    # Activities
    path("activities/", views.activities_list, name="activities"),
    path("activities/<int:activity_id>/edit/", views.edit_activity, name="edit_activity"),
    path("activities/<int:activity_id>/delete/", views.delete_activity, name="delete_activity"),
    # Auth
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
