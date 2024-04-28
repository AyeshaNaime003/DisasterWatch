# Generated by Django 4.2.11 on 2024-04-24 21:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_alter_customuser_profile_picture"),
    ]

    operations = [
        migrations.CreateModel(
            name="InferenceModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("disaster_date", models.DateField()),
                ("disaster_city", models.CharField(max_length=100)),
                ("disaster_state", models.CharField(max_length=100)),
                ("disaster_country", models.CharField(max_length=100)),
                ("disaster_type", models.CharField(max_length=50)),
                ("disaster_description", models.TextField(max_length=300)),
                ("disaster_comments", models.TextField(max_length=300)),
                ("tif_middle_latitude", models.FloatField()),
                ("tif_middle_longitude", models.FloatField()),
                ("pre_tif_path", models.CharField(max_length=300)),
                ("post_tif_path", models.CharField(max_length=300)),
                ("results", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]