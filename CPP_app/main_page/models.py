import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


class News(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    photo = models.ImageField(upload_to='news/', blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}{self.creation_date.day}-{self.creation_date.month}-{self.creation_date.year}"


class User(AbstractUser):
    ROLE_CHOICES = [
        ('MI', 'Miłośnik'),
        ('HP', 'Hodowca Polski'),
        ('HZ', 'Hodowca Zagraniczny'),
        ('WZ', 'Wystawca Zagraniczny'),
        ('WD', 'Wystawca standardu D')
    ]
    CLUB_CHOICES = [
        ('PL', 'Polska (CCP)'),
        ('PET', 'Wystawca standardu D - Brak klubu'),
        ('SOCHM', 'Czech Republic (SOCHM)'),
        ('SZOCHVM', 'Czech Republic (SZOCHVM)'),
        ('SK', 'Slovakia'),
        ('UA', 'Ukraine'),
        ('SE', 'Sweden'),
        ('DMK', 'Denmark (DMK)'),
        ('DMF', 'Denmark (DMF)'),
        ('FI', 'Finland'),
        ('NMK', 'Norway (NMK)'),
        ('NMF', 'Norway (NMF)'),
        ('GB', 'Great Britain'),
        ('MFD', 'Germany (MFD)'),
        ('OMNC', 'Germany (OMNC)'),
        ('NL', 'Netherlands'),
        ('FAEC', 'France (FAEC)'),
        ('CCF', 'France (CCF)'),
        ('CH', 'Switzerland'),
        ('BE', 'Belgium'),
        ('AT', 'Austria'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('PT', 'Portugal'),
        ('IE', 'Ireland'),
        ('SI', 'Slovenia'),
        ('HU', 'Hungary'),
        ('USA', 'USA'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('NZ', 'New Zealand'),
    ]
    COUNTRY_CHOICES = [
        ('PL', 'Polska'),
        ('CZ', 'Czech Republic'),
        ('SK', 'Slovakia'),
        ('UA', 'Ukraine'),
        ('SE', 'Sweden'),
        ('DK', 'Denmark'),
        ('FI', 'Finland'),
        ('NO', 'Norway'),
        ('GB', 'Great Britain'),
        ('DE', 'Germany'),
        ('NL', 'Netherlands'),
        ('FR', 'France'),
        ('CH', 'Switzerland'),
        ('BE', 'Belgium'),
        ('AT', 'Austria'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('PT', 'Portugal'),
        ('IE', 'Ireland'),
        ('SI', 'Slovenia'),
        ('HU', 'Hungary'),
        ('USA', 'USA'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('NZ', 'New Zealand'),
    ]
    birthdate = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length=20, choices=COUNTRY_CHOICES, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    registration_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=False)
    club = models.CharField(max_length=10, choices=CLUB_CHOICES, blank=True)
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


class Color(models.Model):
    name = models.CharField(max_length=150, unique=True, blank=False, null=False)
    position = models.CharField(max_length=1, blank=False, null=False)

    def __str__(self):
        return self.name + ' ' + self.position


class EyeColor(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False, null=False)
    polish_name = models.CharField(max_length=150, unique=False, blank=False, null=False)

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
    POSITION_CHOICES = [
        ('Before', 'Before'),
        ('After', 'After'),
    ]
    name = models.CharField(max_length=150, null=False, blank=False)
    nickname = models.CharField(max_length=150, null=False, blank=True)
    sex = models.CharField(max_length=6, choices=SEX_CHOICE, default='Samiec', blank=False, null=False)
    birth_date = models.DateField(blank=True, null=True)
    birth_weight = models.PositiveIntegerField(null=True, blank=True)
    owner = models.ForeignKey('Breeding', null=True, blank=True, on_delete=models.SET_NULL,
                              default=None, related_name="PIG_owner")
    breed = models.ForeignKey('Breed', on_delete=models.PROTECT)
    breeder = models.CharField(max_length=255, null=True, blank=True)
    father = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                               default=None, related_name='PIG_father', limit_choices_to={'sex': 'Male'})
    mother = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                               default=None, related_name='PIG_mother', limit_choices_to={'sex': 'Female'})
    colors = models.CharField(max_length=200, null=True, blank=True)
    eye_color = models.ForeignKey('EyeColor', null=True, blank=True, on_delete=models.PROTECT)
    registration_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    litter = models.ForeignKey('Litter', null=True, blank=True, on_delete=models.PROTECT,
                               default=None, related_name='PIG_litter')
    photo = models.ImageField(upload_to='zdjecia_swinek/zdjecia_uzytkownikow', null=True, blank=True)
    nickname_position = models.CharField(max_length=6, choices=POSITION_CHOICES, default='After', blank=True, null=True)
    is_in_breeding = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " " + self.nickname


class Litter(models.Model):
    breeding = models.ForeignKey('Breeding', related_name='LITTER_breeding', on_delete=models.PROTECT)
    birthdate = models.DateField(null=True, blank=True)
    mother = models.ForeignKey('Pig', null=True, blank=True, related_name='LITTER_mother', on_delete=models.PROTECT)
    father = models.ForeignKey('Pig', null=True, blank=True, related_name='LITTER_father', on_delete=models.PROTECT)
    number_of_male = models.PositiveIntegerField(null=True, blank=True)
    number_of_female = models.PositiveIntegerField(null=True, blank=True)


class Message(models.Model):
    title = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.title
