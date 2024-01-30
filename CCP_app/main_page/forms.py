from django import forms
from .models import News, User, Message, Pig, Breed, Color, EyeColor, Breeding
from datetime import date, datetime, timedelta
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import re


class PigColorWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        choices_position_1 = (
            Color.objects.filter(position=1).values_list("name", flat=True).distinct()
        )
        choices_position_2 = (
            Color.objects.filter(position=2).values_list("name", flat=True).distinct()
        )
        choices_position_3 = (
            Color.objects.filter(position=3).values_list("name", flat=True).distinct()
        )
        choices_position_4 = (
            Color.objects.filter(position=4).values_list("name", flat=True).distinct()
        )

        widgets = [
            forms.Select(
                choices=[("", "")] + [(color, color) for color in choices_position_1]
            ),
            forms.Select(choices=[("", ""), ("Sable", "Sable")]),
            forms.Select(
                choices=[("", "")] + [(color, color) for color in choices_position_2]
            ),
            forms.Select(
                choices=[("", "")] + [(color, color) for color in choices_position_3]
            ),
            forms.Select(
                choices=[("", "")] + [(color, color) for color in choices_position_4]
            ),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split("/")
        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = [
            data.get(name + "_0", None),
            data.get(name + "_1", None),
            data.get(name + "_2", None),
            data.get(name + "_3", None),
            data.get(name + "_4", None),
        ]
        for i in range(len(values)):
            if values[i] is None:
                values[i] = ""
        result = f"['{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}', '{values[4]}']"
        return result


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["title", "content", "photo"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["title", "first_name", "email", "content"]


class RegistrationForm(forms.Form):
    registration_type = forms.ChoiceField(
        choices=[("member", "Hodowca lub Miłośnik"), ("exhibitor", "Wystawca")],
        label="Wybierz rodzaj rejestracji",
    )


class CustomUserCreationForm(UserCreationForm):
    cur_year = datetime.today().year
    year_range = tuple([i for i in range(cur_year - 90, cur_year - 10)])
    ROLE_CHOICES = [
        ("MI", "Miłośnik"),
        ("HP", "Hodowca Polski"),
        ("HZ", "Hodowca Zagraniczny"),
    ]

    birthdate = forms.DateField(
        label="Data urodzenia", widget=forms.SelectDateWidget(years=year_range)
    )
    phone_number = forms.CharField(max_length=15, label="Numer telefonu")
    town = forms.CharField(max_length=100, label="Miejscowość")
    postal_code = forms.CharField(max_length=10, label="Kod pocztowy")
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Członek")
    questionnaire = forms.CharField(
        widget=forms.Textarea, label="Ankieta", required=True
    )
    country = forms.ChoiceField(choices=User.COUNTRY_CHOICES, label="Państwo")
    first_name = forms.CharField(max_length=30, required=True, label="Imię")
    last_name = forms.CharField(max_length=30, required=True, label="Nazwisko")
    email = forms.EmailField(required=True, label="Adres email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.generate_username(
            self.cleaned_data.get("first_name"), self.cleaned_data.get("last_name")
        )
        user.is_active = False
        user.club = "PL"

        if not user.last_edit_date:
            user.last_edit_date = user.date_joined
        if commit:
            user.save()
        return user

    @staticmethod
    def generate_username(first_name, last_name):
        first_name = first_name.lower()
        last_name = last_name.lower()

        if " " in first_name:
            first_name = "_".join(first_name.split())
        if " " in last_name:
            last_name = "_".join(last_name.split())

        username = f"{first_name}.{last_name}"
        num = 1

        while User.objects.filter(username=username).exists():
            username = f"{first_name}.{last_name}{num}"
            num += 1

        return username

    class Meta:
        model = get_user_model()
        fields = [f for f in UserCreationForm.Meta.fields if f != "username"] + [
            "role",
            "first_name",
            "last_name",
            "email",
            "birthdate",
            "phone_number",
            "country",
            "town",
            "postal_code",
            "questionnaire",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            user_exists = get_user_model().objects.filter(email=email).exists()
            if user_exists:
                raise forms.ValidationError(
                    "Użytkownik z tym adresem e-mail już istnieje."
                )
        return email

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")

        if birthdate:
            age = (date.today() - birthdate).days // 365
            if age < 15 or age > 100:
                raise forms.ValidationError(
                    "Wiek użytkownika powinien być między 15 a 100 lat."
                )
        return birthdate

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        role = self.cleaned_data.get("role")

        if not re.match(r"^[\d+ ()-]*$", phone_number):
            raise forms.ValidationError(
                "Nieprawidłowy numer telefonu. Wprowadź go w odpowiednim formacie."
            )

        if role == "MI" or role == "HP":
            if not re.match(r"^\d{9}$", phone_number):
                raise forms.ValidationError("Numer telefonu musi składać się z 9 cyfr.")
        elif role == "HZ":
            if not re.match(r"^+\d{1,4} \d{6,12}$", phone_number):
                raise forms.ValidationError(
                    "Numer telefonu musi mieć format numeru kierunkowego "
                    "oddzielonego spacją i numeru, np. '+1234 123456789'."
                )
        return phone_number

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise forms.ValidationError("Imię może zawierać tylko litery.")
        if not first_name.istitle():
            raise forms.ValidationError("Imię musi zaczynać się z wielkiej litery.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name.isalpha():
            raise forms.ValidationError("Nazwisko może zawierać tylko litery.")
        if not last_name.istitle():
            raise forms.ValidationError("Nazwisko musi zaczynać się z wielkiej litery.")
        return last_name

    def clean_town(self):
        town = self.cleaned_data.get("town")
        words = town.split()
        if not all(
            word.isalpha() or word.replace(" ", "").isalpha() for word in town.split()
        ):
            raise forms.ValidationError("Wpisz poprawną nazwę miejscowości.")
        for word in words:
            if not word[0].isupper():
                raise forms.ValidationError(
                    "Wszystkie słowa w miejscowości powinny zaczynać się od wielkiej litery."
                )
        return town

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code")
        role = self.cleaned_data.get("role")
        if not re.match(r"^[a-zA-Z\d -]*$", postal_code):
            raise forms.ValidationError(
                "Nieprawidłowy kod pocztowy. Wprowadź go w odpowiednim formacie."
            )
        if role == "MI" or role == "HP":
            if not re.match(r"^\d{2}-\d{3}$", postal_code):
                raise forms.ValidationError(
                    "Kod pocztowy powinien być w formacie 12-345"
                )
        return postal_code


class ExhibitorCreationForm(UserCreationForm):
    today = datetime.today()
    min_year = (today - timedelta(days=80 * 365)).strftime("%Y-%m-%d")
    max_year = today.strftime("%Y-%m-%d")
    EX_CHOICES = [("WZ", "Wystawca Zagraniczny"), ("WD", "Wystawca standardu D")]
    birthdate = forms.DateField(label="Data urodzenia", required=False)
    phone_number = forms.CharField(
        max_length=15, label="Numer telefonu", required=False
    )
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
        user.username = self.generate_username(
            self.cleaned_data.get("first_name"), self.cleaned_data.get("last_name")
        )
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

        if " " in first_name:
            first_name = "_".join(first_name.split())
        if " " in last_name:
            last_name = "_".join(last_name.split())

        username = f"{first_name}.{last_name}"
        num = 1

        while User.objects.filter(username=username).exists():
            username = f"{first_name}.{last_name}{num}"
            num += 1

        return username

    class Meta:
        model = get_user_model()
        fields = [f for f in UserCreationForm.Meta.fields if f != "username"] + [
            "role",
            "club",
            "first_name",
            "last_name",
            "email",
            "birthdate",
            "phone_number",
            "country",
            "town",
            "postal_code",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            user_exists = get_user_model().objects.filter(email=email).exists()
            if user_exists:
                raise forms.ValidationError(
                    "Użytkownik z tym adresem e-mail już istnieje."
                )
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise forms.ValidationError("Imię może zawierać tylko litery.")
        if not first_name.istitle():
            raise forms.ValidationError("Imię musi zaczynać się z wielkiej litery.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name.isalpha():
            raise forms.ValidationError("Nazwisko może zawierać tylko litery.")
        if not last_name.istitle():
            raise forms.ValidationError("Nazwisko musi zaczynać się z wielkiej litery.")
        return last_name


class UserActionForm(forms.Form):
    ACTION_CHOICES = [
        ("accept", "Akceptuj"),
        ("delete", "Usuń"),
    ]

    action = forms.ChoiceField(choices=ACTION_CHOICES)
    email_content = forms.CharField(widget=forms.Textarea, required=False)


class ReplyForm(forms.Form):
    title = forms.CharField(max_length=255, required=True)
    content = forms.CharField(widget=forms.Textarea, required=True)


class PigWDForm(forms.ModelForm):
    cur_year = datetime.today().year
    year_range = tuple([i for i in range(cur_year - 10, cur_year + 1)])

    name = forms.CharField(max_length=150, label="Imię", required=True)
    sex = forms.ChoiceField(choices=Pig.SEX_CHOICE, label="Płeć", required=True)
    birth_date = forms.DateField(
        label="Data urodzenia",
        widget=forms.SelectDateWidget(years=year_range),
        required=False,
    )
    nickname = forms.CharField(max_length=255, label="Przydomek", required=False)

    class Meta:
        model = Pig
        fields = ["name", "sex", "birth_date", "colors"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = kwargs.pop("owner", None)
        self.fields["colors"] = forms.CharField(
            max_length=255, widget=PigColorWidget, label="Umaszczenie", required=False
        )

    def save(self, commit=True):
        pig = super().save(commit=False)
        pig.breed = Breed.objects.get(name="PET (świnka domowa – pupil)")
        pig.is_active = True
        pig.nickname = self.owner.username
        if commit:
            pig.save()
            pig.owner.set([self.owner])
            pig.save()
        return pig

    def clean(self):
        name = self.cleaned_data.get("name")
        nickname = self.owner.username
        if Pig.objects.filter(name=name, nickname=nickname).exists():
            self.add_error(
                "name", forms.ValidationError("Już posiadasz świnkę o takim imieniu")
            )
        else:
            return self.cleaned_data

    def clean_colors(self):
        cleaned_data = super().clean()
        pig_color_value = cleaned_data.get("colors", None)
        print(pig_color_value)
        if pig_color_value.startswith("['', 'Sable'"):
            raise forms.ValidationError(
                'Aby wybrać "Sable" wybierz kolor z rodziny czerni'
            )
        if pig_color_value == "['', '', '', '', '']":
            raise forms.ValidationError("Wybierz przynajmniej jeden kolor.")

        return pig_color_value


class PigWZForm(forms.ModelForm):
    cur_year = datetime.today().year
    year_range = tuple([i for i in range(cur_year - 10, cur_year + 1)])

    name = forms.CharField(max_length=150, label="Imię", required=True)
    nickname = forms.CharField(max_length=150, label="Przydomek", required=True)
    sex = forms.ChoiceField(choices=Pig.SEX_CHOICE, label="Płeć", required=True)
    birth_date = forms.DateField(
        label="Data urodzenia",
        widget=forms.SelectDateWidget(years=year_range),
        required=True,
    )
    breed = forms.ModelChoiceField(
        queryset=Breed.objects.all(), label="Rasa", required=True
    )
    registration_number = forms.CharField(
        max_length=25, label="Numer rejestracyjny", required=False
    )

    class Meta:
        model = Pig
        fields = [
            "name",
            "nickname",
            "sex",
            "birth_date",
            "owner",
            "colors",
            "breed",
            "registration_number",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = kwargs.pop("owner", None)
        self.fields["colors"] = forms.CharField(
            max_length=255, widget=PigColorWidget, label="Umaszczenie", required=False
        )

    def save(self, commit=True):
        pig = super().save(commit=False)
        pig.is_active = True
        if commit:
            pig.save()
            pig.owner.set([self.owner])
            pig.save()
        return pig

    def clean(self):
        name = self.cleaned_data.get("name")
        nickname = self.cleaned_data.get("nickname")
        if Pig.objects.filter(name=name, nickname=nickname).exists():
            self.add_error(
                "name",
                forms.ValidationError(
                    "Świnka o podanym imieniu i przydomku już istnieje"
                ),
            )
            self.add_error(
                "nickname",
                forms.ValidationError(
                    "Świnka o podanym imieniu i przydomku już istnieje"
                ),
            )
        else:
            return self.cleaned_data

    def clean_colors(self):
        cleaned_data = super().clean()
        pig_color_value = cleaned_data.get("colors", None)
        if pig_color_value.startswith("['', 'Sable'"):
            raise forms.ValidationError(
                'Aby wybrać "Sable" wybierz kolor z rodziny czerni'
            )
        if pig_color_value == "['', '', '', '', '']":
            raise forms.ValidationError("Wybierz przynajmniej jeden kolor.")

        return pig_color_value


class ExistingPigForm(forms.Form):
    existing_pig = forms.ModelChoiceField(
        queryset=Pig.objects.all(), empty_label="--- Wybierz świnkę ---", required=False
    )


class ExhibitorAddParentPigForm(forms.ModelForm):
    name = forms.CharField(max_length=150, label="Imię", required=False)
    nickname = forms.CharField(max_length=150, label="Przydomek", required=False)
    breed = forms.ModelChoiceField(
        queryset=Breed.objects.all(), label="Rasa", required=False
    )

    class Meta:
        model = Pig
        fields = ["name", "nickname", "breed", "colors"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["colors"] = forms.CharField(
            max_length=255, widget=PigColorWidget, label="Umaszczenie", required=False
        )


class ExhibitorAddPigForm(forms.ModelForm):
    cur_year = datetime.today().year
    year_range = tuple([i for i in range(cur_year - 10, cur_year + 1)])

    name = forms.CharField(max_length=150, label="Imię", required=False)
    nickname = forms.CharField(max_length=150, label="Przydomek", required=False)
    sex = forms.ChoiceField(choices=Pig.SEX_CHOICE, label="Płeć", required=False)
    birth_date = forms.DateField(
        label="Data urodzenia",
        widget=forms.SelectDateWidget(years=year_range),
        required=False,
    )
    breed = forms.ModelChoiceField(
        queryset=Breed.objects.all(), label="Rasa", required=False
    )
    eye_color = forms.ModelChoiceField(
        queryset=EyeColor.objects.all(), label="Kolor oczu", required=False
    )
    owner = forms.CharField(max_length=255, label="Właściciel", required=False)
    breeder = forms.CharField(max_length=255, label="Hodowca", required=False)

    class Meta:
        model = Pig
        fields = [
            "name",
            "nickname",
            "sex",
            "colors",
            "birth_date",
            "birth_weight",
            "breed",
            "eye_color",
            "owner",
            "breeder",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["colors"] = forms.CharField(
            max_length=255, widget=PigColorWidget, label="Umaszczenie", required=False
        )

    def clean_colors(self):
        pig_color_value = self.cleaned_data.get("colors")
        if pig_color_value.startswith("Sable"):
            raise forms.ValidationError(
                'Aby wybrać "Sable" wybierz kolor z rodziny czerni'
            )
        if pig_color_value == "":
            raise forms.ValidationError("Wybierz przynajmniej jeden kolor.")
        # Dodać wyjątki kolorów dla ras !!
        return pig_color_value

    def clean_birth_weight(self):
        birth_weight = self.cleaned_data.get("birth_weight")
        if birth_weight is not None:
            if birth_weight < 30:
                raise forms.ValidationError("Waga jest za mała.")
        return birth_weight

    def clean_name(self):
        allowed_characters = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'-_"
        )
        name = self.cleaned_data.get("name")

        if not all(char in allowed_characters for char in name):
            raise forms.ValidationError("Imię zawiera niedozwolone znaki.")
        return name

    def clean_nickname(self):
        allowed_characters = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'-_ "
        )
        nickname = self.cleaned_data.get("nickname")
        if not all(char in allowed_characters for char in nickname):
            raise forms.ValidationError("Przydomek zawiera niedozwolone znaki.")
        return nickname

    def clean_breed(self):
        return self.cleaned_data.get("breed")

    def clean_owner(self):
        breeding_name = self.cleaned_data.get("owner")

        if breeding_name:
            try:
                breeding = Breeding.objects.get(name=breeding_name)
            except Breeding.DoesNotExist:
                raise forms.ValidationError("Nie znaleziono hodowli o podanej nazwie.")
            return breeding.name
        else:
            return None


class BreedingForm(forms.ModelForm):
    name = forms.CharField(max_length=150, label="name", required=True)
    nickname = forms.CharField(max_length=150, label="nickname", required=True)
    owners = forms.ModelChoiceField(
        queryset=User.objects.all(), required=True, label="owners"
    )
    breeds = forms.ModelMultipleChoiceField(
        queryset=Breed.objects.all(), required=True, label="breeds"
    )
    purpose = forms.CharField(widget=forms.Textarea, required=True)

    def save(self, commit=True):
        Breeding = super().save(commit=False)
        if commit:
            Breeding.save()
            Breeding.owners.add(self.data["owners"])
            Breeding.owners.add(self.request.user)
            Breeding.breeds.add(*self.clean_breeds())
            Breeding.contact_breeder.add(self.request.user)
        return Breeding

    class Meta:
        model = Breeding
        fields = ["name", "nickname", "owners", "breeds", "name_position", "purpose"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(BreedingForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Breeding.objects.filter(name=name).exists():
            raise forms.ValidationError("Hodowla o tej nazwie już istnieje.")
        return name

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if Breeding.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError("Hodowla z takim przydomkiem już istnieje.")
        return nickname

    def clean_breeds(self):
        breeds_ids = self.cleaned_data.get("breeds", [])
        selected_breeds = Breed.objects.filter(id__in=breeds_ids)
        return selected_breeds
