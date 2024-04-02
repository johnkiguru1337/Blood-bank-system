# Generated by Django 5.0.3 on 2024-03-27 20:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0006_alter_blooddonation_blood_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationcount',
            name='id_donor',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='mysite.donor'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='donationcount',
            name='donor',
            field=models.CharField(max_length=255),
        ),
    ]
