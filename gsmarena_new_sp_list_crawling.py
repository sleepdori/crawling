import time
import json
import pandas as pd
from common.config_loader import ConfigLoader
from cipher.crypto_util import CryptoUtil
from dbutil.oracle_db_manager import OracleDBManager
from dbutil.postgresql_db_manager import PostgreSQLManager
from crawler.gsmarena_new_sp_list import gamarena_new_sp_list
from util.myutil import read_json

config = ConfigLoader()

path_separator = config.get_path_separator()
project_home = config.get("project_home")

crawling_out_path = config.get("crawling", "out_path")
use_connection_nm = config.get("crawling", "use_connection_nm")
load_database_type = config.get("crawling", "load_database_type")

gsmarena_new_sp_list_target_nm = config.get("crawling", "gsmarena", "new_sp_list_target")
gsmarena_new_sp_list_fix = config.get("crawling", "gsmarena", "new_sp_list_fix")

out_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{gsmarena_new_sp_list_target_nm}'
new_sp_list_file = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{gsmarena_new_sp_list_fix}'

print(f"신규 판정 대상 파일 : {out_file_nm}")
print(f"신규 모델 파일 : {new_sp_list_file}")

key_file_path = config.get('key_file_path')
key_file_name = config.get('key_file_name')
crypto = CryptoUtil(key_file_path, key_file_name)

HOST = config.get("databases", use_connection_nm, "host")
PORT = config.get("databases", use_connection_nm, "port")
DATABASE = config.get("databases", use_connection_nm, "database")
DSN = f'{HOST}:{PORT}/{DATABASE}'
DB_USER = crypto.decrypt(config.get("databases", use_connection_nm, "user"))
DB_PASS = crypto.decrypt(config.get("databases", use_connection_nm, "password"))

db_mgr = None
if load_database_type.lower() == 'oracle' :
    db_mgr = OracleDBManager(DB_USER, DB_PASS, DSN)
elif load_database_type.lower() == 'postgresql' :
    db_mgr = PostgreSQLManager(DB_USER, DB_PASS, HOST, PORT, DATABASE)

gsmarena_is_exists_query = config.get("crawling", "gsmarena", "query", use_connection_nm, 'is_exists_query')
gsmarena_max_sp_no_query = config.get("crawling", "gsmarena", "query", use_connection_nm, 'max_sp_no_query')

print(f"get gsmarena_is_exists_query : {gsmarena_is_exists_query}")
# 연결 시도
connected = db_mgr.check_connection()
if not connected:
    print(f"Database connection failed")
    exit()

result = db_mgr.select(gsmarena_max_sp_no_query, params=None)
sp_no = 0
for row in result:
    sp_no = row['MAX_SP_NO']

print(f"max_sp_no = {sp_no}")

gamarena_new_sp_list(out_file_nm)

df = read_json(out_file_nm)

print(f"new sp list info : {len(df)}")

new_df = []

for m_index, model_info in df.iterrows() :
    brand_name = model_info['brand_name']
    model_name = model_info['device_name']
    
    params = None
    if load_database_type.lower() == 'oracle' :
        params = {"BRND_NM": brand_name, "MODEL_NM": model_name}
    elif load_database_type.lower() == 'postgresql' :
        params = [brand_name, model_name]

    connected = db_mgr.check_connection()
    if not connected:
        print(f"Database connection failed")
        exit()

    result = db_mgr.select(gsmarena_is_exists_query, params=params)

    for row in result:
        is_cnt = row['CNT']
        if is_cnt > 0 :
            print(f"brand_name : {brand_name}, model_name : {model_name} 는 존재하는 모델입니다.")
        else :
            model_info['device_seq'] = sp_no
            sp_no += 1
            print(f"brand_name : {brand_name}, model_name : {model_name} 는 신규 모델입니다. {type(model_info)}")
            
            new_df.append(model_info.to_dict())


    time.sleep(0.2)  # 요청 간 딜레이 추가

print(new_sp_list_file, f"model count {len(new_df)}, {type(new_df)}")

with open(new_sp_list_file, 'w') as f:
    json.dump(new_df, f, indent=4)