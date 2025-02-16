# Generated by Django 5.1.6 on 2025-02-16 10:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("qna", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SessionChatInfo",
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
                ("userQuestion", models.TextField(default=None)),
                ("aiResponse", models.TextField(default=None)),
                ("generatedOn", models.DateTimeField(auto_now_add=True)),
                (
                    "chatSession",
                    models.ForeignKey(
                        help_text="Document Related to Which Session",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="qna.chatsessionmanager",
                    ),
                ),
            ],
        ),
    ]
