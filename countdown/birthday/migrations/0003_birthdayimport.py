# Generated by Django 5.1.6 on 2025-05-21 22:08

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('birthday', '0002_alter_organization_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BirthdayImport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='birthday_imports/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'csv'])])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('processed', models.BooleanField(default=False)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='birthday.organization')),
            ],
        ),
    ]
