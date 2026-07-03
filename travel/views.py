from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from . import models, amap


def index(request):
    """首页"""
    cities = [
        {"name": "三亚", "image": "images/sanyaa.jpg", "desc": "海滩 · 海岛 · 热带风情"},
        {"name": "成都", "image": "images/chengdu.jpg", "desc": "美食 · 茶馆 · 慢生活"},
        {"name": "大理", "image": "images/dali.jpg", "desc": "洱海 · 苍山 · 古城慢时光"},
        {"name": "西安", "image": "images/xian.jpg", "desc": "古都 · 兵马俑 · 碳水天堂"},
        {"name": "厦门", "image": "images/xiamen.jpg", "desc": "鼓浪屿 · 文艺 · 海风骑行"},
        {"name": "重庆", "image": "images/chongqing.jpg", "desc": "8D魔幻 · 火锅 · 洪崖洞"},
    ]
    return render(request, "travel/index.html", {
        "cities": cities,
        "collection_count": _collection_count(request.user),
    })


def discover(request):
    """发现页"""
    categories = [
        {"icon": "🏖️", "label": "海边躺平", "link": "/city/三亚/"},
        {"icon": "🍜", "label": "美食之旅", "link": "/city/成都/"},
        {"icon": "🏔️", "label": "爬山徒步", "link": "/city/大理/"},
        {"icon": "🏛️", "label": "历史古都", "link": "/city/西安/"},
        {"icon": "🌃", "label": "城市漫游", "link": "/city/重庆/"},
        {"icon": "🚲", "label": "文艺街区", "link": "/city/厦门/"},
        {"icon": "🍵", "label": "主题灵感", "link": "/theme/1/"},
        {"icon": "⛺", "label": "露营户外", "link": "#"},
        {"icon": "🎿", "label": "冰雪世界", "link": "#"},
        {"icon": "🌾", "label": "古镇田园", "link": "#"},
    ]
    trending = [
        {"name": "三亚", "image": "images/sanyaa.jpg", "link": "/city/三亚/", "tag": "🔥 本周热搜"},
        {"name": "大理", "image": "images/dali.jpg", "link": "/city/大理/", "tag": "🔥 持续热门"},
        {"name": "成都", "image": "images/chengdu.jpg", "link": "/city/成都/", "tag": "📈 上升中"},
        {"name": "西安", "image": "images/xian.jpg", "link": "/city/西安/", "tag": "📈 上升中"},
        {"name": "厦门", "image": "images/xiamen.jpg", "link": "/city/厦门/", "tag": "🌸 春季热门"},
        {"name": "重庆", "image": "images/chongqing.jpg", "link": "/city/重庆/", "tag": "🍲 美食相关"},
    ]
    provinces = [
        {"flag": "🌴", "name": "海南", "cities": "三亚、海口"},
        {"flag": "🐼", "name": "四川", "cities": "成都、乐山"},
        {"flag": "🦚", "name": "云南", "cities": "大理、丽江"},
        {"flag": "🏯", "name": "陕西", "cities": "西安、华山"},
        {"flag": "🌊", "name": "福建", "cities": "厦门、泉州"},
        {"flag": "🌆", "name": "重庆", "cities": "渝中、武隆"},
    ]
    return render(request, "travel/discover.html", {
        "categories": categories, "trending": trending, "provinces": provinces,
    })


def city_list(request, city_name):
    """城市景点列表"""
    pois = models.POI.objects.filter(city__name=city_name).order_by("-rating")
    if not pois.exists():
        # 尝试从高德拉数据
        _sync_city_pois(city_name)
        pois = models.POI.objects.filter(city__name=city_name).order_by("-rating")
    return render(request, "travel/city_list.html", {
        "city_name": city_name,
        "pois": pois,
        "collection_count": _collection_count(request.user),
    })


def poi_detail(request, poi_id):
    """景点详情"""
    poi = get_object_or_404(models.POI, id=poi_id)
    tips = poi.tips.filter(is_active=True).order_by("?")[:3]
    return render(request, "travel/poi_detail.html", {
        "poi": poi,
        "tips": tips,
        "collected": _is_collected(request.user, poi),
        "collection_count": _collection_count(request.user),
    })


def theme_detail(request, theme_id):
    """主题详情"""
    theme = get_object_or_404(models.Theme, id=theme_id)
    theme_pois = theme.theme_pois.select_related("poi").order_by("sort_order")
    return render(request, "travel/theme_detail.html", {
        "theme": theme,
        "theme_pois": theme_pois,
    })


@login_required
def plan(request):
    """我的规划"""
    collections = models.PoiCollection.objects.filter(
        user=request.user
    ).select_related("poi", "poi__city").order_by("sort_order")
    return render(request, "travel/plan.html", {
        "collections": collections,
        "collection_count": collections.count(),
    })


@login_required
def trips(request):
    """我的行程列表"""
    trips = models.Trip.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "travel/trips.html", {"trips": trips})


@login_required
def trip_detail(request, trip_id):
    """行程详情"""
    trip = get_object_or_404(models.Trip, id=trip_id, user=request.user)
    return render(request, "travel/trip_detail.html", {"trip": trip})


# --- API ---

def api_search_city(request):
    """GET /api/search/city/?q=三亚"""
    q = request.GET.get("q", "")
    results = []
    if q:
        pois = amap.search_poi(keywords=q, types="", offset=10)
        cities = {}
        for p in pois:
            cn = p.get("cityname", "")
            if cn and cn not in cities:
                cities[cn] = {"name": cn, "province": p.get("pname", ""), "adcode": p.get("citycode", "")}
        results = list(cities.values())[:6]
    return JsonResponse({"code": 0, "data": results})


@login_required
def api_collect_toggle(request, poi_id):
    """POST 收藏/取消收藏"""
    poi = get_object_or_404(models.POI, id=poi_id)
    coll, created = models.PoiCollection.objects.get_or_create(user=request.user, poi=poi)
    if not created:
        coll.delete()
    # Redirect back for form POST, or JSON for AJAX
    ref = request.META.get("HTTP_REFERER", "/")
    return redirect(ref) if not request.headers.get("X-Requested-With") else JsonResponse({"code": 0})


@login_required
def api_add_tip(request, poi_id):
    """POST 写Tips"""
    poi = get_object_or_404(models.POI, id=poi_id)
    content = request.POST.get("content", "").strip()
    if content and len(content) <= 80:
        models.PoiTip.objects.create(poi=poi, user=request.user, content=content, source="user")
    ref = request.META.get("HTTP_REFERER", "/")
    return redirect(ref) if not request.headers.get("X-Requested-With") else JsonResponse({"code": 0})


# --- 选址推荐 ---

@login_required
def api_location_recommend(request):
    """POST 住宿选址推荐"""
    from django.conf import settings
    cols = models.PoiCollection.objects.filter(user=request.user).select_related("poi","poi__city")
    if cols.count() < 3:
        return JsonResponse({"code":40001,"message":"至少收藏3个景点才能分析"})
    pois = [c.poi for c in cols]
    cn = pois[0].city.name

    hotels = amap.search_poi(keywords="酒店", city=cn, types="住宿服务", offset=30)
    if not hotels:
        return JsonResponse({"code":40002,"message":"未找到酒店数据"})

    areas, seen = [], set()
    for h in hotels:
        loc = h.get("location","").split(",")
        if len(loc)==2:
            a = h.get("address","")[:10]
            if a not in seen:
                seen.add(a); areas.append({"name":h.get("address",""),"lng":loc[0],"lat":loc[1]})
                if len(areas)>=5: break

    poi_locs = "|".join(f"{p.lng},{p.lat}" for p in pois)
    results = []
    for a in areas:
        d = f"{a['lng']},{a['lat']}"
        dists = amap.distance_matrix(poi_locs, d)
        if dists:
            tt = sum(int(x.get("duration","0")) for x in dists)/60
            w = sum(1 for x in dists if int(x.get("duration","999999"))<=20*60)
            results.append({"name":a["name"],"total_min":round(tt,1),"within_20min":f"{w}/{len(pois)}","score":round(100-tt,1)})
    results.sort(key=lambda x:-x["score"])
    return JsonResponse({"code":0,"data":{"city":cn,"poi_count":len(pois),"recommendations":results[:3]}})


# --- 路线生成 ---

@login_required
def api_generate_route(request):
    """POST 生成路线：贪心排序 + 按天拆分"""
    cols = models.PoiCollection.objects.filter(user=request.user).select_related("poi","poi__city")
    if cols.count() < 2:
        return JsonResponse({"code":40001,"message":"至少收藏2个景点才能生成路线"})

    days = int(request.POST.get("days", 3))
    route_type = request.POST.get("type", "compact")
    hotel = request.POST.get("hotel", "")

    pois = [(c.poi, c.weight) for c in cols]
    cn = pois[0][0].city.name

    # Greedy nearest-neighbor sort (start from first POI)
    ordered = [pois[0][0]]
    remaining = pois[1:]
    while remaining:
        last = ordered[-1]
        origins = "|".join(f"{p[0].lng},{p[0].lat}" for p in remaining)
        dest = f"{last.lng},{last.lat}"
        dists = amap.distance_matrix(origins, dest)
        # Find nearest
        best_i, best_dur = 0, float("inf")
        for i, d in enumerate(dists):
            dur = int(d.get("duration", 999999))
            if dur < best_dur:
                best_dur, best_i = dur, i
        ordered.append(remaining.pop(best_i)[0])

    # Split into days
    per_day = max(1, len(ordered) // days)
    leftover = len(ordered) % days
    schedule = []
    idx = 0
    for d in range(days):
        count = per_day + (1 if d < leftover else 0)
        schedule.append(ordered[idx:idx+count])
        idx += count

    # Build response
    result_days = []
    total_time = 0
    for day_idx, day_pois in enumerate(schedule):
        day_items = [{"name": p.name, "id": p.id, "lng": float(p.lng), "lat": float(p.lat),
                       "address": p.address, "rating": float(p.rating)} for p in day_pois]
        day_time = 0
        # Compute route: hotel → poi1 → poi2 → ...
        for i in range(len(day_pois)-1):
            o = f"{day_pois[i].lng},{day_pois[i].lat}"
            d = f"{day_pois[i+1].lng},{day_pois[i+1].lat}"
            dd = amap.distance_matrix(o, d)
            if dd:
                dur = int(dd[0].get("duration", 0)) // 60
                day_items[i]["next_drive_min"] = dur
                day_time += dur
        result_days.append({"day": day_idx+1, "pois": day_items, "drive_min": day_time})
        total_time += day_time

    # Save trip with share code
    import random, string, datetime as dt
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    expires = dt.datetime.now() + dt.timedelta(hours=24)
    if hotel:
        trip = models.Trip.objects.create(
            user=request.user, city=pois[0][0].city, name=f"{cn}{days}日游",
            hotel_area=hotel, route_type=route_type, total_days=days,
            route_data={"days": result_days}, status="saved",
            share_code=code, share_expires_at=expires)
        trip_id = trip.id
    else:
        trip_id = None
        code = None

    return JsonResponse({"code":0,"data":{"city":cn,"days":result_days,"total_drive_min":total_time,"trip_id":trip_id,"share_code":code,"route_type":route_type}})


def trip_share(request, code):
    """公开查看——分享码访问，无需登录"""
    from datetime import datetime as dtt
    trip = get_object_or_404(models.Trip, share_code=code.upper())
    if trip.share_expires_at and trip.share_expires_at < dtt.now():
        return render(request, "travel/share_expired.html", {"trip": trip})
    return render(request, "travel/trip_share.html", {"trip": trip})


# --- Agent 搜索 ---

def api_agent_search(request):
    """Agent自然语言搜索"""
    from django.conf import settings
    import json as _json
    q = request.GET.get("q","").strip()
    if not q: return JsonResponse({"code":40001,"message":"请输入搜索内容"})

    prompt = f'你是旅游搜索助手。从用户输入提取约束推荐目的地。\n用户："{q}"\n严格JSON：{{"constraints":[],"candidate_regions":[],"tags":[],"confidence":0.5}}\n3-5个中国城市。'

    try:
        r = requests.post("https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization":f"Bearer {settings.DEEPSEEK_KEY}","Content-Type":"application/json"},
            json={"model":"deepseek-chat","messages":[{"role":"user","content":prompt}],"temperature":0.3,"max_tokens":300}, timeout=10)
        c = r.json()["choices"][0]["message"]["content"].strip()
        if c.startswith("```"): c = c.split("\n",1)[1].rsplit("\n```",1)[0]
        p = _json.loads(c)
    except Exception:
        p = _fallback_parse(q)

    all_pois = []
    for rg in p.get("candidate_regions",[])[:4]:
        for x in amap.search_poi(keywords=rg, types="风景名胜", offset=5):
            all_pois.append({"name":x.get("name",""),"city":x.get("cityname",""),"address":x.get("address",""),
                "rating":x.get("biz_ext",{}).get("rating","0"),"match_reason":rg})

    return JsonResponse({"code":0,"data":{"query":q,"constraints":p.get("constraints",[]),"tags":p.get("tags",[]),
        "confidence":p.get("confidence",0.5),"pois":all_pois[:15]}})


def _fallback_parse(q):
    c, t = [], []
    for kw, v in [("周末","时间-周末"),("爬山","活动-爬山"),("海边","偏好-海边"),("美食","偏好-美食"),("小众","偏好-小众"),("古城","偏好-古城")]:
        if kw in q: c.append(v)
    return {"constraints":c,"candidate_regions":["大理","成都","杭州","厦门","桂林"],"tags":t,"confidence":0.4}


# --- helpers ---

def _collection_count(user):
    if user.is_authenticated:
        return models.PoiCollection.objects.filter(user=user).count()
    return 0

def _is_collected(user, poi):
    if user.is_authenticated:
        return models.PoiCollection.objects.filter(user=user, poi=poi).exists()
    return False

def _sync_city_pois(city_name):
    """从高德同步城市景点到本地数据库"""
    pois = amap.search_poi(keywords=city_name, city=city_name, offset=10)
    if not pois:
        return
    city, _ = models.City.objects.get_or_create(name=city_name)
    for p in pois:
        loc = p.get("location", "0,0").split(",")
        models.POI.objects.update_or_create(
            gaode_poi_id=p.get("id", ""),
            defaults={
                "name": p.get("name", ""),
                "city": city,
                "address": p.get("address", ""),
                "lng": float(loc[0]) if len(loc) > 1 else 0,
                "lat": float(loc[1]) if len(loc) > 1 else 0,
                "category": p.get("type", ""),
                "rating": float(p.get("biz_ext", {}).get("rating", 0) or 0),
            }
        )
