from django.shortcuts import render
from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views


def add_pig_breeder(request):
    return render(request, "add_pig_breeder.html")


urlpatterns = [
    path("", views.MainView.as_view(), name="Main"),
    path("admin/", admin.site.urls),
    path(
        "member_register/", views.MemberRegisterView.as_view(), name="member_register"
    ),
    path(
        "exhibitor_register/",
        views.ExhibitorRegisterView.as_view(),
        name="exhibitor_register",
    ),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("add_news/", views.AddNewsView.as_view(), name="add_news"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("my_profile/", views.UserDetailView.as_view(), name="my_profile"),
    path(
        "change_password/",
        views.CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
    path(
        "inactive_users/",
        views.InactiveUserListView.as_view(),
        name="inactive_user_list",
    ),
    path(
        "user_details/<int:user_id>/",
        views.UserDetailsView.as_view(),
        name="user_details",
    ),
    # contact
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("message_list/", views.MessageListView.as_view(), name="message_list"),
    path(
        "message/<int:message_id>/",
        views.ReplyOrDetailMessageView.as_view(),
        name="reply_or_detail_message",
    ),
    # exhibitors pigs
    path("exhibitor/add_pig/", views.exhibitor_add_pig, name="exhibitor_add_pig"),
    path(
        "exhibitor/my_pigs/",
        views.ExhibitorMyPigsView.as_view(),
        name="exhibitor_my_pigs",
    ),
    path(
        "exhibitor_pig_detail/<int:pig_id>/",
        views.ExhibitorPigDetailView.as_view(),
        name="exhibitor_pig_detail",
    ),
    # breeder pigs
    path("breeder/add_pig/", views.breeder_add_pig, name="breeder_add_pig"),
    path("breeder/my_pigs/", views.BreederMyPigsView.as_view(), name="breeder_my_pigs"),
    path(
        "breeder_pig_detail/<int:pk>/",
        views.BreederPigDetailView.as_view(),
        name="breeder_pig_detail",
    ),
    path(
        "breeder_pig_pedigree/<int:pk>/",
        views.BreederPigPedigreeView.as_view(),
        name="breeder_pig_pedigree",
    ),
    path(
        "breeder_pig_update/<int:pk>/",
        views.BreederPigUpdateView.as_view(),
        name="breeder_pig_update",
    ),
    path("get_parent_pig_info/", views.get_parent_pig_info, name="get_parent_pig_info"),
    path("get_pig_info/", views.get_pig_info, name="get_pig_info"),
    path("waiting_pig_list/", views.display_waiting_pigs, name="waiting_pig_list"),
    path(
        "waiting_pig_list_details/<int:pig_id>/",
        views.display_waiting_pig_details,
        name="waiting_pig_list_details",
    ),
    path(
        "delete_waiting_pig/",
        views.delete_waiting_pig.as_view(),
        name="delete_waiting_pig",
    ),
    path(
        "management/",
        TemplateView.as_view(template_name="management.html"),
        name="management",
    ),
    path(
        "judging_committee/",
        TemplateView.as_view(template_name="judging_committee.html"),
        name="judging_committee",
    ),
    path("add_breeding/", views.AddBreedingView.as_view(), name="add_breeding"),
    path(
        "breeding_details/", views.BreedingDetailView.as_view(), name="breeding_details"
    ),
    path(
        "inactive_breeding_list/",
        views.InactiveBreedingListView.as_view(),
        name="inactive_breeding_list",
    ),
    path(
        "inactive_breeding_details/<int:breeding_id>/",
        views.InactiveBreedingDetailsView.as_view(),
        name="breeding_details",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
