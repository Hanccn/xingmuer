import os
from unittest.mock import patch

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from . import amap
from .models import City, POI


class AmapClientTests(TestCase):
    @patch("travel.amap.requests.get", side_effect=requests.RequestException)
    def test_amap_failure_returns_empty_payload(self, _mock_get):
        self.assertEqual(amap.search_poi("三亚"), [])


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class TravelSmokeTests(TestCase):
    def setUp(self):
        city = City.objects.create(name="大理", province="云南")
        POI.objects.create(
            gaode_poi_id="test-dali-cangshan",
            name="苍山洗马潭索道",
            city=city,
            address="大理苍山景区",
            lng=100.140000,
            lat=25.690000,
            rating=4.6,
            tags=["爬山", "自然风光"],
        )

    def test_core_pages_are_reachable(self):
        for path in ["/", "/discover/", "/city/大理/"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)

    @patch("travel.views.amap.search_poi", return_value=[])
    @patch("travel.views.requests.post", side_effect=requests.RequestException)
    def test_agent_search_falls_back_without_external_services(self, _mock_post, _mock_search):
        response = self.client.get("/api/agent/search/", {"q": "周末两天适合爬山"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        self.assertIn("活动-爬山", payload["constraints"])
        self.assertGreaterEqual(len(payload["pois"]), 1)

    def test_manifest_icons_exist(self):
        for filename in ["icon-192.png", "icon-512.png"]:
            path = os.path.join(settings.BASE_DIR, "static", "images", filename)
            self.assertTrue(os.path.exists(path))


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class LoginFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="demo", password="demo123")

    def test_direct_login_redirects_to_home(self):
        response = self.client.post("/login/", {"username": "demo", "password": "demo123"})

        self.assertRedirects(response, "/")

    def test_login_with_next_redirects_to_requested_page(self):
        response = self.client.post(
            "/login/?next=/plan/",
            {"username": "demo", "password": "demo123", "next": "/plan/"},
        )

        self.assertRedirects(response, "/plan/", target_status_code=200)

    def test_authenticated_user_cannot_get_stuck_on_login_page(self):
        self.client.login(username="demo", password="demo123")

        response = self.client.get("/login/")

        self.assertRedirects(response, "/")
