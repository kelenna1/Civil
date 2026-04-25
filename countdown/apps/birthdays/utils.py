"""
File import utilities for birthday data.
Handles CSV and Excel file processing with proper validation and error handling.
"""

import logging
from django.db import transaction
from .models import Birthday

logger = logging.getLogger(__name__)


class ImportResult:
    """Result of a birthday import operation."""
    def __init__(self):
        self.added = 0
        self.skipped = 0
        self.errors = []

    @property
    def total_processed(self):
        return self.added + self.skipped + len(self.errors)

    @property
    def is_success(self):
        return len(self.errors) == 0

    def __str__(self):
        return f"Added: {self.added}, Skipped: {self.skipped}, Errors: {len(self.errors)}"


def process_birthday_import(import_obj):
    """
    Process a BirthdayImport file and create Birthday records.
    
    Wrapped in a transaction — if anything goes wrong, nothing is committed.
    Supports duplicate detection (skips if name+date already exists).
    
    Args:
        import_obj: A BirthdayImport model instance with a file attached.
    
    Returns:
        ImportResult with counts and any errors.
    """
    import pandas as pd
    
    result = ImportResult()

    try:
        # Read the file
        if import_obj.file.name.endswith('.csv'):
            df = pd.read_csv(import_obj.file)
        else:
            df = pd.read_excel(import_obj.file)

        # Validate required columns
        required_columns = {'name', 'date_of_birth'}
        actual_columns = set(col.strip().lower() for col in df.columns)

        if not required_columns.issubset(actual_columns):
            missing = required_columns - actual_columns
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}. "
                f"File must contain 'name' and 'date_of_birth' columns."
            )

        # Normalize column names (handle case/whitespace variations)
        df.columns = [col.strip().lower() for col in df.columns]

        # Drop rows with missing required data
        df = df.dropna(subset=['name', 'date_of_birth'])

        if df.empty:
            raise ValueError("No valid data found in the file.")

        # Get existing birthdays for duplicate detection
        existing = set(
            Birthday.objects.filter(
                organization=import_obj.organization,
                is_active=True,
            ).values_list('full_name', 'date_of_birth')
        )

        # Process rows within a transaction
        birthdays_to_create = []

        for idx, row in df.iterrows():
            try:
                name = str(row['name']).strip()[:100]
                
                # Parse date — pandas usually handles this, but be defensive
                dob = pd.to_datetime(row['date_of_birth']).date()

                if not name:
                    result.errors.append(f"Row {idx + 2}: Empty name")
                    continue

                # Check for duplicates
                if (name, dob) in existing:
                    result.skipped += 1
                    continue

                birthdays_to_create.append(Birthday(
                    full_name=name,
                    date_of_birth=dob,
                    organization=import_obj.organization,
                ))
                existing.add((name, dob))  # Prevent duplicates within the file itself

            except Exception as row_error:
                result.errors.append(f"Row {idx + 2}: {str(row_error)}")

        # Bulk create in a transaction
        with transaction.atomic():
            if birthdays_to_create:
                Birthday.objects.bulk_create(birthdays_to_create)
                result.added = len(birthdays_to_create)

        # Update import record
        import_obj.status = 'success' if result.is_success else 'error'
        import_obj.status_detail = str(result)
        import_obj.records_added = result.added
        import_obj.records_skipped = result.skipped
        import_obj.save()

    except Exception as e:
        logger.exception(f"Import failed for {import_obj}")
        result.errors.append(str(e))
        import_obj.status = 'error'
        import_obj.status_detail = str(e)[:500]
        import_obj.save()

    return result
