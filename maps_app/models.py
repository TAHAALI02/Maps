from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_ADMIN = "admin"
    ROLE_USER = "user"
    ROLE_CHOICES = (
        (ROLE_ADMIN, "System Admin"),
        (ROLE_USER, "Normal User"),
    )

    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_OTHER = "O"
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    is_active = models.BooleanField(default=True)


    # ── Granular feature permissions ( road_permission / property_permission) ──
    road_edit_permission = models.BooleanField(default=False, verbose_name="Road Edit Permission")
    road_delete_permission = models.BooleanField(default=False, verbose_name="Road Delete Permission")
    property_edit_permission = models.BooleanField(default=False, verbose_name="Property Edit Permission")
    property_delete_permission = models.BooleanField(default=False, verbose_name="Property Delete Permission")


    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "app_users"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name


TOGGLEABLE_PERMISSIONS = [
    'road_edit_permission',
    'road_delete_permission',
    'property_edit_permission',
    'property_delete_permission',
]

class MapFeature(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )

    FEATURE_POLYLINE = 'polyline'
    FEATURE_POLYGON = 'polygon'
    # FEATURE_CIRCLE = 'circle'
    # FEATURE_RECTANGLE = 'rectangle'
    # FEATURE_MARKER = 'marker'

    FEATURE_TYPE_CHOICES = (
        (FEATURE_POLYLINE, 'Polyline'),
        (FEATURE_POLYGON, 'Polygon'),
        # (FEATURE_CIRCLE, 'Circle'),
        # (FEATURE_RECTANGLE, 'Rectangle'),
        # (FEATURE_MARKER, 'Marker'),
    )

    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPE_CHOICES, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    geometry = models.JSONField()
    style = models.JSONField()

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="map_feature_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_map_feature_requests")
    review_note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    published_snapshot = models.JSONField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    delete_requested = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "map_features"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.feature_type} ({self.status})"