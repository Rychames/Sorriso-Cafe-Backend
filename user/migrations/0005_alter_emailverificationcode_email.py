# Generated by Django 5.1.3 on 2024-12-10 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_emailverificationcode_activated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverificationcode',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
