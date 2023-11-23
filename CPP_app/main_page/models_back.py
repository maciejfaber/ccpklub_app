import datetime
import re
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import pre_save


class News(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    photo = models.ImageField(upload_to='news/', blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MyModel #{self.content}"


class User(AbstractUser):
    ROLE_CHOICES = [
        ('MI', 'Miłośnik'),
        ('HP', 'Hodowca Polski'),
        ('HZ', 'Hodowca Zagraniczny'),
    ]
    birthdate = models.DateField(null=True, blank=False)
    phone_number = models.CharField(max_length=15, null=True, blank=False)
    town = models.CharField(max_length=100, null=True, blank=False)
    postal_code = models.CharField(max_length=10, null=True, blank=False)
    registration_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=False)
    questionnaire = models.TextField(default="")
    last_edit_date = models.DateTimeField(null=True, blank=True)


def generate_registration_number():
    year = datetime.datetime.now().year
    number = 1
    while Pig.objects.filter(register_number=f"CCP/{year}/{number:03d}").exists():
        number += 1
    return f"CCP/{year}/{number:03d}"


class Breed(models.Model):
    STANDARD_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    ]
    name = models.CharField(max_length=150, unique=True, blank=False, null=False)
    polish_name = models.CharField(max_length=150, unique=True, blank=False, null=False)
    standard = models.CharField(max_length=2, choices=STANDARD_CHOICES, blank=False, null=False)
    description = models.TextField()

    def __str__(self):
        return self.name


class Breeding(models.Model):
    POSITION_CHOICES = [
        ('before', 'Before'),
        ('after', 'After'),
    ]
    STATUS_CHOICES = [
        ('waiting', 'Oczekująca'),
        ('active', 'Aktywna'),
        ('inactive', 'Nieaktywna'),
        ('kicked', 'Usunięta dyscyplinarnie'),
    ]
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    owners = models.ManyToManyField(User, blank=False, related_name='BREEDING_owners')
    breeds = models.ManyToManyField(Breed, blank=False, related_name='BREEDING_breeds')
    contact_breeder = models.ManyToManyField(User, blank=False, related_name='BREEDING_contact_breeder')
    name_position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='after')
    purpose = models.TextField()
    www = models.CharField(max_length=200, null=True, blank=True)
    fb = models.CharField(max_length=200, null=True, blank=True)
    banner = models.ImageField(upload_to='news/', blank=True, null=True)
    date_of_join = models.DateField(auto_now_add=True)
    date_of_acceptance = models.DateField(null=True, blank=True)
    registration_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.registration_number}"


class Pig(models.Model):
    SEX_CHOICE = [
        ('Male', 'Samiec'),
        ('Female', 'Samica')
    ]

    name = models.CharField(max_length=150, null=False, blank=False)
    nickname = models.CharField(max_length=150, null=False, blank=False)
    sex = models.CharField(max_length=6, choices=SEX_CHOICE, default='Samiec', blank=False, null=False)
    birth_date = models.DateField(default=timezone.now, blank=True, null=True)
    birth_weight = models.IntegerField(null=True, blank=True)
    owner = models.CharField(max_length=200, null=True, blank=True)
    breed = models.ForeignKey('Breed', on_delete=models.PROTECT)
    father_name = models.CharField(max_length=150, null=True, blank=True)
    father_nickname = models.CharField(max_length=150, null=True, blank=True)
    mother_name = models.CharField(max_length=150, null=True, blank=True)
    mother_nickname = models.CharField(max_length=150, null=True, blank=True)
    colors = models.CharField(max_length=200, null=False, blank=False)
    eye_color = models.CharField(max_length=50, null=True, blank=True)
    registration_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    litter = models.ForeignKey('Litter', null=True, blank=True, on_delete=models.PROTECT, related_name='PIG_litter')
    photo = models.ImageField(upload_to='zdjecia_swinek/zdjecia_uzytkownikow', null=True, blank=True)
    is_in_breeding = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " " + self.nickname


class Litter(models.Model):
    breeding = models.ManyToManyField(Breeding, related_name='LITTER_breeding')
    birthdate = models.DateField(null=False, blank=False)
    mother = models.ForeignKey('Pig', related_name='LITTER_mother', on_delete=models.PROTECT)
    father = models.ForeignKey('Pig', related_name='LITTER_father', on_delete=models.PROTECT)


class Message(models.Model):
    title = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.title



