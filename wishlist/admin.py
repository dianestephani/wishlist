from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ItemEvent, Purchase, User, WishlistItem


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


class ItemEventInline(admin.TabularInline):
    model = ItemEvent
    extra = 0
    readonly_fields = ("event_type", "user", "message", "created_at")
    can_delete = False


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "price", "store", "status", "created_at")
    list_filter = ("status", "category", "store")
    search_fields = ("title", "brand", "store")
    readonly_fields = ("created_at",)
    inlines = [ItemEventInline]


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
