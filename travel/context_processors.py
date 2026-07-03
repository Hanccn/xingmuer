from django.conf import settings

def amap_key(request):
    return {
        "AMAP_JS_KEY": getattr(settings, "AMAP_JS_KEY", ""),
        "AMAP_JS_SECRET": getattr(settings, "AMAP_JS_SECRET", ""),
    }
