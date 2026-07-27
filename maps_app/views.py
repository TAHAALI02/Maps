from django.shortcuts import render,redirect,get_object_or_404
from functools import wraps
from django.http import HttpResponseForbidden,JsonResponse
from .models import TOGGLEABLE_PERMISSIONS


# Create your views here.

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.role != request.user.ROLE_ADMIN:
            return HttpResponseForbidden("You don't have permission to view this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped

def _require_perm_manage(request):
    """Returns True if user may manage permissions; False otherwise."""
    if not request.user.is_authenticated:
        return False
    return request.user.role == request.user.ROLE_ADMIN



def home(request):
    # form = LocationForm()
    latitude= 24.6877
    longitude= 46.738586
    zoom= 10.5
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "zoom": zoom,
    }
    return render(request,'maps_app/home.html',{'data':data})


# =================================================================================================


from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET, require_POST

from .forms import AdminSignupForm, UserSignupForm, LoginForm
from django.contrib import messages

User = get_user_model()


def admin_signup(request):
    if User.objects.filter(role=User.ROLE_ADMIN).exists():
        return redirect('login')

    if request.method == "POST":
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin account created. You can now log in.")
            return redirect("signup_success")
    else:
        form = AdminSignupForm()
    return render(request, "accounts/admin_signup.html", {"form": form})


def user_signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. You can now log in.")
            return redirect("signup_success")
    else:
        form = UserSignupForm()
    return render(request, "accounts/user_signup.html", {"form": form})


def signup_success(request):
    return render(request, "accounts/signup_success.html")


@require_GET
def check_username(request):
    username = request.GET.get("username", "").strip()
    if not username:
        return JsonResponse({"available": False, "message": "Username cannot be empty."})
    if len(username) < 3:
        return JsonResponse({"available": False, "message": "Username must be at least 3 characters."})
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({
        "available": not exists,
        "message": "Username is already taken." if exists else "Username is available.",
    })

# =========================================================================================
# Login View

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

'''
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Look up the user first so we can tell "locked" apart from "wrong password"
            existing = User.objects.filter(username__iexact=username).first()
            if existing and not existing.is_active:
                messages.error(request, "Your account has been locked by an admin.")
            else:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                    return redirect("home")
                else:
                    form.add_error(None, "Invalid username or password.")
                    messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})'''


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["username"]   # Username or Email
            password = form.cleaned_data["password"]
            # Find user by username or email
            existing = User.objects.filter(username__iexact=identifier).first() or User.objects.filter(
                email__iexact=identifier
            ).first()
            if existing and not existing.is_active:
                messages.error(request, "Your account has been locked by an admin.")
            elif existing:
                # Always authenticate using username
                user = authenticate(
                    request,
                    username=existing.username,
                    password=password
                )
                if user is not None:
                    login(request, user)
                    messages.success(
                        request,
                        f"Welcome back, {user.first_name or user.username}!"
                    )
                    return redirect("home")
                form.add_error(None, "Invalid username/email or password.")
                messages.error(request, "Invalid username/email or password.")
            else:
                form.add_error(None, "Invalid username/email or password.")
                messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request,"You've been logged out")
    return redirect("login")



@admin_required #this is custom 'admin required'
def user_list(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "accounts/user_list.html", {"users": users})

# this for locked
@admin_required #this is custom 'admin required'
def toggle_lock(request, user_id):
    if request.method != "POST":
        return redirect("user_list")
    target = User.objects.filter(id=user_id).first()
    # print(target)
    if not target:
        messages.error(request, "User not found.")
        return redirect("user_list")
    if target.id == request.user.id:
        messages.error(request, "You can't lock your own account.")
        return redirect("user_list")
    target.is_active = not target.is_active
    #       both are same
    '''     or
    if target.is_active:
        target.is_active = False
    else:
        target.is_active = True
    '''
    target.save(update_fields=["is_active"])

    if not target.is_active:
        messages.success(request, f"{target.username}'s account has been locked.")
    else:
        messages.success(request, f"{target.username}'s account has been unlocked.")
    return redirect("user_list")


from django.contrib.auth import update_session_auth_hash
from .forms import AccountInformationForm, PasswordChangeCustomForm
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)

@login_required
def account_information(request):
    user = request.user
    old_email = user.email
    if request.method == "POST":
        if "update_profile" in request.POST:
            profile_form = AccountInformationForm(
                request.POST,
                request.FILES,
                instance=user,
            )
            # empty pswd form
            password_form = PasswordChangeCustomForm()

            # ----------------------------
            # Update Profile
            # ----------------------------            
            if profile_form.is_valid():
                profile_form.save()
                
                # logout if email changed
                if old_email != profile_form.instance.email:
                    logout(request)
                    messages.success(request, "Email updated successfully. Please login using your new email.")
                    return redirect("login")
                messages.success(request,"Profile updated successfully.")
                return redirect("account_information")

        # ----------------------------
        # Change Password
        # ----------------------------
        elif "change_password" in request.POST:
            # Pre-fill profile form
            profile_form = AccountInformationForm(instance=user)

            # Bind only password form
            password_form = PasswordChangeCustomForm(request.POST)

            if password_form.is_valid():
                current = password_form.cleaned_data["current_password"]
                new = password_form.cleaned_data["new_password"]
                if not user.check_password(current):
                    password_form.add_error("current_password","Current password is incorrect.")
                    messages.error( request, "Current password is incorrect." )
                else:
                    user.set_password(new)
                    user.save()
                    # update_session_auth_hash(request, user)
                    logout(request)
                    messages.success( request, "Password changed successfully." )
                    return redirect("login")
    else:
        profile_form = AccountInformationForm(instance=user)
        password_form = PasswordChangeCustomForm()
    return render(request, "accounts/account_information.html",
                  {"profile_form": profile_form, "password_form": password_form,}
                )


# ==========================================================================
# feature Polyline or polygon Approval Workflow — Views
# ==========================================================================
import json
from django.utils import timezone
from .models import MapFeature
from .forms import MapFeatureForm



# this is for all feature (like polyline or polygon or etc ) 
# @login_required
# @require_POST
# def submit_polyline_request(request):
#     """Validate and store a draft polyline as a pending approval request."""
#     try:
#         payload = json.loads(request.body)
#     except (json.JSONDecodeError, ValueError):
#         return JsonResponse(
#             {'errors': {'__all__': [{'message': 'Invalid JSON body.'}]}}, status=400
#         )

#     form_data = {
#         'feature_type': 'polyline', # 'feature_type':  payload.get("feature_type"), 
#         'name': payload.get('name', ''),
#         'description': payload.get('description', ''),
#         'geometry': json.dumps({
#             'type': 'LineString',
#             'coordinates': payload.get('coordinates'),
#         }),
#         'style': json.dumps({
#             'color': payload.get('color'),
#             'stroke_width': payload.get('stroke_width'),
#             'opacity': payload.get('opacity'),
#             'line_style': payload.get('line_style'),
#         }),
#     }

#     form = MapFeatureForm(data=form_data)
#     if not form.is_valid():
#         return JsonResponse({'errors': form.errors.as_json()}, status=400)

#     cd = form.cleaned_data
    

#     mf = MapFeature.objects.create(
#         feature_type='polyline', #feature_type= cd.get('feature_type') or '',
#         creator=request.user,
#         name=cd.get('name') or '',
#         description=cd.get('description') or '',
#         geometry=cd['geometry'],
#         style=cd['style'],
#         status=MapFeature.STATUS_PENDING,
#     )
#     return JsonResponse({'id': mf.id, 'status': mf.status}, status=201)



def _flatten_snapshot(snapshot):
    """published_snapshot can be in either shape:
    - old flat shape (pre-MapFeature): {name, description, coordinates, color, stroke_width, opacity, line_style}
    - new nested shape (post-MapFeature): {name, description, geometry: {...}, style: {...}}
    The 'previous' road map on the requests page expects the flat shape — normalize here."""
    if not snapshot:
        return None
    if 'geometry' in snapshot or 'style' in snapshot:
        geometry = snapshot.get('geometry') or {}
        style = snapshot.get('style') or {}
        return {
            'name': snapshot.get('name', ''),
            'description': snapshot.get('description', ''),
            'feature_type': geometry.get('type') == 'Polygon' and 'polygon' or 'polyline',
            'coordinates': geometry.get('coordinates', []),
            'color': style.get('color'),
            'stroke_width': style.get('stroke_width'),
            'opacity': style.get('opacity'),
            'line_style': style.get('line_style'),
            'fill_color': style.get('fill_color'),
            'fill_opacity': style.get('fill_opacity'),
        }
    return snapshot  # already flat (old format)


# polyline request list
@admin_required
def feature_requests_list(request):
    """Admin page: list pending/approved/rejected feature requests, any type."""
    status_filter = request.GET.get('status', 'pending')
    valid_statuses = ('pending', 'approved', 'rejected', 'all')
    if status_filter not in valid_statuses:
        status_filter = 'pending'

    qs = MapFeature.objects.select_related('creator', 'reviewer')
    if status_filter != 'all':
        qs = qs.filter(status=status_filter)

    TYPE_LABELS = {
        MapFeature.FEATURE_POLYLINE: 'Road',
        MapFeature.FEATURE_POLYGON:  'Property',
    }

    requests_list = list(qs)
    for req in requests_list:
        flat_previous = _flatten_snapshot(req.published_snapshot)

        req.type_label = TYPE_LABELS.get(req.feature_type, 'Feature')

        req.poly_data = {
            'feature_type': req.feature_type,
            'current': {
                'feature_type': req.feature_type,   # ← add this line
                'coords': req.geometry.get('coordinates', []),
                'color': req.style.get('color'),
                'weight': req.style.get('stroke_width'),
                'opacity': req.style.get('opacity'),
                'line_style': req.style.get('line_style'),
                'fill_color': req.style.get('fill_color'),
                'fill_opacity': req.style.get('fill_opacity'),
            },
            'previous': flat_previous,
        }

        req.coordinates  = req.geometry.get('coordinates', [])
        req.color        = req.style.get('color')
        req.stroke_width = req.style.get('stroke_width')
        req.opacity      = req.style.get('opacity')
        req.line_style   = req.style.get('line_style')
        req.fill_color   = req.style.get('fill_color')
        req.fill_opacity = req.style.get('fill_opacity')

        req.published_snapshot = flat_previous

    context = {
        'requests':       requests_list,
        'status_filter':  status_filter,
        'pending_count':  MapFeature.objects.filter(status=MapFeature.STATUS_PENDING).count(),
        'approved_count': MapFeature.objects.filter(status=MapFeature.STATUS_APPROVED).count(),
        'rejected_count': MapFeature.objects.filter(status=MapFeature.STATUS_REJECTED).count(),
        'road_pending':    MapFeature.objects.filter(status=MapFeature.STATUS_PENDING,  feature_type=MapFeature.FEATURE_POLYLINE).count(),
        'road_approved':   MapFeature.objects.filter(status=MapFeature.STATUS_APPROVED, feature_type=MapFeature.FEATURE_POLYLINE).count(),
        'road_rejected':   MapFeature.objects.filter(status=MapFeature.STATUS_REJECTED, feature_type=MapFeature.FEATURE_POLYLINE).count(),
        'property_pending':    MapFeature.objects.filter(status=MapFeature.STATUS_PENDING,  feature_type=MapFeature.FEATURE_POLYGON).count(),
        'property_approved':   MapFeature.objects.filter(status=MapFeature.STATUS_APPROVED, feature_type=MapFeature.FEATURE_POLYGON).count(),
        'property_rejected':   MapFeature.objects.filter(status=MapFeature.STATUS_REJECTED, feature_type=MapFeature.FEATURE_POLYGON).count(),
    }
    return render(request, 'maps_app/polyline_requests.html', context)


# review a request in user-list (review request list)
@admin_required
@require_POST
def review_feature_request(request, pk):
    """Approve or reject a pending feature request, any type."""

    mf = MapFeature.objects.filter(pk=pk, status=MapFeature.STATUS_PENDING).first()

    if not mf:
        messages.error(request, "Request not found or already reviewed.")
        return redirect("polyline_requests_list")

    action = request.POST.get("action", "").strip()
    review_note = request.POST.get("review_note", "").strip()

    if action == "approve":
        mf.status = MapFeature.STATUS_APPROVED
        mf.reviewer = request.user
        mf.reviewed_at = timezone.now()
        mf.review_note = review_note or None

        if mf.delete_requested:
            mf.deleted = True
            mf.delete_requested = False
            mf.save(update_fields=[
                "status", "reviewer", "reviewed_at", "review_note",
                "deleted", "delete_requested",
            ])
            messages.success(request, f"'{mf.name or 'Unnamed'}' has been deleted successfully.")
        else:
            mf.published_snapshot = {
                "name": mf.name,
                "description": mf.description,
                "geometry": mf.geometry,
                "style": mf.style,
            }
            mf.published_at = mf.reviewed_at
            mf.save(update_fields=[
                "status", "reviewer", "reviewed_at", "review_note",
                "published_snapshot", "published_at",
            ])
            messages.success(request, f"'{mf.name or 'Unnamed'}' approved and published to the map.")

    elif action == "reject":
        if not review_note:
            messages.error(request, "A review note is required when rejecting a request.")
            return redirect("polyline_requests_list")

        mf.status = MapFeature.STATUS_REJECTED
        mf.reviewer = request.user
        mf.reviewed_at = timezone.now()
        mf.review_note = review_note

        if mf.delete_requested:
            mf.delete_requested = False
            mf.save(update_fields=["status", "reviewer", "reviewed_at", "review_note", "delete_requested"])
            messages.info(request, f"Deletion request for '{mf.name or 'Unnamed'}' was rejected.")
        else:
            mf.save(update_fields=["status", "reviewer", "reviewed_at", "review_note"])
            messages.info(request, f"'{mf.name or 'Unnamed'}' rejected.")

    else:
        messages.error(request, "Invalid action.")

    return redirect("polyline_requests_list")


@login_required
@require_GET
def get_approved_features(request):
    """Returns the last-approved snapshot for every feature ever approved,
    across all types, including creator profile info."""
    qs = MapFeature.objects.filter(deleted=False).exclude(published_snapshot__isnull=True)

    features = []
    for mf in qs:
        creator = mf.creator
        full_name = f"{creator.first_name} {creator.last_name}".strip()
        snap = mf.published_snapshot or {}
        features.append({
            'id': mf.id,
            'feature_type': mf.feature_type,
            'creator_id': creator.id,
            'creator_name': full_name or creator.username,
            'creator_username': creator.username,
            'creator_profile_image': creator.profile_image.url if creator.profile_image else None,
            'current_status': mf.status,
            'published_at': mf.published_at.strftime('%b %d, %Y %H:%M') if mf.published_at else None,
            'name': snap.get('name', ''),
            'description': snap.get('description', ''),
            'geometry': snap.get('geometry', {}),
            'style': snap.get('style', {}),
        })

    can_edit_roads = False
    can_delete_roads = False
    can_edit_properties = False
    can_delete_properties = False

    if request.user.is_authenticated:
        if request.user.role == request.user.ROLE_ADMIN:
            can_edit_roads = True
            can_delete_roads = True
            can_edit_properties = True
            can_delete_properties = True
        else:
            can_edit_roads = getattr(request.user, 'road_edit_permission', False)
            can_delete_roads = getattr(request.user, 'road_delete_permission', False)
            can_edit_properties = getattr(request.user, 'property_edit_permission', False)
            can_delete_properties = getattr(request.user, 'property_delete_permission', False)

    # if request.user.is_authenticated:
    #     if request.user.role == request.user.ROLE_ADMIN:
    #         can_delete_roads = True
    #         can_delete_properties = True
    #     else:
    #         can_delete_roads = getattr(request.user, 'road_permission', False)
    #         can_delete_properties = getattr(request.user, 'property_permission', False)

    response_data = {
        "features": features,
        "current_user_id": request.user.id if request.user.is_authenticated else None,
        "can_edit_roads": can_edit_roads,
        "can_delete_roads": can_delete_roads,
        "can_edit_properties": can_edit_properties,
        "can_delete_properties": can_delete_properties,
        "is_superuser": getattr(request.user, 'is_superuser', False),
    }

    return JsonResponse(response_data)

@admin_required
@require_POST
def purge_rejected_requests(request):
    """Hard-delete all rejected feature requests, any type."""
    count, _ = MapFeature.objects.filter(status=MapFeature.STATUS_REJECTED).delete()
    messages.success(request, f"{count} rejected request(s) permanently purged.")
    return redirect('feature_requests_list')


# @login_required
# @require_POST
# def edit_polyline_request(request, pk):
#     """Creator edits their own polyline. If it had already been reviewed,
#     editing sends it back to pending for a fresh review."""

#     mf = MapFeature.objects.filter(pk=pk, feature_type='polyline', creator=request.user).first()
    
#     if not mf:
#         messages.error(request, 'Request not found.')
#         return redirect('home')
#     if mf.status == MapFeature.STATUS_PENDING:
#         return JsonResponse(
#             {
#                 "success": False,
#                 "message": "This road already has a pending approval request."
#             },
#             status=400,
#         )

#     try:
#         payload = json.loads(request.body)
#     except (json.JSONDecodeError, ValueError):
#         return JsonResponse({'errors': {'__all__': [{'message': 'Invalid JSON body.'}]}}, status=400)

#     form_data = {
#         'feature_type': 'polyline',
#         'name': payload.get('name', ''),
#         'description': payload.get('description', ''),
#         'geometry': json.dumps({
#             'type': 'LineString',
#             'coordinates': payload.get('coordinates'),
#         }),
#         'style': json.dumps({
#             'color': payload.get('color'),
#             'stroke_width': payload.get('stroke_width'),
#             'opacity': payload.get('opacity'),
#             'line_style': payload.get('line_style'),
#         }),
#     }

#     form = MapFeatureForm(data=form_data)
#     if not form.is_valid():
#         return JsonResponse({'errors': form.errors.as_json()}, status=400)

#     cd = form.cleaned_data
#     mf.name = cd.get('name') or ''
#     mf.description = cd.get('description') or ''
#     mf.geometry = cd['geometry']
#     mf.style = cd['style']

#     already_reviewed = mf.status != MapFeature.STATUS_PENDING
#     if already_reviewed:
#         mf.status = MapFeature.STATUS_PENDING
#         mf.reviewer = None
#         mf.reviewed_at = None
#         mf.review_note = None

#     mf.save()

#     return JsonResponse({
#         'id': mf.id,
#         'status': mf.status,
#         'resubmitted': already_reviewed,
#     }, status=200)




@login_required
@require_GET
def get_my_draft_features(request):
    """Returns the current user's own pending/rejected features, across all types."""
    qs = MapFeature.objects.filter(creator=request.user).exclude(status=MapFeature.STATUS_APPROVED)

    features = []
    for mf in qs:
        features.append({
            'id': mf.id,
            'feature_type': mf.feature_type,
            'name': mf.name,
            'description': mf.description,
            'geometry': mf.geometry,
            'style': mf.style,
            'status': mf.status,
            'review_note': mf.review_note,
            'delete_requested': mf.delete_requested,
        })

    return JsonResponse({'features': features})




@login_required
@require_POST
def delete_feature_request(request, pk):
    """Deletes or requests deletion of any MapFeature, regardless of type."""

    mf = get_object_or_404(MapFeature, pk=pk)
    if request.user.is_superuser:
        mf.deleted = True
        mf.save(update_fields=["deleted"])
        return JsonResponse({"success": True, "message": "Feature deleted successfully."})

    perm_needed = 'road_delete_permission' if mf.feature_type == MapFeature.FEATURE_POLYLINE else 'property_delete_permission'
    if not getattr(request.user, perm_needed, False):
        return JsonResponse({
            "success": False,
            "message": "You don't have permission to delete this."
        }, status=403)

    mf = get_object_or_404(MapFeature, pk=pk, creator=request.user)

    if mf.delete_requested:
        return JsonResponse({"success": False, "message": "Deletion request already submitted."}, status=400)

    mf.delete_requested = True
    mf.status = MapFeature.STATUS_PENDING
    mf.reviewer = None
    mf.reviewed_at = None
    mf.review_note = None
    mf.save(update_fields=["delete_requested", "status", "reviewer", "reviewed_at", "review_note"])

    return JsonResponse({"success": True, "message": "Deletion request sent for approval."})



@login_required
@require_POST
def submit_feature_request(request):
    """Validate and store a draft feature (any type) as a pending approval request."""
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'errors': {'__all__': [{'message': 'Invalid JSON body.'}]}}, status=400)

    form_data = {
        'feature_type': payload.get('feature_type', ''),
        'name': payload.get('name', ''),
        'description': payload.get('description', ''),
        'geometry': json.dumps(payload.get('geometry') or {}),
        'style': json.dumps(payload.get('style') or {}),
    }

    form = MapFeatureForm(data=form_data)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors.as_json()}, status=400)

    cd = form.cleaned_data

    if request.user.is_superuser:
        mf = MapFeature.objects.create(
            feature_type = cd['feature_type'],
            creator = request.user,
            name = cd.get('name') or '',
            description = cd.get('description') or '',
            geometry = cd['geometry'],
            style = cd['style'],
            status = MapFeature.STATUS_APPROVED,
            reviewer = request.user,
            reviewed_at = timezone.now(),
            published_at = timezone.now(),
            published_snapshot = {
                "name" : cd.get("name") or "",
                "description" : cd.get("description") or "",
                "geometry" : cd["geometry"],
                "style" : cd["style"],
            }
        )
    else:
        mf = MapFeature.objects.create(
            feature_type=cd['feature_type'],
            creator=request.user,
            name=cd.get('name') or '',
            description=cd.get('description') or '',
            geometry=cd['geometry'],
            style=cd['style'],
            status=MapFeature.STATUS_PENDING,
        )
    return JsonResponse({'id': mf.id, 'status': mf.status}, status=201)


@login_required
@require_POST
def edit_feature_request(request, pk):
    """Creator edits their own feature; superusers can edit any feature."""

    if request.user.is_superuser:
        mf = MapFeature.objects.filter(pk=pk).first()
    else:
        mf = MapFeature.objects.filter(pk=pk, creator=request.user).first()
        if mf:
            perm_needed = 'road_edit_permission' if mf.feature_type == MapFeature.FEATURE_POLYLINE else 'property_edit_permission'
            if not getattr(request.user, perm_needed, False):
                return JsonResponse({'errors': {'__all__': [{'message': 'Permission denied.'}]}}, status=403)

    if not mf:
        messages.error(request, 'Request not found.')
        return redirect('home')

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'errors': {'__all__': [{'message': 'Invalid JSON body.'}]}}, status=400)

    form_data = {
        'feature_type': mf.feature_type,
        'name': payload.get('name', ''),
        'description': payload.get('description', ''),
        'geometry': json.dumps(payload.get('geometry') or {}),
        'style': json.dumps(payload.get('style') or {}),
    }

    form = MapFeatureForm(data=form_data)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors.as_json()}, status=400)

    cd = form.cleaned_data
    mf.name = cd.get('name') or ''
    mf.description = cd.get('description') or ''
    mf.geometry = cd['geometry']
    mf.style = cd['style']

    already_reviewed = False

    if request.user.is_superuser:
        mf.status = MapFeature.STATUS_APPROVED
        mf.reviewer = request.user
        mf.reviewed_at = timezone.now()
        mf.published_at = timezone.now()
        mf.review_note = None
        mf.published_snapshot = {
            "name" : mf.name,
            "description": mf.description,
            "geometry": mf.geometry,
            "style": mf.style,
        }
        mf.published_at = timezone.now()

        # mf.save()

        # return JsonResponse({
        #     "id": mf.id,
        #     "status": mf.status,
        #     "resubmitted": False,
        # })
    else:
        already_reviewed = mf.status != MapFeature.STATUS_PENDING
        if already_reviewed:
            mf.status = MapFeature.STATUS_PENDING
            mf.reviewer = None
            mf.reviewed_at = None
            mf.review_note = None

    mf.save()

    return JsonResponse({
        'id': mf.id,
        'status': mf.status,
        'resubmitted': already_reviewed,
    }, status=200)

# ============================================================================================
# Granular Permissions Management

# @admin_required
def manage_permissions(request):
    if not _require_perm_manage(request):
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    # User = get_user_model()
    users = User.objects.exclude(role="system_admin").exclude(is_superuser=True).order_by("id")
    return render(request, 'maps_app/manage_permissions.html', {'users': users})

@require_POST
def toggle_permission(request, user_id, perm_name):
    if not _require_perm_manage(request):
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    if perm_name not in TOGGLEABLE_PERMISSIONS:
        return JsonResponse({'error': 'Invalid permission.'}, status=400)

    from django.contrib.auth import get_user_model
    User = get_user_model()
    target_user = get_object_or_404(User, id=user_id)

    if target_user.id == request.user.id:
        return JsonResponse({'error': 'Cannot modify own permissions.'}, status=400)
    
    if target_user.role == User.ROLE_ADMIN:
        return JsonResponse({'error': 'Cannot modify admin permissions.'}, status=400)

    current_val = getattr(target_user, perm_name, False)
    setattr(target_user, perm_name, not current_val)
    target_user.save(update_fields=[perm_name])

    return JsonResponse({'success': True, 'new_value': not current_val})