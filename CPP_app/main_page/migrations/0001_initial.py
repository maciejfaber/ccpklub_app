# Generated by Django 3.2.23 on 2023-11-21 17:09

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('birthdate', models.DateField(null=True)),
                ('phone_number', models.CharField(max_length=15, null=True)),
                ('town', models.CharField(max_length=100, null=True)),
                ('postal_code', models.CharField(max_length=10, null=True)),
                ('registration_number', models.CharField(blank=True, max_length=20, null=True)),
                ('role', models.CharField(choices=[('MI', 'Miłośnik'), ('HP', 'Hodowca Polski'), ('HZ', 'Hodowca Zagraniczny')], max_length=20)),
                ('questionnaire', models.TextField(default='')),
                ('last_edit_date', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Breed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('polish_name', models.CharField(max_length=150, unique=True)),
                ('standard', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=2)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Breeding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('name_position', models.CharField(choices=[('before', 'Before'), ('after', 'After')], default='after', max_length=10)),
                ('purpose', models.TextField()),
                ('www', models.CharField(blank=True, max_length=200, null=True)),
                ('fb', models.CharField(blank=True, max_length=200, null=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='news/')),
                ('date_of_join', models.DateField(auto_now_add=True)),
                ('date_of_acceptance', models.DateField(blank=True, null=True)),
                ('registration_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('status', models.CharField(choices=[('waiting', 'Oczekująca'), ('active', 'Aktywna'), ('inactive', 'Nieaktywna'), ('kicked', 'Usunięta dyscyplinarnie')], default='waiting', max_length=10)),
                ('is_active', models.BooleanField(default=False)),
                ('breeds', models.ManyToManyField(related_name='BREEDING_breeds', to='main_page.Breed')),
                ('contact_breeder', models.ManyToManyField(related_name='BREEDING_contact_breeder', to=settings.AUTH_USER_MODEL)),
                ('owners', models.ManyToManyField(related_name='BREEDING_owners', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Litter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('number_of_male', models.PositiveIntegerField(blank=True, null=True)),
                ('number_of_female', models.PositiveIntegerField(blank=True, null=True)),
                ('breeding', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='LITTER_breeding', to='main_page.breeding')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('reply_sent', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('content', models.TextField()),
                ('photo', models.ImageField(blank=True, null=True, upload_to='news/')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('nickname', models.CharField(max_length=150)),
                ('sex', models.CharField(choices=[('Male', 'Samiec'), ('Female', 'Samica')], default='Samiec', max_length=6)),
                ('birth_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('birth_weight', models.IntegerField(blank=True, null=True)),
                ('owner', models.CharField(blank=True, max_length=200, null=True)),
                ('colors', models.CharField(max_length=200)),
                ('eye_color', models.CharField(blank=True, max_length=50, null=True)),
                ('registration_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='zdjecia_swinek/zdjecia_uzytkownikow')),
                ('is_in_breeding', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=False)),
                ('breed', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main_page.breed')),
                ('father', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='PIG_father', to='main_page.pig')),
                ('litter', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='PIG_litter', to='main_page.litter')),
                ('mother', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='PIG_mother', to='main_page.pig')),
            ],
        ),
        migrations.AddField(
            model_name='litter',
            name='father',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='LITTER_father', to='main_page.pig'),
        ),
        migrations.AddField(
            model_name='litter',
            name='mother',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='LITTER_mother', to='main_page.pig'),
        ),
    ]
