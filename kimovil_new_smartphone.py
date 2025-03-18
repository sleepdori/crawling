import os
import json
import time
import sys
import pandas as pd
from common.config_loader import ConfigLoader
from common.print_to_logger import PrintToLogger
from cipher.crypto_util import crypto_util
from dbutil.oracle_db_manager import OracleDBManager
from dbutil.postgresql_db_manager import PostgreSQLManager
from util.myutil import read_json


config = ConfigLoader()
path_separator = config.get_path_separator()
project_home = config.get("project_home")
log_dir = f'{project_home}{path_separator}{config.get("log_dir")}'

logfile = config.get("logfile")
logLevel = config.get("logLevel")
logformat = config.get("logformat")

print(project_home, path_separator, log_dir, logfile, logLevel, logformat)
sys.stdout = PrintToLogger(log_dir=log_dir, log_file_prefix=logfile, loglevel=logLevel)

crawling_out_path = config.get("crawling", "out_path")
use_connection_nm = config.get("crawling", "use_connection_nm")
load_database_type = config.get("crawling", "load_database_type")

key_file_path = config.get('key_file_path')
key_file_name = config.get('key_file_name')

crypto = crypto_util(key_file_path, key_file_name)

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

sp_no = 1
max_sp_no_query = config.get("crawling", "kimovil","query", use_connection_nm, "max_sp_no_query")
is_sp_model_check_query = config.get("crawling", "kimovil","query", use_connection_nm, "is_exists_query")
kimovil_delete_query = config.get("crawling", "gsmarena", "query", use_connection_nm, 'delete_query')

# 연결 시도
connected = db_mgr.check_connection()
if not connected:
    print(f"Database connection failed")
    exit()

result = db_mgr.select(max_sp_no_query)

for row in result:
    sp_no = row['MAX_SP_NO']
    print(f"max sp_no : {sp_no}")

kimovil_new_sp_list_target_nm = config.get("crawling", "kimovil", "new_sp_list_target")
kimovil_new_sp_list_fix = config.get("crawling", "kimovil", "new_sp_list_fix")
kimovil_new_sp_spec = config.get("crawling", "kimovil", "new_sp_spec")
kimovil_new_sp_price = config.get("crawling", "kimovil", "new_sp_price")

new_sp_list_input_file = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{kimovil_new_sp_list_target_nm}'
spec_src_json_file_name = rf"{project_home}{path_separator}{crawling_out_path}{path_separator}kimovil_new_sp_spec_info_src.json"
list_json_file_name = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{kimovil_new_sp_list_fix}'
spec_json_file_name = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{kimovil_new_sp_spec}'
price_json_file_name = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{kimovil_new_sp_price}'

print(f"new_sp_list_input_file : {new_sp_list_input_file}")
print(f"spec_src_json_file_name : {spec_src_json_file_name}")
print(f"load_list_json_file_name : {list_json_file_name}")
print(f"load_spec_json_file_name : {spec_json_file_name}")
print(f"load_price_json_file_name : {price_json_file_name}")

price_col = ['price_model1','price_regn1','price_memory1','price_storage1','p_price1','price_model2','price_regn2','price_memory2','price_storage2','p_price2','price_model3','price_regn3','price_memory3','price_storage3','p_price3','price_model4','price_regn4','price_memory4','price_storage4','p_price4','price_model5','price_regn5','price_memory5','price_storage5','p_price5','price_model6','price_regn6','price_memory6','price_storage6','p_price6','price_model7','price_regn7','price_memory7','price_storage7','p_price7','price_model8','price_regn8','price_memory8','price_storage8','p_price8','price_model9','price_regn9','price_memory9','price_storage9','p_price9','price_model10','price_regn10','price_memory10','price_storage10','p_price10','price_model11','price_regn11','price_memory11','price_storage11','p_price11' ]

#JSON 파일에서 smart phone 목록 조회
new_sp_target_list = read_json(new_sp_list_input_file)
new_sp_target_spec = read_json(spec_src_json_file_name)
print(f"신규 처리 대상 건수(예상) : {len(new_sp_target_list)}")

for device_index, model_info in new_sp_target_list.iterrows() :
    check_query = is_sp_model_check_query.format(model_info['device_link'])
    result = db_mgr.select(check_query)

    is_check = False
    for row in result:
        is_cnt = row['CNT']
        print(f"url info : {model_info['device_link']} , db check count : {is_cnt} ")
        if is_cnt > 0 :
            is_check = True
            params = {'LINK_URL' : model_info['device_link']}
            db_mgr.delete(kimovil_delete_query, params)
            # new_sp_target_list.drop(index=device_index, inplace=True)
            # new_sp_target_spec = new_sp_target_spec.query(f"{model_info['device_seq']} != {new_sp_target_spec['device_seq']}")
            
    print(f"device_index : {device_index}, url info : {model_info['device_link']}")
    new_sp_target_spec.loc[new_sp_target_spec['device_seq'] == model_info['device_seq'], "device_seq"] = sp_no
    new_sp_target_list.at[device_index, 'device_seq'] = sp_no
    
    sp_no += 1

    time.sleep(1)

# 크롤링 한 원천 결과 파일 저장
print(spec_src_json_file_name, f"model count {len(new_sp_target_spec)}")
with open(spec_src_json_file_name, 'w') as jf:
    json.dump(new_sp_target_spec.to_dict(orient='records'), jf, indent=4)

price_column_list = []
price_column_list.append('device_seq')
for col in price_col :
    price_column_list.append(col)

df = pd.DataFrame(new_sp_target_spec)
# 크롤링 한 원천 결과 파일 에서 가격 정보를 제외한 스펙 정보 저장
for col in price_col :
    if col in df.columns :
        df = df.drop(columns=col)

print(spec_json_file_name, f"model count {len(df)}")
with open(spec_json_file_name, 'w') as jf:
    json.dump(df.to_dict(orient='records'), jf, indent=4)


# 크롤링 한 원천 결과 파일 에서 가격 정보를 추출하여 정제
df = pd.DataFrame(new_sp_target_spec)
valid_columns = [col for col in price_column_list if col in df.columns]

if len(valid_columns) > 2 : 
    price_df = df.loc[:, valid_columns]

    # df_no_nulls = price_df.dropna(subset=['price_model1'])
    if "price_model1" in price_df.columns:
        df_no_nulls = price_df.dropna(subset=['price_model1'])
    else:
        print("Warning: `price_model1` column not found in price_df.")
        df_no_nulls = price_df

    melted = pd.melt(df_no_nulls, id_vars=['device_seq'], var_name='attribute', value_name='value')

    # 2. attribute에서 컬럼 그룹과 번호를 추출
    melted['group'] = melted['attribute'].str.extract(r'([a-z_]+)')  # 컬럼 이름의 접두사 추출
    melted['index'] = melted['attribute'].str.extract(r'(\d+)$')  # 숫자 부분 추출

    unique_groups = melted['group'].drop_duplicates()
    rename_map = {group: group.split('_')[-1] for group in unique_groups}
    group_str = ','.join(melted['group'].drop_duplicates())
    print(f"rename_map = {rename_map}")

    # 3. 각 group을 pivot하여 넓은 형태로 변환
    pivoted = melted.pivot(index=['device_seq', 'index'], columns='group', values='value').reset_index()

    # 4. 컬럼 이름 정리
    pivoted.columns.name = None  # MultiIndex 제거
    pivoted = pivoted.rename(columns=rename_map)

    # 5. 결과 정렬
    pivoted = pivoted.sort_values(['device_seq', 'index']).drop(columns=['index'])

    df_no_nulls  = pivoted.dropna(subset=['model'])
    print(df_no_nulls.head(100))

    print(price_json_file_name, f"model count {len(price_df)}")
    with open(price_json_file_name, 'w') as jf:
        json.dump(df_no_nulls.to_dict(orient='records'), jf, indent=4)


# 크롤링 리스트에서 신규건 리스트 저장
print(list_json_file_name, f"model count {len(new_sp_target_list)}")
with open(list_json_file_name, 'w') as jf:
    json.dump(new_sp_target_list.to_dict(orient='records'), jf, indent=4)
