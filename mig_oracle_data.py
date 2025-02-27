import oracledb
import pandas as pd

def migrate_table(table_name, dev_dsn, prd_dsn, dev_user, dev_password, prd_user, prd_password):
    """
    오라클 개발에서 운영으로 특정 테이블의 데이터를 마이그레이션하는 함수.
    
    :param table_name: 복사할 테이블 이름
    :param dev_dsn: 개발 데이터베이스의 DSN (예: "host:port/service_name")
    :param prd_dsn: 운영 데이터베이스의 DSN
    :param dev_user: 개발 데이터베이스 사용자명
    :param dev_password: 개발 데이터베이스 비밀번호
    :param prd_user: 운영 데이터베이스 사용자명
    :param prd_password: 운영 데이터베이스 비밀번호
    """
    
    try:
        # A_DEV 데이터베이스 연결
        dev_conn = oracledb.connect(user=dev_user, password=dev_password, dsn=dev_dsn)
        dev_cursor = dev_conn.cursor()
        
        # A_PRD 데이터베이스 연결
        prd_conn = oracledb.connect(user=prd_user, password=prd_password, dsn=prd_dsn)
        prd_cursor = prd_conn.cursor()
        
        # A_DEV에서 데이터 조회
        query = f"SELECT * FROM {table_name}"
        dev_cursor.execute(query)
        
        # 컬럼 이름 가져오기
        columns = [desc[0] for desc in dev_cursor.description]
        
        # 데이터 가져오기
        rows = dev_cursor.fetchall()
        
        if not rows:
            print(f"{table_name} 테이블에 복사할 데이터가 없습니다.")
            return
        
        # A_PRD에 데이터 삽입
        placeholders = ", ".join([":" + str(i + 1) for i in range(len(columns))])
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        prd_cursor.executemany(insert_query, rows)
        prd_conn.commit()
        
        print(f"{table_name} 테이블 데이터를 개발서버에서 운영서버로 성공적으로 복사했습니다.")
    
    except oracledb.DatabaseError as e:
        print("오류 발생:", e)
    
    finally:
        # 연결 종료
        if dev_cursor: dev_cursor.close()
        if dev_conn: dev_conn.close()
        if prd_cursor: prd_cursor.close()
        if prd_conn: prd_conn.close()

# 예제 사용법
migrate_table(
    table_name="DL_MNL_LOAD_DATA_DTL",
    dev_dsn="10.155.21.136:1621/SMIP_DEV",
    prd_dsn="10.138.32.221:1621/SMIP_PRD",
    dev_user="SMIP_SLSI_DEV",
    dev_password="1q2w3e4r!",
    prd_user="SMIP_SLSI_PRD",
    prd_password="Slsi2025!"
    # dev_user="SMIP_SLSI_DWDM_DEV",
    # dev_password="1q2w3e4r!",
    # prd_user="SMIP_SLSI_DWDM_PRD",
    # prd_password="Slsidw2025!"    
)
