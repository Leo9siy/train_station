from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from station.models import TrainType
from station.serializers import TrainTypeSerializer

types_list = reverse("station:train-types-list")

def get_detail_url(pk: int):
    return reverse(
        "station:train-types-detail",
        kwargs={"pk": pk}
    )

def sample_train_type(name = None):
    def_name = "test"
    if name:
        def_name = name
    return TrainType.objects.create(
        name=def_name
    )


class UnAuthorized(TestCase):
    def test_get_list(self):
        respone = self.client.get(types_list)
        self.assertEqual(200, respone.status_code)

    def test_throttling(self):
        for _ in range(10):
            self.client.get(types_list)
        respone = self.client.get(types_list)
        self.assertEqual(429, respone.status_code)

    def test_get_with_parametrize(self):
        for name in ["d", "a", "b", "c"]:
            sample_train_type(name)

        respone = self.client.get(types_list, data={"name": "a"})
        self.assertEqual(200, respone.status_code)
        self.assertEqual(
            respone.data["results"],
            TrainTypeSerializer(
                TrainType.objects.filter(name__icontains="a"),
                many=True
            ).data)

    def test_post_list(self):
        response = self.client.post(types_list, data={"name": "am"})
        self.assertEqual(response.status_code, 401)

    def test_get_detail(self):
        type = sample_train_type()
        response = self.client.get(get_detail_url(type.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, TrainTypeSerializer(type).data)

    def test_put_patch_destroy_detail(self):
        type = sample_train_type()
        respone = self.client.put(get_detail_url(type.pk), data={"name": "am"})
        self.assertEqual(respone.status_code, 401)

        respone = self.client.patch(get_detail_url(type.pk), data={"name": "am"})
        self.assertEqual(respone.status_code, 401)

        respone = self.client.delete(get_detail_url(type.pk))
        self.assertEqual(respone.status_code, 401)


class Authorized(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email@mail.com",
            password="password"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_list(self):
        respone = self.client.get(types_list)
        self.assertEqual(200, respone.status_code)

    def test_post_list(self):
        response = self.client.post(types_list, data={"name": "am"})
        self.assertEqual(response.status_code, 403)

    def test_get_detail(self):
        type = sample_train_type()
        respone = self.client.get(get_detail_url(type.pk))
        self.assertEqual(respone.status_code, 200)

    def test_put_patch_destroy_detail(self):
        type = sample_train_type()
        respone = self.client.put(get_detail_url(type.pk), data={"name": "am"})
        self.assertEqual(respone.status_code, 403)

        respone = self.client.patch(get_detail_url(type.pk), data={"name": "am"})
        self.assertEqual(respone.status_code, 403)

        respone = self.client.delete(get_detail_url(type.pk))
        self.assertEqual(respone.status_code, 403)


class AdminAuthorized(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email@mail.com",
            password="password",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_list(self):
        respone = self.client.get(types_list)
        self.assertEqual(200, respone.status_code)

    def test_post_list(self):
        response = self.client.post(types_list, data={"name": "am"})
        self.assertEqual(response.status_code, 201)

        response = self.client.get(types_list)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_detail(self):
        type = sample_train_type()
        respone = self.client.get(get_detail_url(type.pk))
        self.assertEqual(respone.status_code, 200)

    def test_put_detail(self):
        type = sample_train_type()
        respone = self.client.put(get_detail_url(type.pk), data={"name": "am"})
        self.assertEqual(respone.status_code, 200)
        type.refresh_from_db()
        self.assertEqual(type.name, "am")

    def test_patch_detail(self):
        type = sample_train_type()
        respone = self.client.patch(get_detail_url(type.pk), data={"name": "am"})
        self.assertEqual(respone.status_code, 200)
        type.refresh_from_db()
        self.assertEqual(type.name, "am")

    def test_delete_detail(self):
        type = sample_train_type()
        respone = self.client.delete(get_detail_url(type.pk))
        self.assertEqual(respone.status_code, 204)
        self.assertEqual(TrainType.objects.count(), 0)
