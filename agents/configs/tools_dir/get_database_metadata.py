import asyncpg
import os

async def get_database_metadata(connection):
    metadata = {}
    tables = await get_tables(connection)
    
    for table in tables:
        metadata[table] = {
            "columns": await get_columns(connection, table),
            "primary_keys": await get_primary_keys(connection, table),
            "foreign_keys": await get_foreign_keys(connection, table),
        }
    
    return metadata

async def connect_to_supabase():
    """Connect to the Supabase database."""
    try:
        # Fetch connection details from environment variables
        db_host = os.getenv("SUPABASE_DB_HOST", "aws-0-us-west-1.pooler.supabase.com")
        db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
        db_user = os.getenv("SUPABASE_DB_USER", "postgres.acejgpdnjeyknidwnkei")
        db_password = os.getenv("SUPABASE_DB_PASSWORD", "sJzxjWB9aDVuBX2")
        db_port = int(os.getenv("SUPABASE_DB_PORT", 6543))

           # Establish connection
        connection = await asyncpg.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
            statement_cache_size=0  # Disable statement caching to avoid issues with pgbouncer
        )
        print("Successfully connected to the Supabase database.")
        return connection
    except asyncpg.exceptions.PostgresError as pg_error:
        print(f"PostgreSQL error: {pg_error}")
        raise
    except Exception as e:
        print(f"Error connecting to the Supabase database: {e}")
        raise
      
async def get_tables(connection):
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
    """
    rows = await connection.fetch(query)
    tables = [row['table_name'] for row in rows]
    print("Tables:", tables)
    return tables
  
async def get_columns(connection, table_name):
    query = f"""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = '{table_name}';
    """
    rows = await connection.fetch(query)
    columns = [
        {
            "column_name": row['column_name'],
            "data_type": row['data_type'],
            "is_nullable": row['is_nullable'],
        }
        for row in rows
    ]
    print(f"Columns for {table_name}:", columns)
    return columns

async def get_primary_keys(connection, table_name):
    query = f"""
    SELECT kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'PRIMARY KEY';
    """
    rows = await connection.fetch(query)
    primary_keys = [row['column_name'] for row in rows]
    print(f"Primary Keys for {table_name}:", primary_keys)
    return primary_keys
  
async def get_foreign_keys(connection, table_name):
    query = f"""
    SELECT
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM
        information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY';
    """
    rows = await connection.fetch(query)
    foreign_keys = [
        {
            "column_name": row['column_name'],
            "foreign_table_name": row['foreign_table_name'],
            "foreign_column_name": row['foreign_column_name'],
        }
        for row in rows
    ]
    print(f"Foreign Keys for {table_name}:", foreign_keys)
    return foreign_keys