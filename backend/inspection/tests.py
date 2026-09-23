from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from inspection.models import Inspection


def _payload(**overrides):
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
        inspector = Group.objects.create(name="inspector")
        cls.keeper = User.objects.create_user(username="keeper", password="light123456")
        cls.keeper.groups.add(inspector)
        cls.watch = User.objects.create_user(username="watch", password="watch123456")

    def test_keeper_post_saves_row_and_shows_saved_banner(self):
        self.client.login(username="keeper", password="light123456")
        before = Inspection.objects.count()

        response = self.client.post(reverse("create"), _payload())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "已登记")
        self.assertEqual(Inspection.objects.count(), before + 1)
        row = Inspection.objects.latest("id")
        self.assertEqual(row.aid_code, "LH-77")
        self.assertEqual(row.verdict, "合格")
        self.assertEqual(row.created_by, "keeper")

    def test_keeper_post_failing_light_still_saves_row(self):
        self.client.login(username="keeper", password="light123456")
        before = Inspection.objects.count()

        response = self.client.post(
            reverse("create"), _payload(aid_code="LH-78", measured_cd="800")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "已登记")
        self.assertContains(response, "光强不足")
        self.assertEqual(Inspection.objects.count(), before + 1)
        row = Inspection.objects.latest("id")
        self.assertEqual(row.verdict, "不合格")

    def test_watch_post_is_rejected_and_saves_nothing(self):
        self.client.login(username="watch", password="watch123456")
        before = Inspection.objects.count()

        response = self.client.post(reverse("create"), _payload())

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "只读账号不能登记", status_code=403)
        self.assertNotContains(response, "已登记", status_code=403)
        self.assertEqual(Inspection.objects.count(), before)

    def test_watch_get_is_rejected_and_offers_no_form(self):
        self.client.login(username="watch", password="watch123456")
        before = Inspection.objects.count()

        response = self.client.get(reverse("create"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "只读账号不能登记", status_code=403)
        self.assertNotContains(response, "已登记", status_code=403)
        self.assertEqual(Inspection.objects.count(), before)
