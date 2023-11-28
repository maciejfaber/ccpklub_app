from django.urls import path
from . import views
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('', views.main, name='Main'),
    path('admin/', admin.site.urls),
    path('member_register/', views.register, name='register'),
    path('exhibitor_register/', views.exhibitor_register, name='exhibitor_register'),
    path('register_as/', views.register_as, name='register_as'),
    path('add_news/', views.add_news, name='add_news'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('inactive_users/', views.InactiveUserListView.as_view(), name='inactive_user_list'),
    path('user_details/<int:user_id>/', views.UserDetailsView.as_view(), name='user_details'),
    path('confirm_delete_user/<int:user_id>/', views.ConfirmDeleteUserView.as_view(), name='confirm_delete_user'),
    path('message_list/', views.message_list, name='message_list'),
    path('message/<int:message_id>/', views.reply_or_detail_message, name='reply_or_detail_message'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
