"""
Migration 0010 — Add granular permission flags to CustomUser.

Back-fill rationale (preserves every capability existing users already held):
────────────────────────────────────────────────────────────────────────────
perm_draw_roads            → True  for all non-admin users
    Basis: isAuthenticated was the only gate; all logged-in users could draw roads.

perm_edit_own_roads        → True  for all non-admin users
    Basis: isAuthenticated + creator==user was the only gate.

perm_delete_own_roads      → copied from delete_roads
    Basis: delete_feature_request (views.py) checked `user.delete_roads` for ALL
    feature types — verified at line 684 ("any MapFeature, regardless of type").

perm_view_pending_roads    → True  for all non-admin users
    Basis: get_my_draft_features required only isAuthenticated.

perm_approve_roads         → False for all non-admin users  ✅ audited — no regression
    Basis: feature_requests_list is @admin_required; no non-admin ever accessed it.

perm_draw_properties       → True  for all non-admin users
    Basis: same as perm_draw_roads.

perm_edit_own_properties   → True  for all non-admin users
    Basis: same as perm_edit_own_roads.

perm_delete_own_properties → copied from delete_roads
    Basis: delete_feature_request used delete_roads for polygons too (same view,
    no feature_type branch — verified in views.py lines 673–702).

perm_view_pending_properties → True  for all non-admin users
    Basis: same as perm_view_pending_roads.

perm_approve_properties    → False for all non-admin users  ✅ audited — no regression
    Basis: same as perm_approve_roads.

perm_manage_users          → False for all non-admin users
    Basis: user_list is @admin_required.

perm_manage_permissions    → False for all non-admin users
    Basis: delete_road_permission is @admin_required.

Admin users: all 11 flags set to True in the DB for correctness (has_perm_field()
also returns True unconditionally for admins at runtime, so the stored value is
only for data completeness).
"""

from django.db import migrations, models


def backfill_permissions(apps, schema_editor):
    CustomUser = apps.get_model('maps_app', 'CustomUser')

    for user in CustomUser.objects.all():
        is_admin = user.role == 'admin'

        if is_admin:
            # Admins get all flags set to True for DB completeness.
            user.perm_draw_roads             = True
            user.perm_edit_own_roads         = True
            user.perm_delete_own_roads       = True
            user.perm_view_pending_roads     = True
            user.perm_approve_roads          = True
            user.perm_draw_properties        = True
            user.perm_edit_own_properties    = True
            user.perm_delete_own_properties  = True
            user.perm_view_pending_properties = True
            user.perm_approve_properties     = True
            user.perm_manage_users           = True
            user.perm_manage_permissions     = True
        else:
            # Normal users: preserve the capabilities they already held.
            user.perm_draw_roads             = True   # was always allowed
            user.perm_edit_own_roads         = True   # was always allowed
            user.perm_delete_own_roads       = user.delete_roads   # legacy flag
            user.perm_view_pending_roads     = True   # was always allowed
            user.perm_approve_roads          = False  # always admin-only
            user.perm_draw_properties        = True   # was always allowed
            user.perm_edit_own_properties    = True   # was always allowed
            user.perm_delete_own_properties  = user.delete_roads   # same legacy flag governed both
            user.perm_view_pending_properties = True  # was always allowed
            user.perm_approve_properties     = False  # always admin-only
            user.perm_manage_users           = False  # always admin-only
            user.perm_manage_permissions     = False  # always admin-only

        user.save(update_fields=[
            'perm_draw_roads', 'perm_edit_own_roads', 'perm_delete_own_roads',
            'perm_view_pending_roads', 'perm_approve_roads',
            'perm_draw_properties', 'perm_edit_own_properties', 'perm_delete_own_properties',
            'perm_view_pending_properties', 'perm_approve_properties',
            'perm_manage_users', 'perm_manage_permissions',
        ])


def reverse_backfill(apps, schema_editor):
    # No-op: the AddField operations below handle removal on reverse.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('maps_app', '0009_copy_polyline_to_mapfeature'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='perm_draw_roads',
            field=models.BooleanField(default=False, verbose_name='Draw Roads'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_edit_own_roads',
            field=models.BooleanField(default=False, verbose_name='Edit Own Roads'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_delete_own_roads',
            field=models.BooleanField(default=False, verbose_name='Delete Own Roads'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_view_pending_roads',
            field=models.BooleanField(default=False, verbose_name='View Pending Roads'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_approve_roads',
            field=models.BooleanField(default=False, verbose_name='Approve Roads'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_draw_properties',
            field=models.BooleanField(default=False, verbose_name='Draw Properties'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_edit_own_properties',
            field=models.BooleanField(default=False, verbose_name='Edit Own Properties'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_delete_own_properties',
            field=models.BooleanField(default=False, verbose_name='Delete Own Properties'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_view_pending_properties',
            field=models.BooleanField(default=False, verbose_name='View Pending Properties'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_approve_properties',
            field=models.BooleanField(default=False, verbose_name='Approve Properties'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_manage_users',
            field=models.BooleanField(default=False, verbose_name='Manage Users'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='perm_manage_permissions',
            field=models.BooleanField(default=False, verbose_name='Manage Permissions'),
        ),
        migrations.RunPython(backfill_permissions, reverse_code=reverse_backfill),
    ]
