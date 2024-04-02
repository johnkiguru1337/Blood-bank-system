# Generated by Django 5.0.3 on 2024-03-25 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0003_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloodrequest',
            name='role',
            field=models.CharField(choices=[('donor', 'Donor'), ('patient', 'Patient'), ('staff', 'Staff')], default='patient', max_length=20),
        ),
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='static/profile_pics'),
        ),
    ]
