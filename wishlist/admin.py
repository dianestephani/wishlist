from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Activity, Event, ItemEvent, ItemView, Purchase, StoreClick, User, Wishlist, WishlistItem


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "phone_number", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone_number",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("email", "phone_number")}),
    )


class ItemViewInline(admin.TabularInline):
    model = ItemView
    extra = 0
    readonly_fields = ("user", "count")
    can_delete = False


class StoreClickInline(admin.TabularInline):
    model = StoreClick
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False


class ItemEventInline(admin.TabularInline):
    model = ItemEvent
    extra = 0
    readonly_fields = ("event_type", "user", "message", "created_at")
    can_delete = False


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "status", "category", "brand", "store", "user", "created_at")
    list_filter = ("status", "category", "brand", "store")
    search_fields = ("title", "category", "brand", "store", "notes")
    list_editable = ("price", "status", "category", "brand", "store")
    list_per_page = 25
    readonly_fields = ("created_at",)
    inlines = [ItemViewInline, StoreClickInline, ItemEventInline]

    fieldsets = (
        (None, {
            "fields": ("user", "title", "status"),
        }),
        ("Product Details", {
            "fields": ("price", "category", "brand", "store", "product_url"),
        }),
        ("Media & Notes", {
            "fields": ("image", "notes"),
        }),
        ("Metadata", {
            "fields": ("created_at",),
        }),
    )


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("item", "purchased_by", "purchased_at")
    list_filter = ("purchased_at",)
    readonly_fields = ("purchased_at",)


@admin.register(ItemEvent)
class ItemEventAdmin(admin.ModelAdmin):
    list_display = ("item", "event_type", "user", "created_at")
    list_filter = ("event_type", "created_at")
    readonly_fields = ("item", "event_type", "user", "message", "created_at")


@admin.register(StoreClick)
class StoreClickAdmin(admin.ModelAdmin):
    list_display = ("item", "user", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("item", "user", "created_at")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "date", "start_time", "end_time", "address", "created_at")
    list_filter = ("date",)
    search_fields = ("title", "address")
    readonly_fields = ("created_at",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "location", "created_at")
    search_fields = ("title", "location")
    readonly_fields = ("created_at",)
