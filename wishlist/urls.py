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
    # Profile
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/delete/", views.delete_account, name="delete_account"),
    # Messaging
    path("inbox/", views.inbox, name="inbox"),
    path("inbox/new/", views.new_message, name="new_message"),
    path("conversation/<int:convo_id>/", views.conversation_detail, name="conversation_detail"),
    path("message/<int:user_id>/", views.start_conversation, name="start_conversation"),
    path("activity/", views.activity_feed, name="activity_feed"),
    # APIs
    path("api/notifications/", views.notifications_api, name="notifications_api"),
    path("api/activity/", views.activity_feed_api, name="activity_feed_api"),
    path("api/messages/", views.messages_api, name="messages_api"),
    # Friends
    path("friends/", views.friends, name="friends"),
    path("friends/requests/", views.friend_requests_page, name="friend_requests_page"),
    path("friends/add/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("friends/request/<int:request_id>/accept/", views.accept_friend_request, name="accept_friend_request"),
    path("friends/request/<int:request_id>/deny/", views.deny_friend_request, name="deny_friend_request"),
    path("friends/remove/<int:user_id>/", views.remove_friend, name="remove_friend"),
    path("api/friend-requests/", views.friend_requests_api, name="friend_requests_api"),
    path("users/<str:username>/", views.public_profile, name="public_profile"),
    path("users/<str:username>/wishlist/<int:wishlist_id>/", views.friend_wishlist_detail, name="friend_wishlist_detail"),
    path("users/<str:username>/event/<int:event_id>/", views.friend_event_detail, name="friend_event_detail"),
    path("users/<str:username>/activity/<int:activity_id>/", views.friend_activity_detail, name="friend_activity_detail"),
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
