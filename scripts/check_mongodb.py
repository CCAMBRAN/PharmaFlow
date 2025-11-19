import os
import sys
import traceback
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

def main():
    uri = os.getenv('MONGODB_URI')
    if not uri:
        print('MONGODB_URI no está definido en .env')
        return 2
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # ping para probar la conexión
        client.admin.command('ping')
        db_name = os.getenv('MONGODB_DATABASE', 'pharmaflow')
        db = client[db_name]
        print('✅ Conexión MongoDB Atlas OK — base:', db_name)
        print('Colecciones existentes:', db.list_collection_names())
        client.close()
        return 0
    except Exception:
        print('❌ Error conectando a MongoDB Atlas:')
        traceback.print_exc()
        return 3

if __name__ == '__main__':
    sys.exit(main())
