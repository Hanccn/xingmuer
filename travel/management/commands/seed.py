from django.core.management.base import BaseCommand
from travel import models
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Seed sample data for development"

    def handle(self, *args, **options):
        # Create test user
        user, _ = User.objects.get_or_create(username="demo", defaults={"email": "demo@test.com"})
        user.set_password("demo123")
        user.save()

        # Create cities
        cities_data = [
            ("三亚", "海南"), ("成都", "四川"), ("大理", "云南"),
            ("西安", "陕西"), ("厦门", "福建"), ("重庆", "重庆"),
        ]
        cities = {}
        for name, prov in cities_data:
            c, _ = models.City.objects.get_or_create(name=name, defaults={"province": prov})
            cities[name] = c

        # Create POIs for 三亚
        sanya_pois = [
            {"name": "天涯海角", "addr": "三亚市天涯区", "lng": 109.34, "lat": 18.29, "rating": 4.3, "tags": ["海滩", "自然风光", "经典必去"], "duration": 150, "hidden": False},
            {"name": "蜈支洲岛", "addr": "海棠区", "lng": 109.76, "lat": 18.31, "rating": 4.5, "tags": ["海岛", "潜水", "需预约"], "duration": 300, "hidden": False, "reservation_val": True},
            {"name": "后海村", "addr": "海棠区", "lng": 109.77, "lat": 18.32, "rating": 4.0, "tags": ["渔村", "冲浪", "夜市"], "duration": 150, "hidden": True},
        ]
        for p in sanya_pois:
            models.POI.objects.update_or_create(
                gaode_poi_id=f"seed-sy-{p['name']}",
                defaults={"name": p["name"], "city": cities["三亚"], "address": p.get("addr", ""),
                    "lng": p["lng"], "lat": p["lat"], "rating": p["rating"],
                    "tags": p["tags"], "suggested_duration": p.get("duration"),
                    "is_hidden_gem": p.get("hidden", False),
                    "need_reservation": p.get("reservation_val", False)})

        # Tips
        poi_tianya = models.POI.objects.get(gaode_poi_id="seed-sy-天涯海角")
        tips = [
            ("下午4点后半价票，人还少，拍照光线最好", "scraped_xhs"),
            ("门口的椰子30别买，往停车场走200米有10块的", "user"),
            ("去天涯石别走主路，右边礁石小道更出片", "user"),
        ]
        for content, source in tips:
            models.PoiTip.objects.get_or_create(poi=poi_tianya, content=content, defaults={"source": source})

        # Theme
        theme, _ = models.Theme.objects.get_or_create(name="老茶馆地图", defaults={"description": "成都本地人常去的老茶馆", "target_style": "free"})

        self.stdout.write(self.style.SUCCESS("Seed data created. User: demo / demo123"))
