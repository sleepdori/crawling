import oracledb

class OracleDBManager:
    def __init__(self, user, password, dsn):
        self.dsn = dsn
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self, autocommit=True, transaction_id=None):
        try:
            self.conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)
            self.conn.autocommit = autocommit 
            self.cursor = self.conn.cursor()
            if transaction_id :
                self.cursor.execute(f"SET TRANSACTION NAME '{transaction_id}'")  
            print("Oracle DB Connection OK!!")
        except oracledb.Error as error:
            print(f"Oracle DB Connection Failed: {error}")
            self.conn = None
            self.cursor = None

    def check_connection(self, autocommit=True, transaction_id=None):
        if self.conn is None or self.cursor is None:
            print("Reconnecting to the database...")
            self.connect(autocommit=autocommit, transaction_id=transaction_id)

        try:
            self.cursor.execute("SELECT 1 FROM DUAL")
            return True
        except oracledb.Error as error:
            print(f"Connection check failed: {error}")
            self.connect(autocommit=autocommit, transaction_id=transaction_id)
            return False

    def execute_query(self, sql, params=None):
        try:
            if not self.check_connection():
                raise oracledb.Error("Database connection is not available.")
            # self.cursor.execute(sql, params)
            self.cursor.prepare(sql)
            
            # prepare()로 필요한 변수만 추출
            required_bind_vars = {var for var in self.cursor.bindnames()}

            # 필요한 변수만 필터링
            filtered_params = {key: params[key] for key in required_bind_vars if params.get(key) is not None}

            print(f"required_bind_vars : {required_bind_vars}, filtered_params : {filtered_params}")
            # SQL 실행
            self.cursor.execute(sql, filtered_params)
            
            return True
        except oracledb.Error as error:
            print(f"Query Execution Error: {error}")
            return False

    def insert(self, sql, params=None):
        if self.execute_query(sql, params):
            self.conn.commit()
            print("Insert OK!")
            return True
        return False

    def load(self, df, sql):
        try:
            if not self.check_connection():
                raise oracledb.Error("Database connection is not available.")
            self.cursor.executemany(sql, df.to_records(index=False))
            self.conn.commit()
            print("Data Load OK!!")
            return True
        except oracledb.Error as error:
            print(f"Data Load Error: {error}")
            return False

    def select(self, sql, params=None):
        try:
            if not self.check_connection():
                raise oracledb.Error("Database connection is not available.")
            # self.cursor.execute(sql, params)
            self.cursor.prepare(sql)
            
            # prepare()로 필요한 변수만 추출
            required_bind_vars = {var for var in self.cursor.bindnames()}

            # 필요한 변수만 필터링
            filtered_params = {key: params[key] for key in required_bind_vars if params.get(key) is not None}

            print(f"required_bind_vars : {required_bind_vars}, filtered_params : {filtered_params}")
            # SQL 실행
            self.cursor.execute(sql, filtered_params)
            
            columns = [col[0] for col in self.cursor.description]
            rows = self.cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            return result
        
        except oracledb.Error as error:
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
        """트랜잭션을 커밋합니다."""
        try:
            if self.conn:
                self.conn.commit()
                print("트랜잭션이 커밋되었습니다.")
        except oracledb.DatabaseError as e:
            print(f"커밋 오류: {e}")
            raise

    def rollback(self):
        """트랜잭션을 롤백합니다."""
        try:
            if self.conn:
                self.conn.rollback()
                print("트랜잭션이 롤백되었습니다.")
        except oracledb.DatabaseError as e:
            print(f"롤백 오류: {e}")
            raise
            
    def columns_info(self, schema_name=None, table_name=None):
        try:
            if table_name is None:
                raise ValueError("Table name must be provided.")

            if schema_name is None:
                query = (
                    f"SELECT COLUMN_ID, COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_SCALE, NULLABLE "
                    f"FROM USER_TAB_COLUMNS "
                    f"WHERE TABLE_NAME = UPPER(:table_name) "
                    f"ORDER BY COLUMN_ID ASC"
                )
                params = {"table_name": table_name}
            else:
                query = (
                    f"SELECT COLUMN_ID, COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_SCALE, NULLABLE "
                    f"FROM ALL_TAB_COLUMNS "
                    f"WHERE OWNER = UPPER(:schema_name) AND TABLE_NAME = UPPER(:table_name) "
                    f"ORDER BY COLUMN_ID ASC"
                )
                params = {"schema_name": schema_name, "table_name": table_name}

            return self.select(query, params)
        except ValueError as ve:
            print(f"ValueError: {ve}")
            return None
        except oracledb.Error as error:
            print(f"Error fetching column info: {error}")
            return None

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Oracle DB Connection closed.")
