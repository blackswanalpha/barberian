# Generated by Django 4.2.10 on 2025-04-26 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffsettings',
            name='services',
            field=models.ManyToManyField(blank=True, related_name='staff_settings', to='services.service', verbose_name='Services'),
        ),
    ]
