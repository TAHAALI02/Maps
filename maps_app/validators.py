from django.core.exceptions import ValidationError
import re

HEX_COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')


def validate_polyline(geometry, style):
    """Raises ValidationError if geometry/style for a polyline are invalid.
    Mirrors the checks that used to live in PolylineRequestForm."""

    coords = geometry.get('coordinates')
    if not isinstance(coords, list) or len(coords) < 2:
        raise ValidationError("A polyline needs at least 2 coordinate points.")

    for i, pair in enumerate(coords):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValidationError(f"Point {i+1}: each coordinate must be a [lat, lng] pair.")
        lat, lng = pair
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            raise ValidationError(f"Point {i+1}: lat and lng must be numeric.")
        if not (-90 <= lat <= 90):
            raise ValidationError(f"Point {i+1}: latitude {lat} is out of range [-90, 90].")
        if not (-180 <= lng <= 180):
            raise ValidationError(f"Point {i+1}: longitude {lng} is out of range [-180, 180].")

    color = style.get('color', '')
    if not HEX_COLOR_RE.match(color):
        raise ValidationError("Color must be a valid 7-character hex string (e.g. #FF0000).")

    stroke_width = style.get('stroke_width')
    if not isinstance(stroke_width, int) or not (1 <= stroke_width <= 15):
        raise ValidationError("Stroke width must be an integer between 1 and 15.")

    opacity = style.get('opacity')
    if not isinstance(opacity, (int, float)) or not (0.1 <= opacity <= 1.0):
        raise ValidationError("Opacity must be a number between 0.1 and 1.0.")

    if style.get('line_style') not in ('solid', 'dashed', 'dotted'):
        raise ValidationError("Line style must be solid, dashed, or dotted.")





def validate_polygon(geometry, style):
    """Raises ValidationError if geometry/style for a polygon are invalid."""

    coords = geometry.get('coordinates')
    if not isinstance(coords, list) or len(coords) < 3:
        raise ValidationError("A polygon needs at least 3 points.")

    for i, pair in enumerate(coords):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValidationError(f"Point {i+1}: each coordinate must be a [lat, lng] pair.")
        lat, lng = pair
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            raise ValidationError(f"Point {i+1}: lat and lng must be numeric.")
        if not (-90 <= lat <= 90):
            raise ValidationError(f"Point {i+1}: latitude {lat} is out of range [-90, 90].")
        if not (-180 <= lng <= 180):
            raise ValidationError(f"Point {i+1}: longitude {lng} is out of range [-180, 180].")

    # Border color
    color = style.get('color', '')
    if not HEX_COLOR_RE.match(color):
        raise ValidationError("Border color must be a valid 7-character hex string (e.g. #FF0000).")

    # Fill color
    fill_color = style.get('fill_color', '')
    if not HEX_COLOR_RE.match(fill_color):
        raise ValidationError("Fill color must be a valid 7-character hex string (e.g. #FF0000).")

    stroke_width = style.get('stroke_width')
    if not isinstance(stroke_width, int) or not (1 <= stroke_width <= 15):
        raise ValidationError("Border width must be an integer between 1 and 15.")

    opacity = style.get('opacity')
    if not isinstance(opacity, (int, float)) or not (0.1 <= opacity <= 1.0):
        raise ValidationError("Border opacity must be a number between 0.1 and 1.0.")

    fill_opacity = style.get('fill_opacity')
    if not isinstance(fill_opacity, (int, float)) or not (0.0 <= fill_opacity <= 1.0):
        raise ValidationError("Fill opacity must be a number between 0.0 and 1.0.")

    if style.get('line_style') not in ('solid', 'dashed', 'dotted'):
        raise ValidationError("Line style must be solid, dashed, or dotted.")
    



# Add one entry here per new geometry type — nothing else needs to change.
FEATURE_VALIDATORS = {
    'polyline': validate_polyline,
    'polygon': validate_polygon,
}