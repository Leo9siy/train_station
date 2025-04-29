from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from station.models import Crew
from station.serializers import CrewSerializer


crews_list_url = reverse("station:crew-list")

def get_detail_url(crew_id):
    return reverse("station:crew-detail", args=[crew_id])


def sample_crew(first_name=None, last_name=None):
    attrs = {
        "first_name": "test_first",
        "last_name": "test_last",
    }
    if first_name:
        attrs["first_name"] = first_name
    if last_name:
        attrs["last_name"] = last_name

    return Crew.objects.create(**attrs)


class UnAuthorizedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_crews_list(self):
        response = self.client.get(crews_list_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(crews_list_url, {"first_name": "test"})
        crews = CrewSerializer(Crew.objects.all().filter(first_name__icontains="test"), many=True)
        self.assertEqual(response.data["results"], crews.data)

    def test_get_crews_with_parameters(self):
        sample_crew()
        sample_crew(first_name="not", last_name="not")

        response = self.client.get(crews_list_url, {"first_name": "test"})
        crews = CrewSerializer(Crew.objects.all().filter(first_name__icontains="test"), many=True)
        self.assertEqual(response.data["results"], crews.data)

        response = self.client.get(crews_list_url, {
            "first_name": "not",
            "last_name": "not"
        })
        crews = CrewSerializer(Crew.objects.all().filter(
            Q(first_name__icontains="not")
            & Q(last_name__icontains="not")
        ), many=True)
        self.assertEqual(response.data["results"], crews.data)

    def test_post_crews_list(self):
        response = self.client.post(crews_list_url, {})
        self.assertEqual(response.status_code, 401)

    def test_get_crews_detail(self):
        crew = sample_crew()

        response = self.client.get(get_detail_url(crew.id))
        self.assertEqual(response.status_code, 200)

    def test_patch_put_crews_detail(self):
        crew = sample_crew()
        response = self.client.patch(get_detail_url(crew.id), {"first_name": "test"})
        self.assertEqual(response.status_code, 401)

        response = self.client.put(get_detail_url(crew.id), {"first_name": "test"})
        self.assertEqual(response.status_code, 401)

        response = self.client.delete(get_detail_url(crew.id))
        self.assertEqual(response.status_code, 401)


class AuthorizedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_crews_list(self):
        response = self.client.get(crews_list_url)
        self.assertEqual(response.status_code, 200)

    def test_post_crews_list(self):
        response = self.client.post(crews_list_url, {})
        self.assertEqual(response.status_code, 403)

    def test_get_crews_detail(self):
        crew = sample_crew()

        response = self.client.get(get_detail_url(crew.id))
        self.assertEqual(response.status_code, 200)

    def test_patch_put_crews_detail(self):
        crew = sample_crew()
        response = self.client.patch(get_detail_url(crew.id), {"first_name": "test"})
        self.assertEqual(response.status_code, 403)

        response = self.client.put(get_detail_url(crew.id), {
            "first_name": "test",
            "last_name": "test"
        })
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(get_detail_url(crew.id))
        self.assertEqual(response.status_code, 403)


class AdminAuthorizedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(self.user)

    def test_get_crews_list(self):
        response = self.client.get(crews_list_url)
        self.assertEqual(response.status_code, 200)

    def test_post_empty_crews_list(self):
        response = self.client.post(crews_list_url, {})
        self.assertEqual(response.status_code, 400)

    def test_post_crews_list(self):
        response = self.client.post(crews_list_url, {
            "first_name": "hello",
            "last_name": "world",
        })
        crew = Crew.objects.get(first_name="hello", last_name="world")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, CrewSerializer(crew).data)

        response = self.client.get(crews_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], CrewSerializer(Crew.objects.all(), many=True).data)

    def test_get_crews_detail(self):
        crew = sample_crew()
        response = self.client.get(get_detail_url(crew.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, CrewSerializer(crew).data)

    def test_patch_crews_detail(self):
        crew = sample_crew()
        response = self.client.patch(get_detail_url(crew.id), {
            "first_name": "foxy",
        }, format="json")

        crew.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(crew.first_name, "foxy")

    def test_put_crews_detail(self):
        crew = sample_crew()
        response = self.client.put(get_detail_url(crew.id), {
            "first_name": "foxy",
            "last_name": "world",
        })

        crew.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CrewSerializer(crew).data, response.data)

    def test_delete_crews_detail(self):
        crew = sample_crew()
        response = self.client.delete(get_detail_url(crew.id))
        self.assertEqual(response.status_code, 204)

        response = self.client.get(crews_list_url)
        self.assertEqual(response.data["results"], CrewSerializer(Crew.objects.all(), many=True).data)
