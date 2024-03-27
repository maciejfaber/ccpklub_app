import ast
import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


class News(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    photo = models.ImageField(upload_to="staticfiles/img/news", blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}{self.creation_date.day}-{self.creation_date.month}-{self.creation_date.year}"


class User(AbstractUser):
    ROLE_CHOICES = [
        ("MI", "Miłośnik"),
        ("HP", "Hodowca Polski"),
        ("HZ", "Hodowca Zagraniczny"),
        ("WZ", "Wystawca Zagraniczny"),
        ("WD", "Wystawca standardu D"),
    ]
    CLUB_CHOICES = [
        ("PL", "Polska (CCP)"),
        ("PET", "Wystawca standardu D - Brak klubu"),
        ("SOCHM", "Czech Republic (SOCHM)"),
        ("SZOCHVM", "Czech Republic (SZOCHVM)"),
        ("SK", "Slovakia"),
        ("UA", "Ukraine"),
        ("SE", "Sweden"),
        ("DMK", "Denmark (DMK)"),
        ("DMF", "Denmark (DMF)"),
        ("FI", "Finland"),
        ("NMK", "Norway (NMK)"),
        ("NMF", "Norway (NMF)"),
        ("GB", "Great Britain"),
        ("MFD", "Germany (MFD)"),
        ("OMNC", "Germany (OMNC)"),
        ("NL", "Netherlands"),
        ("FAEC", "France (FAEC)"),
        ("CCF", "France (CCF)"),
        ("CH", "Switzerland"),
        ("BE", "Belgium"),
        ("AT", "Austria"),
        ("IT", "Italy"),
        ("ES", "Spain"),
        ("PT", "Portugal"),
        ("IE", "Ireland"),
        ("SI", "Slovenia"),
        ("HU", "Hungary"),
        ("USA", "USA"),
        ("CA", "Canada"),
        ("AU", "Australia"),
        ("NZ", "New Zealand"),
    ]
    COUNTRY_CHOICES = [
        ("PL", "Polska"),
        ("CZ", "Czech Republic"),
        ("SK", "Slovakia"),
        ("UA", "Ukraine"),
        ("SE", "Sweden"),
        ("DK", "Denmark"),
        ("FI", "Finland"),
        ("NO", "Norway"),
        ("GB", "Great Britain"),
        ("DE", "Germany"),
        ("NL", "Netherlands"),
        ("FR", "France"),
        ("CH", "Switzerland"),
        ("BE", "Belgium"),
        ("AT", "Austria"),
        ("IT", "Italy"),
        ("ES", "Spain"),
        ("PT", "Portugal"),
        ("IE", "Ireland"),
        ("SI", "Slovenia"),
        ("HU", "Hungary"),
        ("USA", "USA"),
        ("CA", "Canada"),
        ("AU", "Australia"),
        ("NZ", "New Zealand"),
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
    STANDARD_CHOICES = [("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    name = models.CharField(max_length=150, unique=True, blank=False, null=False)
    polish_name = models.CharField(max_length=150, unique=True, blank=False, null=False)
    standard = models.CharField(
        max_length=2, choices=STANDARD_CHOICES, blank=False, null=False
    )
    description = models.TextField()

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=150, unique=True, blank=False, null=False)
    position = models.CharField(max_length=1, blank=False, null=False)

    def __str__(self):
        return self.name + " " + self.position


class EyeColor(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False, null=False)
    polish_name = models.CharField(
        max_length=150, unique=False, blank=False, null=False
    )
    short = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.name


class Breeding(models.Model):
    POSITION_CHOICES = [
        ("before", "Before"),
        ("after", "After"),
    ]
    STATUS_CHOICES = [
        ("waiting", "Oczekująca"),
        ("active", "Aktywna"),
        ("inactive", "Nieaktywna"),
        ("kicked", "Usunięta dyscyplinarnie"),
    ]
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    nickname = models.CharField(max_length=100, null=False, blank=False, unique=True)
    owners = models.ManyToManyField("User", blank=True, related_name="BREEDING_owners")
    breeds = models.ManyToManyField(
        "Breed", blank=False, related_name="BREEDING_breeds"
    )
    contact_breeder = models.ManyToManyField(
        "User", blank=False, related_name="BREEDING_contact_breeder"
    )
    name_position = models.CharField(
        max_length=10, choices=POSITION_CHOICES, default="after"
    )
    purpose = models.TextField()
    www = models.CharField(max_length=200, null=True, blank=True)
    fb = models.CharField(max_length=200, null=True, blank=True)
    banner = models.ImageField(upload_to="news/", blank=True, null=True)
    date_of_join = models.DateField(auto_now_add=True)
    date_of_acceptance = models.DateField(null=True, blank=True)
    registration_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="waiting")
    is_active = models.BooleanField(default=False)

    def __str__(self):
        if self.registration_number is None:
            return f"{self.name} - Oczekująca"
        else:
            return f"{self.name} - {self.registration_number}"


class Pig(models.Model):
    SEX_CHOICE = [("Male", "Samiec"), ("Female", "Samica")]
    POSITION_CHOICES = [
        ("Before", "Before"),
        ("After", "After"),
    ]
    name = models.CharField(max_length=150, null=False, blank=False)
    nickname = models.CharField(max_length=150, null=False, blank=True)
    sex = models.CharField(
        max_length=6, choices=SEX_CHOICE, default="Samiec", blank=False, null=False
    )
    birth_date = models.DateField(blank=True, null=True)
    birth_weight = models.PositiveIntegerField(null=True, blank=True)
    owner = models.ManyToManyField(
        "User", blank=True, default=None, related_name="PIG_owner"
    )
    breed = models.ForeignKey("Breed", on_delete=models.PROTECT)
    breeder = models.CharField(max_length=255, null=True, blank=True)
    father = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        default=None,
        related_name="PIG_father",
        limit_choices_to={"sex": "Male"},
    )
    mother = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        default=None,
        related_name="PIG_mother",
        limit_choices_to={"sex": "Female"},
    )
    colors = models.CharField(max_length=200, null=True, blank=True)
    eye_color = models.ForeignKey(
        "EyeColor", null=True, blank=True, on_delete=models.PROTECT
    )
    registration_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True
    )
    litter = models.ForeignKey(
        "Litter",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        default=None,
        related_name="PIG_litter",
    )
    photo = models.ImageField(upload_to="pig_photos", null=True, blank=True)
    nickname_position = models.CharField(
        max_length=6, choices=POSITION_CHOICES, default="After", blank=True, null=True
    )
    is_in_breeding = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    litter_count = models.PositiveIntegerField(default=0)
    for_breeding = models.BooleanField(default=True)
    for_exhibitions = models.BooleanField(default=True)

    def __str__(self):
        return self.name + " " + self.nickname

    def formatted_colors(self):
        if self.colors:
            values = ast.literal_eval(self.colors)
            result = values[0]
            result += f" {values[1]}" if values[1] != "" else ""
            if result == "":
                result += values[2]
            elif values[2] != "":
                result += f"-{values[2]}"
            if result != "" and values[3] != "":
                result += f"-{values[3]}"
            else:
                result += values[3]
            if result != "" and values[4] != "":
                result += f"-{values[4]}"
            else:
                result += values[4]
            return result
        else:
            return "Świnka jest niewidzialna"


class Litter(models.Model):
    breeding = models.ForeignKey(
        "Breeding", related_name="LITTER_breeding", on_delete=models.PROTECT
    )
    birthdate = models.DateField(null=True, blank=True)
    mother = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="LITTER_mother",
        on_delete=models.PROTECT,
    )
    father = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="LITTER_father",
        on_delete=models.PROTECT,
    )
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


class Judge(models.Model):
    title = models.CharField(null=True, blank=True, max_length=100)
    first_name = models.CharField(null=False, blank=False, max_length=255)
    last_name = models.CharField(null=False, blank=False, max_length=255)
    country = models.CharField(null=False, blank=False, max_length=5)
    town = models.CharField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    judge_number = models.CharField(null=True, blank=True, max_length=50)
    phone_number = models.CharField(null=True, blank=True, max_length=25)
    email = models.EmailField()
    license = models.CharField(null=True, blank=True, max_length=255)
    judging_in = models.TextField(null=True, blank=True)
    languages = models.TextField(null=True, blank=True)
    standard_a = models.CharField(null=True, blank=True, max_length=5)
    standard_b = models.CharField(null=True, blank=True, max_length=5)
    standard_c = models.CharField(null=True, blank=True, max_length=5)
    standard_d = models.CharField(null=True, blank=True, max_length=5)


class Rating(models.Model):
    RATING_CHOICES = [
        ("", ""),
        ("Dyskwalifikacja", "DSF"),
        ("Dostateczna", "N-B"),
        ("Dobra", "G"),
        ("Bardzo dobra", "SG"),
        ("Doskonała", "HV"),
        ("Wybitna", "V"),
    ]
    CAC_CHOICES = [
        ("", ""),
        ("BCAC", "BCAC"),
        ("JCAC", "JCAC"),
        ("CAC", "CAC"),
    ]
    exhibition_id = models.ForeignKey(
        "Exhibition",
        null=True,
        blank=True,
        related_name="Rating_exhibition",
        on_delete=models.PROTECT,
    )
    catalog_number = models.PositiveIntegerField(null=True, blank=True)
    rating_pig = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Rating_pig",
        on_delete=models.PROTECT,
    )
    type_build = models.TextField(null=True, blank=True)
    head_eyes_ears = models.TextField(null=True, blank=True)
    coat = models.TextField(null=True, blank=True)
    breed_specificity = models.TextField(null=True, blank=True)
    color_specificity = models.TextField(null=True, blank=True)
    condition = models.TextField(null=True, blank=True)
    notice = models.TextField(null=True, blank=True)
    pig_rating = models.CharField(max_length=50, choices=RATING_CHOICES, default="")
    cac = models.CharField(max_length=10, choices=CAC_CHOICES, default="")


class Winners(models.Model):
    exhibition_id = models.ForeignKey(
        "Exhibition",
        null=True,
        blank=True,
        related_name="Winners_exhibition",
        on_delete=models.PROTECT,
    )
    best_in_show_b_c_1 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISBC1",
        on_delete=models.PROTECT,
    )
    best_in_show_b_c_2 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISBC2",
        on_delete=models.PROTECT,
    )
    best_in_show_b_c_3 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISBC3",
        on_delete=models.PROTECT,
    )
    best_in_show_baby_1 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISB1",
        on_delete=models.PROTECT,
    )
    best_in_show_baby_2 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISB2",
        on_delete=models.PROTECT,
    )
    best_in_show_baby_3 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISB3",
        on_delete=models.PROTECT,
    )
    best_in_show_junior_1 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISJ1",
        on_delete=models.PROTECT,
    )
    best_in_show_junior_2 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISJ2",
        on_delete=models.PROTECT,
    )
    best_in_show_junior_3 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISJ3",
        on_delete=models.PROTECT,
    )
    best_in_show_adult_1 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISA1",
        on_delete=models.PROTECT,
    )
    best_in_show_adult_2 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISA2",
        on_delete=models.PROTECT,
    )
    best_in_show_adult_3 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISA3",
        on_delete=models.PROTECT,
    )
    best_in_show_senior_1 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISS1",
        on_delete=models.PROTECT,
    )
    best_in_show_senior_2 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISS2",
        on_delete=models.PROTECT,
    )
    best_in_show_senior_3 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BISS3",
        on_delete=models.PROTECT,
    )
    best_of_best_1 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BOB1",
        on_delete=models.PROTECT,
    )
    best_of_best_2 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BOB2",
        on_delete=models.PROTECT,
    )
    best_of_best_3 = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_BOB3",
        on_delete=models.PROTECT,
    )
    pwcc_winner = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_PWCC",
        on_delete=models.PROTECT,
    )
    pwsc_winner = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Winners_PWSS",
        on_delete=models.PROTECT,
    )
    best_of_breed = models.ManyToManyField(
        "Bob", blank=True, related_name="Winners_bob"
    )


class Bob(models.Model):
    winners_id = models.ForeignKey(
        "Winners",
        null=True,
        blank=True,
        related_name="Bob_winners",
        on_delete=models.PROTECT,
    )
    breed = models.ForeignKey(
        "Breed",
        null=True,
        blank=True,
        related_name="Bob_breed",
        on_delete=models.PROTECT,
    )
    best_of_breed = models.ForeignKey(
        "Pig", null=True, blank=True, related_name="Bob_bob", on_delete=models.PROTECT
    )
    best_of_breed_baby = models.ForeignKey(
        "Pig", null=True, blank=True, related_name="Bob_bobb", on_delete=models.PROTECT
    )
    best_of_breed_junior = models.ForeignKey(
        "Pig", null=True, blank=True, related_name="Bob_bobj", on_delete=models.PROTECT
    )
    best_of_breed_adult = models.ForeignKey(
        "Pig", null=True, blank=True, related_name="Bob_boba", on_delete=models.PROTECT
    )


class Exhibition(models.Model):
    TYPE_CHOICES = [
        ("normal", "normal"),
        ("ee", "ee"),
    ]
    name = models.CharField(null=False, blank=False, max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    judges = models.ManyToManyField(
        "Judge", blank=True, related_name="Exhibition_judges"
    )
    address = models.CharField(null=True, blank=True, max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default="normal")
    fees = models.CharField(null=True, blank=False, max_length=255)
    entries = models.ForeignKey(
        "Pig", related_name="Exhibition_pigs", on_delete=models.PROTECT
    )
    rating = models.ManyToManyField(
        "Rating", blank=True, related_name="Exhibition_rating"
    )
    # winners
    banner = models.ImageField(upload_to="ehxibitions/baners/", blank=True, null=True)


class ExhibitionGroup(models.Model):
    TYPE_CHOICES = [
        ("normal", "normal"),
        ("summer", "summer"),
        ("winter", "winter"),
    ]
    name = models.CharField(null=True, blank=True, max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default="normal")
    exhibitions = models.ManyToManyField(
        "Exhibition", blank=True, related_name="Group_exhibitions"
    )
    winner = models.ForeignKey(
        "Pig",
        null=True,
        blank=True,
        related_name="Group_winner",
        on_delete=models.PROTECT,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
