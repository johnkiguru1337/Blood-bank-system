# Generated by Django 5.0.3 on 2024-03-27 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0005_bloodtype_alter_profile_image_blooddonation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blooddonation',
            name='blood_type',
            field=models.CharField(max_length=3),
        ),
        migrations.AlterField(
            model_name='blooddonation',
            name='donor',
            field=models.CharField(max_length=255),
        ),
        migrations.DeleteModel(
            name='BloodType',
        ),
    ]