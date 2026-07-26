from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import TOGGLEABLE_PERMISSIONS, MapFeature

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_normal_user(username='testuser', road_permission=False, property_permission=False):
    """Create a normal (non-admin) user with specified permissions."""
    return User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='Testpass1!',
        role=User.ROLE_USER,
        road_permission=road_permission,
        property_permission=property_permission,
    )


def make_admin_user(username='adminuser'):
    """Create an admin user."""
    return User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='Testpass1!',
        role=User.ROLE_ADMIN,
        is_staff=True,
        is_superuser=True,
    )


# ---------------------------------------------------------------------------
# 1. Permission field tests
# ---------------------------------------------------------------------------

class PermissionFieldTest(TestCase):
    """
    Verify that road_permission and property_permission fields work correctly
    and that the is_admin property returns the right value.
    """

    def test_normal_user_defaults_false(self):
        """New normal users should have both permissions False by default."""
        user = make_normal_user('defaults')
        self.assertFalse(user.road_permission)
        self.assertFalse(user.property_permission)

    def test_normal_user_with_road_permission(self):
        """Normal user can be granted road_permission."""
        user = make_normal_user('roaduser', road_permission=True)
        self.assertTrue(user.road_permission)
        self.assertFalse(user.property_permission)

    def test_normal_user_with_property_permission(self):
        """Normal user can be granted property_permission."""
        user = make_normal_user('propuser', property_permission=True)
        self.assertFalse(user.road_permission)
        self.assertTrue(user.property_permission)

    def test_normal_user_with_both_permissions(self):
        """Normal user can be granted both permissions."""
        user = make_normal_user('bothuser', road_permission=True, property_permission=True)
        self.assertTrue(user.road_permission)
        self.assertTrue(user.property_permission)

    def test_is_admin_property_for_admin(self):
        """is_admin property returns True for admin users."""
        admin = make_admin_user()
        self.assertTrue(admin.is_admin)

    def test_is_admin_property_for_normal(self):
        """is_admin property returns False for normal users."""
        user = make_normal_user('notadmin')
        self.assertFalse(user.is_admin)


# ---------------------------------------------------------------------------
# 2. TOGGLEABLE_PERMISSIONS whitelist guard
# ---------------------------------------------------------------------------

class TogglePermissionWhitelistTest(TestCase):
    """
    toggle_permission must reject any perm_name not in TOGGLEABLE_PERMISSIONS.
    """

    def setUp(self):
        self.admin = make_admin_user('wl_admin')
        self.target = make_normal_user('wl_target')
        self.client = Client()
        self.client.force_login(self.admin)

    def _toggle_url(self, user_id, perm_name):
        return reverse('toggle_permission', args=[user_id, perm_name])

    def test_road_permission_accepted(self):
        """road_permission is a valid toggle target and returns 200."""
        url = self._toggle_url(self.target.id, 'road_permission')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

    def test_property_permission_accepted(self):
        """property_permission is a valid toggle target and returns 200."""
        url = self._toggle_url(self.target.id, 'property_permission')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

    def test_is_superuser_rejected_400(self):
        """Attempting to toggle is_superuser is rejected with 400."""
        url = self._toggle_url(self.target.id, 'is_superuser')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 400)

    def test_is_staff_rejected_400(self):
        """Attempting to toggle is_staff is rejected with 400."""
        url = self._toggle_url(self.target.id, 'is_staff')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 400)

    def test_arbitrary_string_rejected_400(self):
        """Arbitrary string not in whitelist is rejected with 400."""
        url = self._toggle_url(self.target.id, 'password')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 400)

    def test_toggle_actually_flips_value(self):
        """Toggling road_permission flips it from False to True."""
        self.assertFalse(self.target.road_permission)
        url = self._toggle_url(self.target.id, 'road_permission')
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.target.refresh_from_db()
        self.assertTrue(self.target.road_permission)

    def test_toggle_flips_back(self):
        """Toggling road_permission twice returns it to original value."""
        url = self._toggle_url(self.target.id, 'road_permission')
        self.client.post(url)  # False -> True
        self.client.post(url)  # True -> False
        self.target.refresh_from_db()
        self.assertFalse(self.target.road_permission)


# ---------------------------------------------------------------------------
# 3. Server-side authorization guards on manage_permissions / toggle_permission
# ---------------------------------------------------------------------------

class ManagePermissionsAuthTest(TestCase):
    """
    Both manage_permissions and toggle_permission must return 403 for users
    who are not admins.
    """

    def setUp(self):
        self.normal = make_normal_user('auth_normal')
        self.admin = make_admin_user('auth_admin')
        self.target = make_normal_user('auth_target')
        self.client = Client()

    def test_manage_permissions_403_for_normal_user(self):
        """Normal user gets 403 on GET."""
        self.client.force_login(self.normal)
        resp = self.client.get(reverse('manage_permissions'))
        self.assertEqual(resp.status_code, 403)

    def test_manage_permissions_200_for_admin(self):
        """Admin always gets 200."""
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('manage_permissions'))
        self.assertEqual(resp.status_code, 200)

    def test_toggle_permission_403_for_normal_user(self):
        """Normal user gets 403 on POST."""
        self.client.force_login(self.normal)
        url = reverse('toggle_permission', args=[self.target.id, 'road_permission'])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)

    def test_toggle_permission_200_for_admin(self):
        """Admin can toggle a valid permission."""
        self.client.force_login(self.admin)
        url = reverse('toggle_permission', args=[self.target.id, 'road_permission'])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

    def test_manage_permissions_redirects_anonymous(self):
        """Anonymous user is redirected to login."""
        resp = self.client.get(reverse('manage_permissions'))
        self.assertIn(resp.status_code, [302, 403])


# ---------------------------------------------------------------------------
# 4. submit_feature_request — no draw-permission gate
# ---------------------------------------------------------------------------

class SubmitFeaturePermissionTest(TestCase):
    """
    With the simplified 2-permission model, any authenticated user can submit
    (draw) features. The permission only gates edit/delete.
    """

    ROAD_PAYLOAD = {
        'feature_type': 'polyline',
        'name': 'Test Road',
        'description': '',
        'geometry': {'type': 'LineString', 'coordinates': [[24.0, 46.0], [24.1, 46.1]]},
        'style': {'color': '#ff0000', 'stroke_width': 4, 'opacity': 0.8, 'line_style': 'solid'},
    }
    PROPERTY_PAYLOAD = {
        'feature_type': 'polygon',
        'name': 'Test Property',
        'description': '',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [[24.0, 46.0], [24.1, 46.0], [24.1, 46.1], [24.0, 46.0]]
        },
        'style': {
            'color': '#00ff00', 'fill_color': '#33cc33',
            'stroke_width': 2, 'opacity': 0.8,
            'fill_opacity': 0.4, 'line_style': 'solid'
        },
    }

    def setUp(self):
        self.client = Client()
        self.url = reverse('submit_feature_request')

    def _post(self, user, payload):
        self.client.force_login(user)
        import json
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_draw_road_without_perm_returns_201(self):
        """Any authenticated user can submit a road (draw is ungated)."""
        user = make_normal_user('noroad')
        resp = self._post(user, self.ROAD_PAYLOAD)
        self.assertEqual(resp.status_code, 201)

    def test_draw_property_without_perm_returns_201(self):
        """Any authenticated user can submit a property (draw is ungated)."""
        user = make_normal_user('noprop')
        resp = self._post(user, self.PROPERTY_PAYLOAD)
        self.assertEqual(resp.status_code, 201)

    def test_anonymous_cannot_submit(self):
        """Anonymous users cannot submit features."""
        import json
        resp = self.client.post(
            self.url,
            data=json.dumps(self.ROAD_PAYLOAD),
            content_type='application/json',
        )
        # Should redirect to login or return 403
        self.assertIn(resp.status_code, [302, 403])