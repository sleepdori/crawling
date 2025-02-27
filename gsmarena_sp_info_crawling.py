import time
import json
import pandas as pd
from common.config_loader import ConfigLoader
from crawler.gsmarena_sp_list import gamarena_sp_list
from crawler.gsmarena_sp_spec_detail import gsmarena_sp_spec_detail
from util.myutil import read_json

config = ConfigLoader()

path_separator = config.get_path_separator()
project_home = config.get("project_home")

crawling_out_path = config.get("crawling", "out_path")
use_connection_nm = config.get("crawling", "use_connection_nm")
load_database_type = config.get("crawling", "load_database_type")
gsmarena_sp_list = config.get("crawling", "gsmarena", "sp_list")
gsmarena_sp_spec = config.get("crawling", "gsmarena", "sp_spec")

out_list_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{gsmarena_sp_list}'
out_spec_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{gsmarena_sp_spec}'

print(f"GSMArena SP List 파일 : {out_list_file_nm}")
print(f"GSMArena SP Spec 파일 : {out_spec_file_nm}")

GET_LIST = False
START_IDX = 6500

if GET_LIST :
    gamarena_sp_list(out_list_file_nm)
    START_IDX = 0

df = read_json(out_list_file_nm)

print(f"new sp list info : {len(df)}")

spec_df = []

if GET_LIST == False :
    spec_df = read_json(out_spec_file_nm)
    for s_index, model_spec in spec_df.iterrows() :
        START_IDX = int(model_spec['device_seq'])

print(f"START DEVICE SEQ : {START_IDX}")

spec_crawler = gsmarena_sp_spec_detail()
for m_index, model_info in df.iterrows() :

    if m_index > START_IDX :
        print(f"brand_name = {model_info['brand_name']}, no = {m_index}, device_name = {model_info['device_name']}, device_link = {model_info['device_link']}")
        spec_crawler = gsmarena_sp_spec_detail()
        spec_success, model_spec_detail = spec_crawler.run_crawling(model_info)

        if spec_success :
            model_spec_detail['device_seq'] = m_index
            spec_df.append(model_spec_detail)
        else :
            time.sleep(10)
            spec_success, model_spec_detail = spec_crawler.run_crawling(model_info)
            if spec_success :
                model_spec_detail['device_seq'] = m_index
                spec_df.append(model_spec_detail)
            else :
                print(f"brand_name = {model_info['brand_name']}, no = {m_index}, device_name = {model_info['device_name']}, device_link = {model_info['device_link']}, error : {model_spec_detail}")

        time.sleep(5)

        if m_index % 500 == 0 :
            print(out_spec_file_nm, f"model count {len(spec_df)}")
            with open(out_spec_file_nm, 'w', encoding='utf-8') as f:
                json.dump(spec_df, f, ensure_ascii=False, indent=4)

print(out_spec_file_nm, f"model count {len(spec_df)}")
with open(out_spec_file_nm, 'w', encoding='utf-8') as f:
    json.dump(spec_df, f, ensure_ascii=False, indent=4)
    