# Generated by Django 5.1.3 on 2024-11-14 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='date_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]
