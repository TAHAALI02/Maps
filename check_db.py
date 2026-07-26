import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'maps.settings'
import django
django.setup()
from django.db import connection
cursor = connection.cursor()

# Check columns on app_users
cursor.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name = 'app_users'
    ORDER BY ordinal_position
""")
print("=== app_users columns ===")
for row in cursor.fetchall():
    print(f"  {row[0]}")

# Check applied migrations
print("\n=== Applied maps_app migrations ===")
cursor.execute("SELECT name FROM django_migrations WHERE app='maps_app' ORDER BY id")
for row in cursor.fetchall():
    print(f"  {row[0]}")
