from django.shortcuts import render
from django.urls import path
from . import views
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views


def add_pig_breeder(request):
    return render(request, 'add_pig_breeder.html')


urlpatterns = [
    path('', views.main, name='Main'),
    path('admin/', admin.site.urls),
    path('member_register/', views.member_register, name='member_register'),
    path('exhibitor_register/', views.exhibitor_register, name='exhibitor_register'),
    path('register/', views.register, name='register'),
    path('add_news/', views.add_news, name='add_news'),

    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('inactive_users/', views.InactiveUserListView.as_view(), name='inactive_user_list'),
    path('user_details/<int:user_id>/', views.UserDetailsView.as_view(), name='user_details'),
    path('confirm_delete_user/<int:user_id>/', views.ConfirmDeleteUserView.as_view(), name='confirm_delete_user'),
    # contact
    path('contact/', views.contact, name='contact'),
    path('message_list/', views.message_list, name='message_list'),
    path('message/<int:message_id>/', views.reply_or_detail_message, name='reply_or_detail_message'),
    # exhibitors pigs
    path('exhibitor/add_pig/', views.exhibitor_add_pig, name='exhibitor_add_pig'),
    path('exhibitor/my_pigs/', views.exhibitor_my_pigs, name='exhibitor_my_pigs'),
    path('exhibitor_pig_detail/<int:pig_id>/', views.exhibitor_pig_detail, name='exhibitor_pig_detail'),
    # breeder pigs
    path('breeder/add_pig/', views.breeder_add_pig, name='breeder_add_pig'),
    path('get_parent_pig_info/', views.get_parent_pig_info, name='get_parent_pig_info'),
    path('get_pig_info/', views.get_pig_info, name='get_pig_info'),
    path('waiting_pig_list/', views.display_waiting_pigs, name='waiting_pig_list'),
    path('waiting_pig_list_details/<int:pig_id>/', views.display_waiting_pig_details, name='waiting_pig_list_details'),
    path('delete_waiting_pig/', views.delete_waiting_pig.as_view(), name='delete_waiting_pig'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
