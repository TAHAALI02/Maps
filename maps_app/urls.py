from django.urls import path
from . import views
from django.views.generic import RedirectView



from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("onetime/", views.admin_signup, name="admin_signup"),
    path("signup/", views.user_signup, name="signup"),
    path("signup/success/", views.signup_success, name="signup_success"),
    path("api/check-username/", views.check_username, name="check_username"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("manage-users/", views.user_list, name="user_list"),
    path("manage-users/<int:user_id>/toggle-lock/", views.toggle_lock, name="toggle_lock"),
    path("account/", views.account_information, name="account_information"),

    # ──────────────────── Polyline / Feature Approval Workflow ──────────────────────────────
    path('features/approved/', views.get_approved_features, name='get_approved_features'),
    path('features/my-drafts/', views.get_my_draft_features, name='get_my_draft_features'),
    path("polyline/requests/", views.feature_requests_list, name="polyline_requests_list"),
    path("polyline/requests/<int:pk>/review/", views.review_feature_request, name="review_polyline_request"),
    path("polyline/requests/purge/", views.purge_rejected_requests, name="purge_rejected_requests"),
    path('features/<int:pk>/delete/', views.delete_feature_request, name='delete_feature_request'),
    path('features/submit/', views.submit_feature_request, name='submit_feature_request'),
    path('features/<int:pk>/edit/', views.edit_feature_request, name='edit_feature_request'),

    # ──────────────────── Granular Permissions Management ────────────────────────────────────
    path("manage-permissions/", views.manage_permissions, name="manage_permissions"),
    path("manage-permissions/<int:user_id>/toggle/<str:perm_name>/", views.toggle_permission, name="toggle_permission"),
]




# urlpatterns = [
#     path('', views.home, name='home'),
#     path("onetime/", views.admin_signup, name="admin_signup"),
#     path("signup/", views.user_signup, name="signup"),
#     path("signup/success/", views.signup_success, name="signup_success"),
#     path("api/check-username/", views.check_username, name="check_username"),
#     path("login/", views.login_view, name="login"),
#     path("logout/", views.logout_view, name="logout"),
#     path("manage-users/", views.user_list, name="user_list"),
#     path("manage-users/<int:user_id>/toggle-lock/", views.toggle_lock, name="toggle_lock"),
#     path("account/", views.account_information, name="account_information",),
#     # ──────────────────── Polyline Approval Workflow ──────────────────────────────────────────
#     # path("polyline/submit/",                                views.submit_polyline_request,   name="submit_polyline_request"),
#     # path("polyline/approved/",                              views.get_approved_polylines,    name="get_approved_polylines"),
#     # =================================
#     path('features/approved/', views.get_approved_features, name='get_approved_features'),
#     path('features/my-drafts/', views.get_my_draft_features, name='get_my_draft_features'),
#     path("polyline/requests/",                              views.feature_requests_list,    name="polyline_requests_list"),
#     path("polyline/requests/<int:pk>/review/",              views.review_feature_request,   name="review_polyline_request"),
#     path("polyline/requests/purge/",                        views.purge_rejected_requests,   name="purge_rejected_requests"),
#     # path('polylines/mine/',                                 views.get_my_draft_polylines,    name='get_my_draft_polylines'),
#     # path('polylines/<int:pk>/edit/',                        views.edit_polyline_request,     name='edit_polyline_request'),
#     path('features/<int:pk>/delete/', views.delete_feature_request, name='delete_feature_request'),
#     # Permission for delete polyline 
#     path("manage-permissions/", views.manage_permissions, name="manage_permissions"),
#     path("manage-permissions/<int:user_id>/toggle/<str:perm_name>/", views.toggle_permission, name="toggle_permission"),
#     path("road-delete-permissions/", RedirectView.as_view(pattern_name="manage_permissions"), name="delete_permission_list"),
#     path('features/submit/', views.submit_feature_request, name='submit_feature_request'),
#     path('features/<int:pk>/edit/', views.edit_feature_request, name='edit_feature_request'),
# ]