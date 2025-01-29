# Generated by Django 5.0.4 on 2025-01-29 16:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('name', models.CharField(max_length=255)),
                ('cnpj', models.CharField(max_length=40)),
                ('address', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('Eletrônicos', 'Eletrônicos'), ('Móveis', 'Móveis'), ('Alimentos', 'Alimentos'), ('Vestuário', 'Vestuário'), ('Outros', 'Outros')], max_length=30)),
                ('model', models.CharField(max_length=255)),
                ('company_brand', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('quantity', models.PositiveSmallIntegerField()),
                ('size', models.CharField(blank=True, choices=[('S', 'Pequeno'), ('M', 'Médio'), ('G', 'Grande')], max_length=1, null=True)),
                ('lot', models.BooleanField(default=False)),
                ('sector', models.CharField(max_length=255)),
                ('delivered_by', models.CharField(max_length=255)),
                ('delivery_man_signature', models.FileField(blank=True, null=True, upload_to='signatures/')),
                ('date_receipt', models.DateTimeField(auto_now_add=True)),
                ('current_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_products', to='api.company')),
            ],
        ),
    ]
