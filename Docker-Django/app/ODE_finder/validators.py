# Validators for filefields in Django

def validate_csv_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Please upload only csv files.')


def validate_csv_structure(value):
    # TODO: ensure the csv follows the correct structure for parsing
    import pandas as pd
    from django.core.exceptions import ValidationError
