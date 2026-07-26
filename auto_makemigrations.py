import os
import sys
from django.core.management import execute_from_command_line
from unittest.mock import patch

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maps_project.settings') # wait, maps.settings is what I saw before

# Fix the settings module
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'Maps.settings' # The project is Maps, so Maps.settings

def mock_input(prompt):
    print(f"Mocking input for: {prompt}")
    return 'y'

if __name__ == '__main__':
    # Patch input to always return 'y'
    with patch('builtins.input', mock_input):
        # Patch sys.stdout.isatty to make Django think it's interactive
        with patch('sys.stdout.isatty', return_value=True):
            execute_from_command_line(['manage.py', 'makemigrations'])
