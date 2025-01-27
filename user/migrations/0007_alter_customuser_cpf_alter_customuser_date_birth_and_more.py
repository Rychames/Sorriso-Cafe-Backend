# Generated by Django 5.1.3 on 2024-12-10 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_customuser_cpf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='cpf',
            field=models.CharField(blank=True, default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='date_birth',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=20),
            preserve_default=False,
        ),
    ]
