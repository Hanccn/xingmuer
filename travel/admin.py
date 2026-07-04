from django.contrib import admin
from . import models


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "province", "adcode", "created_at")
    search_fields = ("name", "province", "adcode")


@admin.register(models.POI)
class POIAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "category", "rating", "need_reservation", "is_hidden_gem")
    list_filter = ("city", "need_reservation", "is_hidden_gem")
    search_fields = ("name", "address", "category")


@admin.register(models.PoiTip)
class PoiTipAdmin(admin.ModelAdmin):
    list_display = ("poi", "source", "content", "useful_count", "is_active", "created_at")
    list_filter = ("source", "is_active")
    search_fields = ("poi__name", "content")


@admin.register(models.PoiCollection)
class PoiCollectionAdmin(admin.ModelAdmin):
    list_display = ("user", "poi", "sort_order", "weight", "created_at")
    list_filter = ("user", "poi__city")
    search_fields = ("user__username", "poi__name")


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "target_style", "description", "created_at")
    list_filter = ("target_style",)
    search_fields = ("name", "description")


@admin.register(models.ThemePOI)
class ThemePOIAdmin(admin.ModelAdmin):
    list_display = ("theme", "poi", "sort_order")
    list_filter = ("theme", "poi__city")
    search_fields = ("theme__name", "poi__name")


@admin.register(models.Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "city", "status", "route_type", "total_days", "share_code", "created_at")
    list_filter = ("status", "route_type", "city")
    search_fields = ("name", "user__username", "share_code")
