from django import forms
from .models import News, User, Message, Pig, Breed
from datetime import date
from django.contrib.auth.forms import UserCreationForm
import datetime
from django.contrib.auth import get_user_model
import re


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'photo']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title', 'first_name', 'email', 'content']


class RegistrationAsForm(forms.Form):
    registration_type = forms.ChoiceField(
        choices=[
            ('member', 'Hodowca lub Miłośnik'),
            ('exhibitor', 'Wystawca')
        ],
        label="Wybierz rodzaj rejestracji",
    )


class CustomUserCreationForm(UserCreationForm):
    cur_year = datetime.datetime.today().year
    year_range = tuple([i for i in range(cur_year - 90, cur_year - 10)])
    ROLE_CHOICES = [
        ('MI', 'Miłośnik'),
        ('HP', 'Hodowca Polski'),
        ('HZ', 'Hodowca Zagraniczny')
    ]

    birthdate = forms.DateField(label="Data urodzenia", widget=forms.SelectDateWidget(years=year_range))
    phone_number = forms.CharField(max_length=15, label="Numer telefonu")
    town = forms.CharField(max_length=100, label="Miejscowość")
    postal_code = forms.CharField(max_length=10, label="Kod pocztowy")
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Członek")
    questionnaire = forms.CharField(widget=forms.Textarea, label="Ankieta", required=True)
    country = forms.ChoiceField(choices=User.COUNTRY_CHOICES, label="Państwo")
    first_name = forms.CharField(max_length=30, required=True, label="Imię")
    last_name = forms.CharField(max_length=30, required=True, label="Nazwisko")
    email = forms.EmailField(required=True, label="Adres email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.generate_username(self.cleaned_data.get('first_name'), self.cleaned_data.get('last_name'))
        user.is_active = False
        user.club = 'PL'

        if not user.last_edit_date:
            user.last_edit_date = user.date_joined
        if commit:
            user.save()
        return user

    @staticmethod
    def generate_username(first_name, last_name):
        first_name = first_name.lower()
        last_name = last_name.lower()

        if ' ' in first_name:
            first_name = '_'.join(first_name.split())
        if ' ' in last_name:
            last_name = '_'.join(last_name.split())

        username = f"{first_name}.{last_name}"
        num = 1

        while User.objects.filter(username=username).exists():
            username = f"{first_name}.{last_name}{num}"
            num += 1

        return username

    class Meta:
        model = get_user_model()
        fields = [f for f in UserCreationForm.Meta.fields if f != 'username'] + [
            'role', 'first_name', 'last_name',
            'email', 'birthdate', 'phone_number',
            'country', 'town', 'postal_code', 'questionnaire']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            user_exists = get_user_model().objects.filter(email=email).exists()
            if user_exists:
                raise forms.ValidationError("Użytkownik z tym adresem e-mail już istnieje.")
        return email

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get('birthdate')

        if birthdate:
            age = (date.today() - birthdate).days // 365
            if age < 15 or age > 100:
                raise forms.ValidationError("Wiek użytkownika powinien być między 15 a 100 lat.")
        return birthdate

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        role = self.cleaned_data.get('role')

        if not re.match(r'^[\d+ ()-]*$', phone_number):
            raise forms.ValidationError("Nieprawidłowy numer telefonu. Wprowadź go w odpowiednim formacie.")

        if role == 'MI' or role == 'HP':
            if not re.match(r'^\d{9}$', phone_number):
                raise forms.ValidationError("Numer telefonu musi składać się z 9 cyfr.")
        elif role == 'HZ':
            if not re.match(r'^+\d{1,4} \d{6,12}$', phone_number):
                raise forms.ValidationError("Numer telefonu musi mieć format numeru kierunkowego "
                                            "oddzielonego spacją i numeru, np. '+1234 123456789'.")
        return phone_number

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise forms.ValidationError("Imię może zawierać tylko litery.")
        if not first_name.istitle():
            raise forms.ValidationError("Imię musi zaczynać się z wielkiej litery.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise forms.ValidationError("Nazwisko może zawierać tylko litery.")
        if not last_name.istitle():
            raise forms.ValidationError("Nazwisko musi zaczynać się z wielkiej litery.")
        return last_name

    def clean_town(self):
        town = self.cleaned_data.get('town')
        words = town.split()
        if not all(word.isalpha() or word.replace(" ", "").isalpha() for word in town.split()):
            raise forms.ValidationError("Wpisz poprawną nazwę miejscowości.")
        for word in words:
            if not word[0].isupper():
                raise forms.ValidationError("Wszystkie słowa w miejscowości powinny zaczynać się od wielkiej litery.")
        return town

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        role = self.cleaned_data.get('role')
        if not re.match(r'^[a-zA-Z\d -]*$', postal_code):
            raise forms.ValidationError("Nieprawidłowy kod pocztowy. Wprowadź go w odpowiednim formacie.")
        if role == 'MI' or role == 'HP':
            if not re.match(r'^\d{2}-\d{3}$', postal_code):
                raise forms.ValidationError("Kod pocztowy powinien być w formacie 12-345")
        return postal_code


class ExhibitorCreationForm(UserCreationForm):
    cur_year = datetime.datetime.today().year
    year_range = tuple([i for i in range(cur_year - 90, cur_year - 10)])
    EX_CHOICES = [
        ('WZ', 'Wystawca Zagraniczny'),
        ('WD', 'Wystawca standardu D')
    ]
    birthdate = forms.DateField(label="Data urodzenia", widget=forms.SelectDateWidget(years=year_range), required=False)
    phone_number = forms.CharField(max_length=15, label="Numer telefonu", required=False)
    town = forms.CharField(max_length=100, label="Miejscowość", required=False)
    postal_code = forms.CharField(max_length=10, label="Kod pocztowy", required=False)
    role = forms.ChoiceField(choices=EX_CHOICES, label="Członek")
    club = forms.ChoiceField(choices=User.CLUB_CHOICES, label="Klub")
    country = forms.ChoiceField(choices=User.COUNTRY_CHOICES, label="Państwo")
    first_name = forms.CharField(max_length=30, required=True, label="Imię")
    last_name = forms.CharField(max_length=30, required=True, label="Nazwisko")
    email = forms.EmailField(required=True, label="Adres email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.generate_username(self.cleaned_data.get('first_name'), self.cleaned_data.get('last_name'))
        user.is_active = False

        if not user.last_edit_date:
            user.last_edit_date = user.date_joined
        if commit:
            user.save()
        return user

    @staticmethod
    def generate_username(first_name, last_name):
        first_name = first_name.lower()
        last_name = last_name.lower()

        if ' ' in first_name:
            first_name = '_'.join(first_name.split())
        if ' ' in last_name:
            last_name = '_'.join(last_name.split())

        username = f"{first_name}.{last_name}"
        num = 1

        while User.objects.filter(username=username).exists():
            username = f"{first_name}.{last_name}{num}"
            num += 1

        return username

    class Meta:
        model = get_user_model()
        fields = [f for f in UserCreationForm.Meta.fields if f != 'username'] + [
            'role', 'club', 'first_name', 'last_name',
            'email', 'birthdate', 'phone_number',
            'country', 'town', 'postal_code']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            user_exists = get_user_model().objects.filter(email=email).exists()
            if user_exists:
                raise forms.ValidationError("Użytkownik z tym adresem e-mail już istnieje.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise forms.ValidationError("Imię może zawierać tylko litery.")
        if not first_name.istitle():
            raise forms.ValidationError("Imię musi zaczynać się z wielkiej litery.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise forms.ValidationError("Nazwisko może zawierać tylko litery.")
        if not last_name.istitle():
            raise forms.ValidationError("Nazwisko musi zaczynać się z wielkiej litery.")
        return last_name


class ConfirmDeleteUserForm(forms.Form):
    reason_for_deletion = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), label='Powód usunięcia')


class ReplyForm(forms.Form):
    title = forms.CharField(max_length=255, required=True)
    content = forms.CharField(widget=forms.Textarea, required=True)


class PigForm(forms.ModelForm):
    cur_year = datetime.datetime.today().year
    year_range = tuple([i for i in range(cur_year - 10, cur_year+1)])

    name = forms.CharField(max_length=150, label="Imię", required=True)
    sex = forms.ChoiceField(choices=Pig.SEX_CHOICE, label="Płeć", required=True)
    birth_date = forms.DateField(label="Data urodzenia", widget=forms.SelectDateWidget(years=year_range), required=False)
    colors = forms.CharField(max_length=200, label="Umaszczenie", required=True)
    owner = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Pig
        fields = ['name', 'sex', 'birth_date', 'colors']

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        pig = super().save(commit=False)
        pig.breed = Breed.objects.get(name="Pupil - świnka bez rodowodu")
        pig.is_active = True
        pig.owner = User.objects.get(id=self.owner)
        if commit:
            pig.save()
        return pig