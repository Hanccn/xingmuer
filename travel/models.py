from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(max_length=100)
    province = models.CharField(max_length=100, blank=True)
    adcode = models.CharField(max_length=6, blank=True)
    center_lng = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    center_lat = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class POI(models.Model):
    gaode_poi_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="pois")
    address = models.CharField(max_length=500, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=6)
    lat = models.DecimalField(max_digits=10, decimal_places=6)
    category = models.CharField(max_length=100, blank=True)
    business_hours = models.CharField(max_length=200, blank=True)
    ticket_info = models.CharField(max_length=500, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    need_reservation = models.BooleanField(default=False)
    suggested_duration = models.IntegerField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_hidden_gem = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-rating"]

    def __str__(self):
        return self.name


class PoiTip(models.Model):
    SOURCE_CHOICES = [
        ("user", "用户"),
        ("scraped_xhs", "小红书"),
        ("scraped_mfw", "马蜂窝"),
        ("ai", "AI生成"),
    ]
    poi = models.ForeignKey(POI, on_delete=models.CASCADE, related_name="tips")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.CharField(max_length=80)
    source = models.CharField(max_length=30, default="user", choices=SOURCE_CHOICES)
    useful_count = models.IntegerField(default=0)
    show_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PoiCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    poi = models.ForeignKey(POI, on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)
    weight = models.IntegerField(default=1)
    note = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "poi"]
        ordering = ["sort_order"]


class Theme(models.Model):
    STYLE_CHOICES = [("free", "随性型"), ("planner", "规划型"), ("both", "通用")]
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    cover_image = models.CharField(max_length=500, blank=True)
    target_style = models.CharField(max_length=20, default="free", choices=STYLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ThemePOI(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="theme_pois")
    poi = models.ForeignKey(POI, on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ["theme", "poi"]


class Trip(models.Model):
    ROUTE_CHOICES = [("compact", "紧凑型"), ("flexible", "弹性型")]
    TRANSPORT_CHOICES = [("drive", "驾车"), ("transit", "公交"), ("mix", "混合")]
    STATUS_CHOICES = [("draft", "草稿"), ("saved", "已保存"), ("archived", "已归档")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    hotel_area = models.CharField(max_length=200, blank=True)
    route_type = models.CharField(max_length=20, default="compact", choices=ROUTE_CHOICES)
    transport = models.CharField(max_length=20, default="drive", choices=TRANSPORT_CHOICES)
    total_days = models.IntegerField(default=1)
    route_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default="draft", choices=STATUS_CHOICES)
    share_code = models.CharField(max_length=6, blank=True)
    share_expires_at = models.DateTimeField(null=True, blank=True)
    starts_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
