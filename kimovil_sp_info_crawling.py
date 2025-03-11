import time
import json
import pandas as pd
import cloudscraper
from common.config_loader import ConfigLoader
from crawler.kimovil_sp_list import crawling_sp_list
from crawler.kimovil_sp_spec_detail import kimovil_sp_spec_detail
from util.myutil import read_json

proxies = {
    'http': 'http://12.26.204.100:8080',
    'https': 'http://12.26.204.100:8080'
}

config = ConfigLoader()

path_separator = config.get_path_separator()
project_home = config.get("project_home")
crawling_out_path = config.get("crawling", "out_path")
use_connection_nm = config.get("crawling", "use_connection_nm")
load_database_type = config.get("crawling", "load_database_type")

kimovil_sp_list_nm = config.get("crawling", "kimovil", "sp_list")
kimovil_sp_spec_nm = config.get("crawling", "kimovil", "sp_spec")
kimovil_sp_price_nm = config.get("crawling", "kimovil", "sp_price")

out_list_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{kimovil_sp_list_nm}'
out_spec_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{kimovil_sp_spec_nm}'
out_price_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{kimovil_sp_price_nm}'
spec_src_file_name = rf"{project_home}{path_separator}{crawling_out_path}{path_separator}kimovil_sp_spec_src.json"

print(f"KIMOVIL SP List 파일 : {out_list_file_nm}")
print(f"KIMOVIL SP Spec 파일 : {out_spec_file_nm}")
print(f"KIMOVIL SP Price 파일 : {out_price_file_nm}")

price_col = ['price_model1','price_regn1','price_memory1','price_storage1','p_price1','price_model2','price_regn2','price_memory2','price_storage2','p_price2','price_model3','price_regn3','price_memory3','price_storage3','p_price3','price_model4','price_regn4','price_memory4','price_storage4','p_price4','price_model5','price_regn5','price_memory5','price_storage5','p_price5','price_model6','price_regn6','price_memory6','price_storage6','p_price6','price_model7','price_regn7','price_memory7','price_storage7','p_price7','price_model8','price_regn8','price_memory8','price_storage8','p_price8','price_model9','price_regn9','price_memory9','price_storage9','p_price9','price_model10','price_regn10','price_memory10','price_storage10','p_price10','price_model11','price_regn11','price_memory11','price_storage11','p_price11' ]

GET_LIST = False
START_IDX = 0

if GET_LIST :
    crawling_sp_list(out_list_file_nm)
    START_IDX = 0

df = read_json(out_list_file_nm)
print(f"new sp list info : {len(df)}")

spec_df = []
if GET_LIST == False :
    sdf = read_json(spec_src_file_name)

    for s_index, model_spec in sdf.iterrows() :
        START_IDX = int(model_spec['device_seq'])
        spec_df.append(model_spec.to_dict())

spec_crawler = kimovil_sp_spec_detail(proxies)

print(f"START DEVICE SEQ : {START_IDX}")
for m_index, model_info in df.iterrows() :
    if m_index > START_IDX :
        print(f"no = {m_index}, device_name = {model_info['device_name']}, device_link = {model_info['device_link']}")
        spec_success, model_spec_detail = spec_crawler.runCrawling(model_info)

        if spec_success :
            df.at[m_index, 'brand_name'] = model_spec_detail['brand_name']
            model_spec_detail['device_seq'] = model_info['device_seq']
            spec_df.append(model_spec_detail)

        time.sleep(15)
        if m_index % 10 == 0 :
            print(spec_src_file_name, f"model count {len(spec_df)}")
            with open(spec_src_file_name, 'w', encoding='utf-8') as f:
                json.dump(spec_df, f, ensure_ascii=False, indent=4)

print(spec_src_file_name, f"model count {len(spec_df)}")
with open(spec_src_file_name, 'w', encoding='utf-8') as f:
    json.dump(spec_df, f, ensure_ascii=False, indent=4)

price_column_list = []
price_column_list.append('device_seq')
for col in price_col :
    price_column_list.append(col)

df = pd.DataFrame(spec_df)
# 크롤링 한 원천 결과 파일 에서 가격 정보를 제외한 스펙 정보 저장
for col in price_col :
    if col in df.columns :
        df = df.drop(columns=col)

print(out_spec_file_nm, f"model count {len(df)}")
with open(out_spec_file_nm, 'w', encoding='utf-8') as jf:
    json.dump(df.to_dict(orient='records'), jf, ensure_ascii=False, indent=4)


# 크롤링 한 원천 결과 파일 에서 가격 정보를 추출하여 정제
df = pd.DataFrame(spec_df)
valid_columns = [col for col in price_column_list if col in df.columns]

if len(valid_columns) > 2 : 
    price_df = df.loc[:, valid_columns]

    df_no_nulls = price_df.dropna(subset=['price_model1'])

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

    print(out_price_file_nm, f"model count {len(price_df)}")
    with open(out_price_file_nm, 'w', encoding='utf-8') as jf:
        json.dump(df_no_nulls.to_dict(orient='records'), jf, ensure_ascii=False, indent=4)
