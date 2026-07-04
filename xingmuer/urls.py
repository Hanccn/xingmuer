from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from travel import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(
        template_name="login.html",
        redirect_authenticated_user=True,
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    # Pages
    path("", views.index, name="index"),
    path("discover/", views.discover, name="discover"),
    path("city/<str:city_name>/", views.city_list, name="city_list"),
    path("poi/<int:poi_id>/", views.poi_detail, name="poi_detail"),
    path("theme/<int:theme_id>/", views.theme_detail, name="theme_detail"),
    path("plan/", views.plan, name="plan"),
    path("trips/", views.trips, name="trips"),
    path("trip/<int:trip_id>/", views.trip_detail, name="trip_detail"),
    # API
    path("api/search/city/", views.api_search_city, name="api_search_city"),
    path("api/collect/<int:poi_id>/", views.api_collect_toggle, name="api_collect_toggle"),
    path("api/tip/<int:poi_id>/", views.api_add_tip, name="api_add_tip"),
    path("api/location/", views.api_location_recommend, name="api_location"),
    path("api/agent/search/", views.api_agent_search, name="api_agent_search"),
    path("api/route/", views.api_generate_route, name="api_route"),
    path("s/<str:code>/", views.trip_share, name="trip_share"),
]
