# Generated by Django 5.0.3 on 2024-03-27 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0007_donationcount_id_donor_alter_donationcount_donor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationcount',
            name='id_donor',
            field=models.PositiveIntegerField(),
        ),
    ]
