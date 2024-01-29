# Generated by Django 3.2.23 on 2024-01-29 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_page', '0009_alter_breeding_nickname'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Exhibition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(choices=[('normal', 'normal'), ('ee', 'ee')], default='normal', max_length=255)),
                ('fees', models.CharField(max_length=255, null=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='ehxibitions/baners/')),
            ],
        ),
        migrations.CreateModel(
            name='Judge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=5)),
                ('town', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('judge_number', models.CharField(blank=True, max_length=50, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=25, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('license', models.CharField(blank=True, max_length=255, null=True)),
                ('judging_in', models.TextField(blank=True, null=True)),
                ('languages', models.TextField(blank=True, null=True)),
                ('standard_a', models.CharField(blank=True, max_length=5, null=True)),
                ('standard_b', models.CharField(blank=True, max_length=5, null=True)),
                ('standard_c', models.CharField(blank=True, max_length=5, null=True)),
                ('standard_d', models.CharField(blank=True, max_length=5, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='pig',
            name='is_in_breeding',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Winners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('best_in_show_adult_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISA1', to='main_page.pig')),
                ('best_in_show_adult_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISA2', to='main_page.pig')),
                ('best_in_show_adult_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISA3', to='main_page.pig')),
                ('best_in_show_b_c_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISBC1', to='main_page.pig')),
                ('best_in_show_b_c_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISBC2', to='main_page.pig')),
                ('best_in_show_b_c_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISBC3', to='main_page.pig')),
                ('best_in_show_baby_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISB1', to='main_page.pig')),
                ('best_in_show_baby_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISB2', to='main_page.pig')),
                ('best_in_show_baby_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISB3', to='main_page.pig')),
                ('best_in_show_junior_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISJ1', to='main_page.pig')),
                ('best_in_show_junior_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISJ2', to='main_page.pig')),
                ('best_in_show_junior_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISJ3', to='main_page.pig')),
                ('best_in_show_senior_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISS1', to='main_page.pig')),
                ('best_in_show_senior_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISS2', to='main_page.pig')),
                ('best_in_show_senior_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BISS3', to='main_page.pig')),
                ('best_of_best_1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BOB1', to='main_page.pig')),
                ('best_of_best_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BOB2', to='main_page.pig')),
                ('best_of_best_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_BOB3', to='main_page.pig')),
                ('best_of_breed', models.ManyToManyField(blank=True, related_name='Winners_bob', to='main_page.Bob')),
                ('exhibition_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_exhibition', to='main_page.exhibition')),
                ('pwcc_winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_PWCC', to='main_page.pig')),
                ('pwsc_winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Winners_PWSS', to='main_page.pig')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catalog_number', models.PositiveIntegerField(blank=True, null=True)),
                ('type_build', models.TextField(blank=True, null=True)),
                ('head_eyes_ears', models.TextField(blank=True, null=True)),
                ('coat', models.TextField(blank=True, null=True)),
                ('breed_specificity', models.TextField(blank=True, null=True)),
                ('color_specificity', models.TextField(blank=True, null=True)),
                ('condition', models.TextField(blank=True, null=True)),
                ('notice', models.TextField(blank=True, null=True)),
                ('pig_rating', models.CharField(choices=[('', ''), ('Dyskwalifikacja', 'DSF'), ('Dostateczna', 'N-B'), ('Dobra', 'G'), ('Bardzo dobra', 'SG'), ('Doskonała', 'HV'), ('Wybitna', 'V')], default='', max_length=50)),
                ('cac', models.CharField(choices=[('', ''), ('BCAC', 'BCAC'), ('JCAC', 'JCAC'), ('CAC', 'CAC')], default='', max_length=10)),
                ('exhibition_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Rating_exhibition', to='main_page.exhibition')),
                ('rating_pig', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Rating_pig', to='main_page.pig')),
            ],
        ),
        migrations.CreateModel(
            name='ExhibitionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(choices=[('normal', 'normal'), ('summer', 'summer'), ('winter', 'winter')], default='normal', max_length=255)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('exhibitions', models.ManyToManyField(blank=True, related_name='Group_exhibitions', to='main_page.Exhibition')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Group_winner', to='main_page.pig')),
            ],
        ),
        migrations.AddField(
            model_name='exhibition',
            name='entries',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Exhibition_pigs', to='main_page.pig'),
        ),
        migrations.AddField(
            model_name='exhibition',
            name='judges',
            field=models.ManyToManyField(blank=True, related_name='Exhibition_judges', to='main_page.Judge'),
        ),
        migrations.AddField(
            model_name='exhibition',
            name='rating',
            field=models.ManyToManyField(blank=True, related_name='Exhibition_rating', to='main_page.Rating'),
        ),
        migrations.AddField(
            model_name='bob',
            name='best_of_breed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Bob_bob', to='main_page.pig'),
        ),
        migrations.AddField(
            model_name='bob',
            name='best_of_breed_adult',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Bob_boba', to='main_page.pig'),
        ),
        migrations.AddField(
            model_name='bob',
            name='best_of_breed_baby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Bob_bobb', to='main_page.pig'),
        ),
        migrations.AddField(
            model_name='bob',
            name='best_of_breed_junior',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Bob_bobj', to='main_page.pig'),
        ),
        migrations.AddField(
            model_name='bob',
            name='breed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Bob_breed', to='main_page.breed'),
        ),
        migrations.AddField(
            model_name='bob',
            name='winners_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Bob_winners', to='main_page.winners'),
        ),
    ]
