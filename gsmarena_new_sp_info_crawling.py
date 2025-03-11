import time
import json
import pandas as pd
import socket
import concurrent.futures
import itertools
import requests
from common.config_loader import ConfigLoader
from crawler.gsmarena_new_sp_list_proxy import gamarena_new_sp_list
from crawler.gsmarena_sp_spec_detail_proxy import gsmarena_sp_spec_detail
from util.myutil import read_json

config = ConfigLoader()

path_separator = config.get_path_separator()
project_home = config.get("project_home")

crawling_out_path = config.get("crawling", "out_path")
use_connection_nm = config.get("crawling", "use_connection_nm")
load_database_type = config.get("crawling", "load_database_type")

gsmarena_new_sp_list_target_nm = config.get("crawling", "gsmarena", "new_sp_list_target")
gsmarena_new_sp_spec = config.get("crawling", "gsmarena", "new_sp_spec")



out_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{gsmarena_new_sp_list_target_nm}'
spec_json_file_name = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{gsmarena_new_sp_spec}'
spec_json_file_name = spec_json_file_name.replace(".json", "_target.json")

print(f"신규 판정 대상 파일 : {out_file_nm}")

gamarena_new_sp_list(out_file_nm)

df = read_json(out_file_nm)
model_spec_info = []
print(f"new sp list info : {len(df)}")
device_seq = 1

for brand_index, model_info in df.iterrows() :
    print(f"brand_name = {model_info['brand_name']}, no = {brand_index}, device_name = {model_info['device_name']}, device_link = {model_info['device_link']}")
    spec_crawler = gsmarena_sp_spec_detail()
    spec_success, model_spec_detail = spec_crawler.run_crawling(model_info)

    if spec_success :
        model_spec_detail['device_seq'] = device_seq
        model_spec_info.append(model_spec_detail)
    
    device_seq += 1

    time.sleep(20)

print(spec_json_file_name, f"model count {len(model_spec_info)}")
with open(spec_json_file_name, 'w', encoding='utf-8') as f:
    json.dump(model_spec_info, f, ensure_ascii=False, indent=4)
