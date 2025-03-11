import os
import json
import time
import sys
import pandas as pd
from common.config_loader import ConfigLoader
from common.print_to_logger import PrintToLogger
from crawler.kimovil_new_sp_list_proxy import crawling_new_sp_list
from crawler.kimovil_sp_spec_detail_proxy import kimovil_sp_spec_detail
from util.myutil import read_json

config = ConfigLoader()
path_separator = config.get_path_separator()
project_home = config.get("project_home")
log_dir = f'{config.get("project_home")}{path_separator}{config.get("log_dir")}'

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

crawling_out_path = config.get("crawling", "out_path")
use_connection_nm = config.get("crawling", "use_connection_nm")
load_database_type = config.get("crawling", "load_database_type")

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

crawling_new_sp_list(kimovil_new_sp_list_target_nm)

model_spec_info = []

#JSON 파일에서 smart phone 목록 조회
crawling_urls = read_json(new_sp_list_input_file)
print(f"crawling_urls count : {len(crawling_urls)}")

spec_crawler = kimovil_sp_spec_detail()

for device_index, model_info in crawling_urls.iterrows() :

    print(f"device_index : {device_index}, url info : {model_info['device_link']}")
    spec_success, model_spec_detail = spec_crawler.runCrawling(model_info)
    
    while True :
        if spec_success : 
            model_spec_detail['device_seq'] = model_info['device_seq']
            model_spec_info.append(model_spec_detail)
            crawling_urls.at[device_index, 'brand_name'] = model_spec_detail['brand_name']
            break
        else :
            print(f"{model_info['device_link']} rslt retry : {spec_success}, {model_spec_detail}")
            time.sleep(5)

    print(f"Crawling Count : {device_index}")

    time.sleep(20)

# 크롤링 한 원천 결과 파일 저장
print(spec_src_json_file_name, f"model count {len(model_spec_info)}")
with open(spec_src_json_file_name, 'w') as jf:
    json.dump(model_spec_info, jf, indent=4)