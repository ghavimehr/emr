from django.urls import path
from apps.dashboard import views


urlpatterns = [
    # Blog articles
    path('blogs/', views.blog_dashboard, name="blog_dashboard"),
    path('all-blogs/', views.all_blogs, name="all_blogs"),
    path("create-blog/", views.create_blog, name="create_blog"),
    path('update-blog/<str:slug>/', views.update_blog, name="update_blog"),
    path('delete-blog/<str:slug>/', views.delete_blog, name="delete_blog"),
    path('bookmarked-blog/', views.bookmarked_blog, name="bookmarked_blog"),

    # Products
    path('products/', views.product_dashboard, name="product_dashboard"),
    path('create-product/', views.create_product, name="create_product"),
    path('update-product/<str:slug>/', views.update_product, name="update_product"),
    path('delete-product/<str:slug>/', views.delete_product, name="delete_product"),

    # Props
    path('create-props/', views.create_props, name="create_props"),
    path('update-props/<int:pk>/', views.update_prop, name="update_prop"),
    path('delete-props/<int:pk>/', views.delete_prop, name="delete_prop"),

    # Teams
    path('teams/', views.team_list, name="dashboard_team_list"),
    path('team-detail/<int:team_id>/', views.team_detail, name="dashboard_team_detail"),
    path('team-update/<int:team_id>/', views.edit_team, name="dashboard_edit_team"),
    path('team-delete/<int:team_id>/', views.delete_team, name="dashboard_delete_team"),
    path('remove-member/<int:team_id>/<int:profile_id>/', views.remove_team_member, name="remove_team_member"),
    path('create-team/', views.create_team, name='create_team'),

    # Projects
    path('projects/', views.project_list, name="dashboard_project_list"),
    path('project-update/<int:project_id>/', views.edit_project, name="dashboard_edit_project"),
    path('project-delete/<int:project_id>/', views.delete_project, name="dashboard_delete_project"),
    path('create-project/', views.create_project, name='create_project'),

    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile_original/', views.profile_original, name='profile_original'),
    path('api/', views.api_view, name='api_view'),
    path('regenerate-token/', views.regenerate_token, name='regenerate_token'),
    path('stats/', views.stats, name='stats'),
    path('promo/', views.promo, name='promo'),
    path('update-skills/', views.update_skills, name='update_skills'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('toggle-profile-role/', views.toggle_profile_role, name='toggle_profile_role'),
    path('freelancers/', views.freelancer_list, name='freelancer_list'),

    # Invitation
    path('invite/<int:profile_id>/', views.invite_freelancer, name='invite_freelancer'),
    path('invitations/', views.invitation_list, name='invitation_list'),
    path('accept-invitations/<int:id>/', views.accept_invitations, name='accept_invitations'),
    path('deny-invitations/<int:id>/', views.deny_invitations, name='deny_invitations'),
    path('my-projects/', views.my_projects, name='my_projects'),

    # Downloads
    path('free-downloads/', views.free_downloads, name='free_downloads'),
    path('paid-downloads/', views.paid_downloads, name='paid_downloads'),

    # User
    path('users/', views.user_list, name='user_list'),
    path('send/<int:user_id>/', views.send_email_to_user, name='send_email_to_user'),
]
