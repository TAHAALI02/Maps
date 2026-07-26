"""
Migration 0011 — Simplify permissions to road_permission + property_permission.

This migration:
1. Renames delete_roads → road_permission (preserving existing data).
2. Adds property_permission (new field).
3. Removes all 12 granular perm_* fields added in 0010.
4. Back-fills property_permission from the old delete_roads value
   (which is now road_permission after rename).
"""

from django.db import migrations, models


def backfill_property_permission(apps, schema_editor):
    """
    Copy road_permission (formerly delete_roads) value to property_permission
    for every user, since delete_roads historically governed both roads and
    properties.  Admins get True for both.
    """
    CustomUser = apps.get_model('maps_app', 'CustomUser')
    for user in CustomUser.objects.all():
        if user.role == 'admin':
            user.road_permission = True
            user.property_permission = True
        else:
            # road_permission already has the old delete_roads value via rename
            user.property_permission = user.road_permission
        user.save(update_fields=['road_permission', 'property_permission'])


def reverse_backfill(apps, schema_editor):
    pass  # No-op: RenameField handles the reverse rename automatically.


class Migration(migrations.Migration):

    dependencies = [
        ('maps_app', '0010_customuser_granular_permissions'),
    ]

    operations = [
        # ── Step 1: Rename delete_roads → road_permission ──────────────────
        migrations.RenameField(
            model_name='customuser',
            old_name='delete_roads',
            new_name='road_permission',
        ),

        # ── Step 2: Add property_permission ────────────────────────────────
        migrations.AddField(
            model_name='customuser',
            name='property_permission',
            field=models.BooleanField(default=False, verbose_name='Property Permission'),
        ),

        # ── Step 3: Back-fill property_permission from road_permission ─────
        migrations.RunPython(backfill_property_permission, reverse_code=reverse_backfill),

        # ── Step 4: Remove all 12 granular perm_* fields ───────────────────
        migrations.RemoveField(model_name='customuser', name='perm_draw_roads'),
        migrations.RemoveField(model_name='customuser', name='perm_edit_own_roads'),
        migrations.RemoveField(model_name='customuser', name='perm_delete_own_roads'),
        migrations.RemoveField(model_name='customuser', name='perm_view_pending_roads'),
        migrations.RemoveField(model_name='customuser', name='perm_approve_roads'),
        migrations.RemoveField(model_name='customuser', name='perm_draw_properties'),
        migrations.RemoveField(model_name='customuser', name='perm_edit_own_properties'),
        migrations.RemoveField(model_name='customuser', name='perm_delete_own_properties'),
        migrations.RemoveField(model_name='customuser', name='perm_view_pending_properties'),
        migrations.RemoveField(model_name='customuser', name='perm_approve_properties'),
        migrations.RemoveField(model_name='customuser', name='perm_manage_users'),
        migrations.RemoveField(model_name='customuser', name='perm_manage_permissions'),
    ]
