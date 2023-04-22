# Generated by Django 4.2 on 2023-04-19 08:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_spectrum_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='spectrum',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]