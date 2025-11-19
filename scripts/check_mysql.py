import os
import sys
import traceback

# Ensure project root is on sys.path so top-level packages like `utils` and
# `models` can be imported when running this script directly.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

from utils.database_connector import DatabaseConnector
from models.relational_models import RelationalModels


def main():
    print('== MySQL check script ==')
    connector = DatabaseConnector()

    conn = connector.connect_mysql()
    if not conn:
        print('ERROR: Could not connect to MySQL. Ensure MySQL is running and env vars are set.')
        return 2

    try:
        print('Creating relational tables (if not exists)...')
        RelationalModels.create_tables(conn)

        print('\nListing tables in database:')
        cursor = conn.cursor()
        cursor.execute('SHOW TABLES;')
        rows = cursor.fetchall()
        if not rows:
            print('  (no tables found)')
        else:
            for r in rows:
                print('  -', r[0])
        cursor.close()
        return 0
    except Exception as e:
        print('ERROR while creating/listing tables:')
        traceback.print_exc()
        return 3
    finally:
        try:
            connector.close_all_connections()
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(main())
