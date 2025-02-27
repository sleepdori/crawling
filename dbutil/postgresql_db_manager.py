import re
import psycopg2
import pandas as pd

class PostgreSQLManager:
    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            print("PostgreSQL DB Connection OK!!")
        except psycopg2.Error as error:
            print(f"PostgreSQL DB Connection Failed: {error}")
            self.conn = None
            self.cursor = None

    def check_connection(self):
        try:
            if self.conn is None or self.cursor is None or self.conn.closed:
                print("Reconnecting to the database...")
                self.connect()
            self.cursor.execute("SELECT 1")
            return True
        except psycopg2.Error as error:
            print(f"Connection check failed: {error}")
            self.connect()
            return False

    def execute_query(self, sql, params=None):
        try:
            if not self.check_connection():
                raise psycopg2.Error("Database connection is not available.")
            self.cursor.execute(sql, params)
            return True
        except psycopg2.Error as error:
            print(f"Query Execution Error: {error}")
            return False

    def insert(self, sql, params=None):
        if self.execute_query(sql, params):
            self.conn.commit()
            print("Insert OK!")
            return True
        return False

    def convert_sql(self, sql):
        """
        Convert Oracle-style ':variable' SQL to PostgreSQL-style '%s'.
        :param sql: The SQL query with Oracle-style placeholders.
        :return: SQL query with PostgreSQL-style placeholders.
        """
        return re.sub(r':\w+', '%s', sql)
    
    def load(self, data, sql):
        """
        Load data into the database from a Pandas DataFrame.
        :param df: DataFrame containing data to be inserted.
        :param sql: SQL query with Oracle-style placeholders.
        """
        try:
            if not self.check_connection():
                raise psycopg2.Error("Database connection is not available.")

            # Convert Oracle-style ':variable' to PostgreSQL-style '%s'
            converted_sql = self.convert_sql(sql)
            if isinstance(data, pd.DataFrame):
                data = [tuple(row) for row in data.to_numpy()]
            elif isinstance(data, list) and isinstance(data[0], dict):
                data = [tuple(d.values()) for d in data]
            elif not isinstance(data, list):
                raise TypeError("Input data must be a Pandas DataFrame or a list of tuples.")
            # Execute the SQL query
            self.cursor.executemany(converted_sql, data)
            self.conn.commit()

            print("Data Load OK!!")
            return True
        except psycopg2.Error as error:
            print(f"Data Load Error: {error}")
            self.conn.rollback()  # Rollback on error
            return False

    def select(self, sql, params=None):
        try:
            if not self.check_connection():
                raise psycopg2.Error("Database connection is not available.")
            self.cursor.execute(sql, params)
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            print(result)
            return result
        except psycopg2.Error as error:
            print(f"Select Error: {error}")
            return None

    def update(self, sql, params=None):
        if self.execute_query(sql, params):
            self.conn.commit()
            print("Update OK!")
            return True
        return False

    def delete(self, sql, params=None):
        if self.execute_query(sql, params):
            self.conn.commit()
            print("Delete OK!")
            return True
        return False

    def commit(self):
        try:
            if self.conn:
                self.conn.commit()
                print("Transaction committed.")
        except psycopg2.Error as e:
            print(f"Commit error: {e}")
            raise

    def rollback(self):
        try:
            if self.conn:
                self.conn.rollback()
                print("Transaction rolled back.")
        except psycopg2.Error as e:
            print(f"Rollback error: {e}")
            raise

    def columns_info(self, schema_name=None, table_name=None):
        try:
            if table_name is None:
                raise ValueError("Table name must be provided.")

            query = ( """
                SELECT    upper(column_name) as "COLUMN_NAME"                                              
                        , upper(data_type) as "DATA_TYPE"                                                  
                        , CASE WHEN character_maximum_length IS NOT NULL THEN character_maximum_length     
                            WHEN udt_name = 'int4'                    THEN 10                              
                            WHEN udt_name = 'int8'                    THEN 19                              
                            WHEN udt_name = 'numeric'                 THEN numeric_precision               
                            ELSE numeric_precision                                                         
                        END  as "DATA_LENGTH"                                                              
                        , COALESCE(numeric_scale, 0) as "DATA_SCALE"                                       
                        , SUBSTRING(is_nullable, 1, 1)              as "NULLABLE"                           
                FROM information_schema.columns                                                                                         
                WHERE table_name = lower(%s)                                                               
            """)
            params = [table_name]

            if schema_name:
                query += " AND table_schema = lower(%s)"
                params.append(schema_name)

            query += " ORDER BY ordinal_position"

            print(query)
            return self.select(query, params)
        except ValueError as ve:
            print(f"ValueError: {ve}")
            return None
        except psycopg2.Error as error:
            print(f"Error fetching column info: {error}")
            return None

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("PostgreSQL DB Connection closed.")