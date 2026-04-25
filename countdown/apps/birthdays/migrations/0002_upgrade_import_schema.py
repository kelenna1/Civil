"""
Custom migration to upgrade BirthdayImport schema.
Truncates existing status values before altering the column,
adds new tracking fields, and removes the old 'processed' field.
"""

from django.db import migrations, models


def truncate_status_values(apps, schema_editor):
    """Truncate existing status values to fit the new max_length."""
    BirthdayImport = apps.get_model('birthdays', 'BirthdayImport')
    for imp in BirthdayImport.objects.filter(status__regex=r'^.{51,}'):
        # Move the long status to status_detail (after it's created)
        imp.status = imp.status[:50]
        imp.save(update_fields=['status'])


class Migration(migrations.Migration):

    dependencies = [
        ('birthdays', '0001_initial'),
    ]

    operations = [
        # 1. Add new fields first
        migrations.AddField(
            model_name='birthdayimport',
            name='status_detail',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='birthdayimport',
            name='records_added',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='birthdayimport',
            name='records_skipped',
            field=models.PositiveIntegerField(default=0),
        ),

        # 2. Truncate long status values
        migrations.RunPython(truncate_status_values, migrations.RunPython.noop),

        # 3. Now alter the status field (safe because values are truncated)
        migrations.AlterField(
            model_name='birthdayimport',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('processing', 'Processing'), ('success', 'Success'), ('error', 'Error')],
                default='pending',
                max_length=50,
            ),
        ),

        # 4. Remove the old processed field
        migrations.RemoveField(
            model_name='birthdayimport',
            name='processed',
        ),
    ]
