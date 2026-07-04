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

        # Create POIs for core demo cities.
        poi_data = [
            {"city": "三亚", "name": "天涯海角", "addr": "三亚市天涯区", "lng": 109.34, "lat": 18.29, "rating": 4.3, "tags": ["海滩", "自然风光", "经典必去"], "duration": 150},
            {"city": "三亚", "name": "蜈支洲岛", "addr": "海棠区", "lng": 109.76, "lat": 18.31, "rating": 4.5, "tags": ["海岛", "潜水", "需预约"], "duration": 300, "reservation_val": True},
            {"city": "三亚", "name": "后海村", "addr": "海棠区", "lng": 109.77, "lat": 18.32, "rating": 4.0, "tags": ["渔村", "冲浪", "夜市"], "duration": 150, "hidden": True},
            {"city": "成都", "name": "人民公园", "addr": "青羊区少城路", "lng": 104.06, "lat": 30.66, "rating": 4.6, "tags": ["茶馆", "慢生活", "本地体验"], "duration": 120, "hidden": True},
            {"city": "成都", "name": "东郊记忆", "addr": "成华区建设南路", "lng": 104.12, "lat": 30.67, "rating": 4.5, "tags": ["文艺", "展览", "夜游"], "duration": 120},
            {"city": "大理", "name": "洱海生态廊道", "addr": "大理市环海西路", "lng": 100.22, "lat": 25.70, "rating": 4.7, "tags": ["骑行", "湖景", "日落"], "duration": 180},
            {"city": "大理", "name": "苍山洗马潭索道", "addr": "大理苍山景区", "lng": 100.14, "lat": 25.69, "rating": 4.6, "tags": ["爬山", "自然风光"], "duration": 240},
        ]
        seeded_pois = {}
        for p in poi_data:
            poi, _ = models.POI.objects.update_or_create(
                gaode_poi_id=f"seed-{p['city']}-{p['name']}",
                defaults={
                    "name": p["name"],
                    "city": cities[p["city"]],
                    "address": p.get("addr", ""),
                    "lng": p["lng"],
                    "lat": p["lat"],
                    "rating": p["rating"],
                    "tags": p["tags"],
                    "suggested_duration": p.get("duration"),
                    "is_hidden_gem": p.get("hidden", False),
                    "need_reservation": p.get("reservation_val", False),
                },
            )
            seeded_pois[p["name"]] = poi

        # Tips
        tips = [
            ("天涯海角", "下午4点后入园人少，海边拍照光线最好", "scraped_xhs"),
            ("天涯海角", "门口椰子偏贵，往停车场方向走会便宜不少", "user"),
            ("蜈支洲岛", "想玩项目尽量早班船上岛，下午排队会明显变长", "user"),
            ("后海村", "冲浪课适合新手，但晚上更像夜市街区", "user"),
            ("人民公园", "鹤鸣茶社适合感受成都节奏，周末要早点占位", "user"),
            ("洱海生态廊道", "骑行建议选一小段，不必硬绕完整圈", "ai"),
        ]
        for poi_name, content, source in tips:
            models.PoiTip.objects.get_or_create(
                poi=seeded_pois[poi_name],
                content=content[:80],
                defaults={"source": source},
            )

        # Theme
        theme, _ = models.Theme.objects.get_or_create(
            name="老茶馆地图",
            defaults={"description": "成都本地人常去的老茶馆", "target_style": "free"},
        )
        models.ThemePOI.objects.get_or_create(theme=theme, poi=seeded_pois["人民公园"], defaults={"sort_order": 1})

        # Give the demo account a planning list that can immediately generate a route.
        for idx, poi_name in enumerate(["天涯海角", "蜈支洲岛", "后海村"], start=1):
            models.PoiCollection.objects.get_or_create(
                user=user,
                poi=seeded_pois[poi_name],
                defaults={"sort_order": idx, "weight": 1},
            )

        self.stdout.write(self.style.SUCCESS("Seed data created. User: demo / demo123"))
