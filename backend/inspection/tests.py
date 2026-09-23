from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from inspection.models import Inspection


def payload(**overrides):
    data = {
        "aid_code": "LH-77",
        "measured_cd": "1500",
        "required_cd": "1200",
        "bearing_error_deg": "0.3",
    }
    data.update(overrides)
    return data


class RegistrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = Group.objects.create(name="inspector")
        cls.keeper = User.objects.create_user(username="keeper", password="light123456")
        cls.keeper.groups.add(group)
        cls.watch = User.objects.create_user(username="watch", password="watch123456")

    def login(self, username, password):
        self.assertTrue(self.client.login(username=username, password=password))

    def test_keeper_post_writes_row_and_shows_registered(self):
        self.login("keeper", "light123456")
        before = Inspection.objects.count()
        response = self.client.post(reverse("create"), payload())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "已登记")
        self.assertEqual(Inspection.objects.count(), before + 1)
        row = Inspection.objects.latest("id")
        self.assertEqual(row.aid_code, "LH-77")
        self.assertEqual(row.created_by, "keeper")
        self.assertEqual(row.verdict, "合格")

    def test_watch_post_rejected_without_row_or_registered_wording(self):
        self.login("watch", "watch123456")
        before = Inspection.objects.count()
        response = self.client.post(reverse("create"), payload())
        self.assertEqual(response.status_code, 403)
        body = response.content.decode()
        self.assertIn("只读账号不能登记", body)
        self.assertNotIn("已登记", body)
        self.assertEqual(Inspection.objects.count(), before)

    def test_watch_get_entry_rejected_without_registered_wording(self):
        self.login("watch", "watch123456")
        before = Inspection.objects.count()
        response = self.client.get(reverse("create"))
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("已登记", response.content.decode())
        self.assertEqual(Inspection.objects.count(), before)

    def test_keeper_get_form_shows_no_registered_wording_before_write(self):
        self.login("keeper", "light123456")
        response = self.client.get(reverse("create"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("已登记", response.content.decode())

    def test_invalid_post_shows_error_without_row_or_registered_wording(self):
        self.login("keeper", "light123456")
        before = Inspection.objects.count()
        response = self.client.post(reverse("create"), payload(aid_code=""))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("请填编号和三项数值", body)
        self.assertNotIn("已登记", body)
        self.assertEqual(Inspection.objects.count(), before)
