from django.db import migrations


def copy_polylines_forward(apps, schema_editor):
    PolylineRequest = apps.get_model('maps_app', 'PolylineRequest')
    MapFeature = apps.get_model('maps_app', 'MapFeature')

    for pr in PolylineRequest.objects.all():
        geometry = {
            'type': 'LineString',
            'coordinates': pr.coordinates,
        }
        style = {
            'color': pr.color,
            'stroke_width': pr.stroke_width,
            'opacity': pr.opacity,
            'line_style': pr.line_style,
        }

        published_snapshot = None
        if pr.published_snapshot:
            snap = pr.published_snapshot
            published_snapshot = {
                'name': snap.get('name', ''),
                'description': snap.get('description', ''),
                'geometry': {
                    'type': 'LineString',
                    'coordinates': snap.get('coordinates'),
                },
                'style': {
                    'color': snap.get('color'),
                    'stroke_width': snap.get('stroke_width'),
                    'opacity': snap.get('opacity'),
                    'line_style': snap.get('line_style'),
                },
            }

        mf = MapFeature.objects.create(
            feature_type='polyline',
            creator=pr.creator,
            name=pr.name,
            description=pr.description,
            geometry=geometry,
            style=style,
            status=pr.status,
            review_note=pr.review_note,
            reviewed_at=pr.reviewed_at,
            reviewer=pr.reviewer,
            published_snapshot=published_snapshot,
            published_at=pr.published_at,
            delete_requested=pr.delete_requested,
            deleted=pr.deleted,
        )

        # created_at has auto_now_add=True, so create() ignores any value passed for it —
        # overwrite it directly afterward to preserve the original timestamp.
        MapFeature.objects.filter(pk=mf.pk).update(created_at=pr.created_at)


def copy_polylines_backward(apps, schema_editor):
    MapFeature = apps.get_model('maps_app', 'MapFeature')
    MapFeature.objects.filter(feature_type='polyline').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('maps_app', '0008_mapfeature'),   # keep whatever Django already put here — don't change it
    ]

    operations = [
        migrations.RunPython(copy_polylines_forward, copy_polylines_backward),
    ]