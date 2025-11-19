import os
import sys
import traceback
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()

def main():
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        
        print(f'✅ Conexión Neo4j OK — URI: {uri}, database: {database}')
        
        # Run a simple test query
        with driver.session(database=database) as session:
            result = session.run("RETURN 'Neo4j está funcionando!' AS message")
            record = result.single()
            print(f'Test query result: {record["message"]}')
            
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) AS count")
            count = result.single()["count"]
            print(f'Total nodes in database: {count}')
        
        driver.close()
        return 0
        
    except Exception:
        print('❌ Error conectando a Neo4j:')
        traceback.print_exc()
        return 3

if __name__ == '__main__':
    sys.exit(main())
