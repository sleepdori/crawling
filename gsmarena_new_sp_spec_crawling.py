import os
import time
import json
import pandas as pd
from common.config_loader import ConfigLoader
from crawler.gsmarena_sp_spec_detail import gsmarena_sp_spec_detail
from util.myutil import read_json

# 옵션 설정: 출력할 최대 행 개수를 None으로 설정 (제한 없음)
pd.set_option('display.max_rows', None)  # 모든 행 출력
pd.set_option('display.max_columns', None)  # 모든 열 출력
pd.set_option('display.width', 1000)       # 출력 화면 폭 설정

config = ConfigLoader()

path_separator = config.get_path_separator()
project_home = config.get("project_home")

crawling_out_path = config.get("crawling", "out_path")
use_connection_nm = config.get("crawling", "use_connection_nm")
load_database_type = config.get("crawling", "load_database_type")

gsmarena_new_sp_spec = config.get("crawling", "gsmarena", "new_sp_spec")
gsmarena_new_sp_list_fix = config.get("crawling", "gsmarena", "new_sp_list_fix")

sp_list_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{gsmarena_new_sp_list_fix}'
spec_json_file_name = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{gsmarena_new_sp_spec}'
print(f"신규 모델 파일 : {sp_list_file_nm}")

model_spec_info = []
df = read_json(sp_list_file_nm)

for brand_index, model_info in df.iterrows() :
    print(f"brand_name = {model_info['brand_name']}, no = {brand_index}, device_name = {model_info['device_name']}, device_link = {model_info['device_link']}")
    spec_crawler = gsmarena_sp_spec_detail()
    spec_success, model_spec_detail = spec_crawler.run_crawling(model_info)

    if spec_success :
        model_spec_detail['device_seq'] = model_info['device_seq']
        model_spec_info.append(model_spec_detail)

    time.sleep(10)

print(spec_json_file_name, f"model count {len(model_spec_info)}")
with open(spec_json_file_name, 'w', encoding='utf-8') as f:
    json.dump(model_spec_info, f, ensure_ascii=False, indent=4)

