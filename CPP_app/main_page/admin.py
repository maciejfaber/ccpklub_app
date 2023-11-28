from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import News, User, Message, Breeding, Breed, Pig, Litter


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'creation_date')
    list_filter = ('creation_date',)
    search_fields = ('title', 'content')
    date_hierarchy = 'creation_date'
    list_max_show_all = 4
    list_display_links = ('title',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email',
                                      'registration_number', 'birthdate',
                                      'phone_number', 'town', 'postal_code',
                                      'country', 'role', 'club', 'questionnaire')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_edit_date')}),
    )


admin.site.register(News, NewsAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Message)
admin.site.register(Breeding)
admin.site.register(Breed)
admin.site.register(Pig)
admin.site.register(Litter)
