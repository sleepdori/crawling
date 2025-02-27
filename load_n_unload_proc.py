import sys
import pandas as pd
import xlwings as xw
import numpy as np
import re
import json
import traceback
from dbutil.oracle_db_manager import OracleDBManager
from dbutil.postgresql_db_manager import PostgreSQLManager
from dbutil.excel_reader import ExcelReader
from dbutil.excel_app_reader import ExcelAppReader
from common.config_loader import ConfigLoader
from common.print_to_logger import PrintToLogger
from cipher.crypto_util import CryptoUtil
import ace_tools_open as tools
from util.myutil import read_json, read_csv_file, utf8_length, clean_column_names, strip_whitespace, replace_nan_in_dict

# 옵션 설정: 출력할 최대 행 개수를 None으로 설정 (제한 없음)
pd.set_option('display.max_rows', None)  # 모든 행 출력
pd.set_option('display.max_columns', None)  # 모든 열 출력
pd.set_option('display.width', 1000)       # 출력 화면 폭 설정

config = ConfigLoader()

path_separator = config.get_path_separator()
project_home = config.get("project_home")
log_dir = f'{config.get("project_home")}{path_separator}{config.get("log_dir")}'

logfile = config.get("logfile")
logLevel = config.get("logLevel")
logformat = config.get("logformat")

print(project_home, path_separator, log_dir, logfile, logLevel, logformat)
sys.stdout = PrintToLogger(log_dir=log_dir, log_file_prefix=logfile, loglevel=logLevel)

use_connection_nm = config.get("excel_load", "use_connection_nm")
load_database_type = config.get("excel_load", "load_database_type")

load_list_sql = config.get("excel_load", use_connection_nm, "load_list_sql")
load_map_sql  = config.get("excel_load", use_connection_nm, "load_map_sql")

key_file_path = f"{project_home}{path_separator}{config.get('key_file_path')}"
key_file_name = config.get('key_file_name')

print(key_file_path, key_file_name)

crypto = CryptoUtil(key_file_path, key_file_name)

HOST = config.get("databases", use_connection_nm, "host")
PORT = config.get("databases", use_connection_nm, "port")
DATABASE = config.get("databases", use_connection_nm, "database")
DSN = f'{HOST}:{PORT}/{DATABASE}'
DB_USER = crypto.decrypt(config.get("databases", use_connection_nm, "user"))
DB_PASS = crypto.decrypt(config.get("databases", use_connection_nm, "password"))

print(DSN, DB_USER, DB_PASS)

db_mgr = None

if load_database_type.lower() == 'oracle' :
    db_mgr = OracleDBManager(DB_USER, DB_PASS, DSN)
elif load_database_type.lower() == 'postgresql' :
    db_mgr = PostgreSQLManager(DB_USER, DB_PASS, HOST, PORT, DATABASE)

load_n_unload_map = config.get("excel_load", "map_file")

print(load_n_unload_map)
load_n_unload_map_file = f'{config.get("project_home")}{path_separator}var{path_separator}{load_n_unload_map}'
print(f"load & unload process map file name : {load_n_unload_map_file}")

excel_loader = None 
map_list = []
map_info = []


def analyze_columns(dataframe, db_colunm_info, excel_column_map, re_check=False):
    results = []
    
    misMatch_column = []
    misMatch_scale = []
    
    for column in dataframe.columns:
        dtype = dataframe[column].dtype
        # print(f"{column} : {dtype}")
        max_length = None
        decimal_places = None
        oracle_column_type = None
        excel_column_nm = ""

        for excel_column in excel_column_map :
            if column.strip().upper() == excel_column['VAL_NM'].strip().upper() :
                excel_column_nm = excel_column['COL_NM'].strip().upper()
                break
        is_date = False
        if dtype == object and not dataframe[column].empty:
            # 샘플 데이터로 날짜 형식 확인
            try:
                sample = dataframe[column].dropna().iloc[0]
                if isinstance(sample, str):
                    pd.to_datetime(sample)
                    is_date = True
            except (ValueError, IndexError, TypeError):
                is_date = False

        if is_date or pd.api.types.is_datetime64_any_dtype(dtype):
            # 날짜/시간 타입인 경우
            oracle_column_type = "TIMESTAMP"
            if db_type in ["TIMESTAMP", "DATE"]:
                # DB가 날짜 타입이면 데이터프레임도 datetime으로 변환
                try:
                    dataframe[column] = pd.to_datetime(dataframe[column])
                except Exception as e:
                    print(f"Column {column} 날짜 변환 실패: {e}")

        if dtype == object:  # 문자열
            max_length = dataframe[column].dropna().apply(utf8_length).max()
            oracle_column_type = f"VARCHAR2({max_length} CHAR)" if max_length else "VARCHAR2(1 CHAR)"
            dataframe[column] = dataframe[column].astype(str) 
        elif np.issubdtype(dtype, np.number):  # 숫자
            max_length = dataframe[column].dropna().apply(lambda x: len(str(int(x))) if not np.isnan(x) else 0).max()
            if dataframe[column].dtype == float:
                decimal_places = dataframe[column].dropna().apply(
                    lambda x: len(str(x).split(".")[1]) if "." in str(x) else 0
                ).max()
            oracle_column_type = f"NUMBER({max_length + (decimal_places or 0)}, {decimal_places or 0})"
        else:
            oracle_column_type = "UNKNOWN"
        
        db_type =""
        db_length = 0
        db_scale = 0
        for d in db_colunm_info :
            # print(d[1], d[2], d[3], d[4])
            if d['COLUMN_NAME'] == excel_column_nm.upper().strip() :
                db_type = d['DATA_TYPE']
                db_length = d['DATA_LENGTH']    
                db_scale = d['DATA_SCALE']  
                break          
        
        if db_type == "NUMBER" and dtype.name == "object" :
            misMatch_column.append(column)
            misMatch_scale.append(db_scale)

        results.append({
            'Column': column,
            'Data Type': dtype.name,
            'DB Col Type' : db_type, 
            'Max Length (UTF-8)': max_length,
            'DB Col Length': db_length, 
            'Decimal Places': decimal_places,
            'DB Scale':db_scale,
            'The column size of the table needs to be increased.': ('Y' if max_length > db_length else 'N'),
            'Oracle Column Type': oracle_column_type
        })   

    if re_check == False :
        if len(misMatch_column) > 0 :

            print(f"액셀 데이터 타입과 Database Table 컬럼의 데이터 타입이 일치 하지 않습니다. 불일치 컬럼 : {len(misMatch_column)}, {misMatch_column}, {misMatch_scale}")

            for miss, scale in zip(misMatch_column, misMatch_scale) :
                print(f"불일치 컬럼 : {miss} 에 대한 캐스팅 작업을 진행합니다. : {dataframe[miss].dtype}, {scale}")
                
                dataframe[miss] = pd.to_numeric(dataframe[miss], errors='coerce')
                if scale > 0 :
                    dataframe[miss] = dataframe[miss].astype(float)    
                if pd.isna(scale) :
                    dataframe[miss] = dataframe[miss].astype(int)
                    
                print(f"불일치 컬럼 : {miss} 에 대한 캐스팅 작업을 완료했습니다. : : 변경된 타입 : {dataframe[miss].dtype}")
    
    return pd.DataFrame(results), dataframe

print(f"Script name : {sys.argv[0]}")

def get_target_info(db_mgr, tbl_nm) :
    sql = load_list_sql.format(tbl_nm)
    print(sql)
    db_mgr.check_connection()
    list = db_mgr.select(sql)
    list_df = pd.DataFrame(list).to_dict(orient='records')
    print(list_df)

    print(load_map_sql)
    map = db_mgr.select(load_map_sql)
    map_df = pd.DataFrame(map).groupby("TBL_NM")
    print(map_df)
    return list_df, map_df

# 전달받은 인수를 출력
tgt_tbl_nm = ''
base_map_src = 'EXCEL'
if len(sys.argv) > 1:
    tgt_tbl_nm = sys.argv[1]
    print(f"테이블명 : {tgt_tbl_nm}")  
else:
    print("로드 대상 테이블명을 입력하세요!")

if len(sys.argv) > 2:
    base_map_src = sys.argv[2]
    print(f"로드 맵 기준 : {base_map_src}") 

try :
    excel_loader = ExcelAppReader(load_n_unload_map_file, DRM=True)
    map_list = excel_loader.load_sheet(sheet_name = 'LIST', start_position='A1').to_dict(orient='records')
    map_info = excel_loader.load_sheet(sheet_name = 'MAP_INFO', start_position='A1').groupby("TBL_NM")

    if base_map_src != 'EXCEL' :
        map_list, map_info = get_target_info(db_mgr, tgt_tbl_nm)

    try:
        excel_loader.unload_app()
    except:
        pass

    m_idx = 1
    for m_list in map_list :
        load_result = True
        load_result_message = ""
        condition = m_list.get('COND_DTL')
        execute_type = m_list.get('EXEC_TYPE')
        source_gubun = m_list.get('SOURCE_TYPE')
        schema_nm = m_list.get('SCHM_NM')
        tbl_nm = m_list.get('TBL_NM')
        melt_yn = m_list.get('MELT_YN')
        read_type = m_list.get('READ_TYPE')
        drm_yn = m_list.get('DRM_YN')
        excel_encoding = m_list.get('ENCD_TYPE')

        if condition == None or condition.strip() == "" : 
            condition = "NONE"

        if tgt_tbl_nm.upper() == tbl_nm.strip().upper() :
            if drm_yn == "Y" :
                drm = True
            else : 
                drm = False

            column_map = map_info.get_group(tbl_nm).to_dict(orient='records')

            # DB 카탈로그 정보에서 테이블에 컬럼 정보를 추출
            db_colunm_info = db_mgr.columns_info(schema_name=schema_nm, table_name=tbl_nm)
            
            # Excel 매핑된 컬럼 명이 DB에 컬럼명과 일치하는지 확인
            for excel_column in column_map :
                if excel_column['MELT_YN'] == 'N' :
                    exists_column = any(d['COLUMN_NAME'].upper() == excel_column['COL_NM'].upper() for d in db_colunm_info )
                    if exists_column == False :
                        load_result = False 
                        load_result_message = f"The column name [{excel_column['COL_NM'].upper()}] registered in the Excel map does not exist in the database table {tbl_nm}."
                        break

            column_list = []
            value_list = []
            change_type_col_list = []
            change_type_to_type = []
            melt_id_var = []
            melt_list = []
            column_str = ""
            value_str = ""
            idx = 0

            for excel_column in column_map :
                if excel_column['CHNG_TYPE'] != '-' :
                    change_type_col_list.append(excel_column['VAL_NM'])
                    change_type_to_type.append(excel_column['CHNG_TYPE'])

                if excel_column['MELT_YN'] == 'N' :
                    column_list.append(excel_column['COL_NM'])
                    value_list.append(excel_column['VAL_NM']) 
                    if excel_column['VAL_NM'] != 'key_word' and excel_column['VAL_NM'] != 'value' :
                        melt_id_var.append(excel_column['VAL_NM']) 

                    if idx == 0 :
                        column_str = excel_column['COL_NM']
                        value_str = ":"+ re.sub(r'\W+&-/()$. ', '_', excel_column['VAL_NM'].strip())
                    else :
                        column_str = column_str + ", " + excel_column['COL_NM']
                        value_str = value_str + ", :"+ re.sub(r'[^\w]+', '_', excel_column['VAL_NM'].strip())
                    idx += 1
                    # print(value_str)
                else :
                    melt_list.append(excel_column['VAL_NM'])
                    

            if ( execute_type.upper() == 'INITIAL_LOAD' or execute_type.upper() == 'APPEND_LOAD' ) and source_gubun.upper() in ('EXCEL', 'CSV'):
                try :
                    print(f"'{tbl_nm}' 테이블 '{m_list.get('FILE_NM')}' 에 '{m_list.get('SHEET_NM')}' Sheet Data {execute_type} 작업")
                    
                           
                    # Excel 의 컬럼명과 DB에 컬럼명이 일치할 경우만 실행
                    if exists_column :

                        #Excel 파일에 데이터를 읽어 온다.
                        load_excel_nm = m_list.get('FILE_NM')
                        load_excel_sheet_nm = m_list.get('SHEET_NM')
                        load_excel_sheet_position = m_list.get('STRT_PSTN')
                         
                        print(f"load excel file name = {load_excel_nm}, sheet = {load_excel_sheet_nm}, start position = {load_excel_sheet_position} excel data load start!!")
                        
                        if source_gubun.upper() == 'EXCEL' :
                            if drm : 
                                load_excel_loader = ExcelAppReader(load_excel_nm, DRM=drm)
                                df = load_excel_loader.load_sheet(sheet_name = load_excel_sheet_nm, start_position=load_excel_sheet_position, dtype=read_type)
                                print(f"load excel file name = {load_excel_nm}, sheet = {load_excel_sheet_nm}, start position = {load_excel_sheet_position} excel data load !!")
                                try:
                                    load_excel_loader.unload_app()
                                except:
                                    load_result = False 
                                    load_result_message = f"An error occurred while reading data from the Excel file '{load_excel_nm}'."     
                            else :
                                excel_reader = ExcelReader(load_excel_nm, load_excel_sheet_nm, load_excel_sheet_position)
                                load_result, df = excel_reader.read_to_sheet()
                            
                        elif source_gubun.upper() == 'CSV' :
                            df = read_csv_file( load_excel_nm, encoding=excel_encoding)     

                        #행렬 전환이 있는 경우
                        if melt_yn == 'Y' :
                            print("행렬전환 대상 데이터 입니다. 행렬전환을 시작합니다.")    
                            df = pd.melt(
                                df,
                                id_vars=melt_id_var,  # ID 컬럼 고정
                                value_vars=melt_list,
                                var_name="key_word",
                                value_name="value",
                            )
                            print("행렬전환을 완료했습니다.") 
                            df['key_word'] = df['key_word'].str.replace('_', '-').apply(convert_date_format)
                            
                        print(f"저장할 대상 컬럼을 추출합니다. {value_list}, {df.columns}, {column_list}") 
                        df_select = df[value_list]

                        if len(change_type_col_list) > 0 :
                            c_idx = 0
                            for change_col in change_type_col_list :
                                
                                if change_type_to_type[c_idx] == 'YM_NS' :
                                    try :
                                        df_select[change_col] = df_select[change_col].apply(convert_date_format)
                                    except Exception as ve:
                                        df_select[change_col] = df_select[change_col].apply(validate_and_convert)

                                c_idx += 1

                        # 데이터프레임의 모든 값에서 공백 제거
                        print("액셀 데이터에서 Cell 값의 앞뒤 공백을 제거합니다.")

                        # df_select = df_select.applymap(strip_whitespace)
                        df_select = df_select.apply(lambda col: col.map(strip_whitespace))

                        print("액셀 데이터에서 Cell 값의 앞뒤 공백을 제거를 완료했습니다..")
                        # 데이터의 컬럼 타입, 사이즈, 수점자리수 조사
                        print("액셀 데이터에서 컬럼의 타입, 컬럼의 길이, 소숫점 이하 자리수를 조사합니다.")
                        
                        column_analysis , df_select = analyze_columns(df_select, db_colunm_info, column_map)

                        print("액셀 데이터에서 컬럼의 타입, 컬럼의 길이, 소숫점 이하 자리수를 조사 완료했습니다. 출력합니다.")

                        tools.display_dataframe_to_user(name="Column Analysis", dataframe=column_analysis)

                        print("출력했습니다.")
                        print("액셀 인스턴스를 종료합니다.")
                        
                        if load_result and execute_type.upper() == 'INITIAL_LOAD':
                            print("INITIAL_LOAD 를 위하여 테이블의 초기화 작업을 진행합니다.")
                            del_sql = f"truncate table {schema_nm}.{tbl_nm}"
                            print(del_sql)
                            del_success = db_mgr.delete(del_sql)

                            if del_success == False :
                                load_result = False 
                                load_result_message = f"An error occurred while initializing the {tbl_nm} table."
                            print("INITIAL_LOAD 를 위하여 테이블의 초기화 작업을 완료했습니다.")
                        else :
                            if condition != "NONE" and condition != '' and condition != 'None':
                                print("액셀 데이터 APPEND 를 위하여 테이블의 데이터를 삭제조건에 맞는 데이터를 삭제합니다.")
                                del_sql = f"delete from {schema_nm}.{tbl_nm} where {condition}"
                                print(del_sql)
                                del_success = db_mgr.delete(del_sql)

                                if del_success == False :
                                    load_result = False 
                                    load_result_message = f"An error occurred while initializing the {tbl_nm} table."  
                                print("액셀 데이터 APPEND 를 위하여 테이블의 데이터를 삭제조건에 맞는 데이터의 삭제를 완료 했습니다..")

                        if load_result :

                            query = f"insert into {schema_nm}.{tbl_nm} ( {column_str}) values ( {value_str} )"
                            print(f"액셀 데이터 적재 SQL : {query}")
                            print("액셀 데이터 적재를 시작합니다.")
                            df_select = clean_column_names(df_select)
                            
                            load_result = db_mgr.load(replace_nan_in_dict(df_select.to_dict(orient='records')), query)

                            if load_result :
                                load_result = True 
                                load_result_message = f"Data from the Excel file '{load_excel_nm}' has been successfully loaded into the {tbl_nm} table."
                                print(f"액셀 데이터 적재를 완료했습니다. {load_result}")
                            else :
                                load_result = False 
                                load_result_message = f"Failed to load data from the Excel file '{load_excel_nm}' into the {tbl_nm} table."
                                print("액셀 데이터 적재중 에러가 발생했습니다.")
                            
                except FileNotFoundError:
                    load_result = False 
                    load_result_message = f"Error: File '{load_excel_nm}' was not found."
                except PermissionError:
                    load_result = False 
                    load_result_message = f"Error: Permission denied to access '{load_excel_nm}'. The file might be open in another program."
                except ValueError as vee:
                    load_result = False 
                    load_result_message = f"ValueError {str(vee)}"
                except Exception as ee:
                    load_result = False 
                    load_result_message = f"An unexpected error occurred: {str(ee)} "
            elif execute_type.upper() == 'JSON_LOAD' :
                df = read_json(m_list.get('FILE_NM'), read_type="str")
                if df is None :
                    exit(1)
                else :

                    print(f"JSON 파일에서 액셀에 매핑된 컬럼만 가져옵니다. {df.columns}")
                    df_select = df[value_list]        
                    print("JSON 파일에서 액셀에 매핑된 컬럼만 가져왔습니다..")

                    # 데이터프레임의 모든 값에서 공백 제거
                    print("액셀 데이터에서 Cell 값의 앞뒤 공백을 제거합니다.")

                    df_select = df_select.applymap(strip_whitespace)

                    print("액셀 데이터에서 Cell 값의 앞뒤 공백을 제거를 완료했습니다..")
                    # 데이터의 컬럼 타입, 사이즈, 수점자리수 조사
                    print("액셀 데이터에서 컬럼의 타입, 컬럼의 길이, 소숫점 이하 자리수를 조사합니다.")
                    
                    column_analysis , df = analyze_columns(df_select, db_colunm_info, column_map)

                    print("액셀 데이터에서 컬럼의 타입, 컬럼의 길이, 소숫점 이하 자리수를 조사 완료했습니다. 출력합니다.")

                    tools.display_dataframe_to_user(name="Column Analysis", dataframe=column_analysis)

                    print("출력했습니다.")
                    df_select = clean_column_names(df_select)

                    query = f"insert into {schema_nm}.{tbl_nm} ( {column_str}) values ( {value_str} )"
                    print(f"액셀 데이터 적재 SQL : {query}")
                    print("액셀 데이터 적재를 시작합니다.")

                    load_result = db_mgr.load(replace_nan_in_dict(df_select.to_dict(orient='records')), query)

                    if load_result :
                        load_result = True 
                        load_result_message = f"Data from the JSON file '{m_list.get('FILE_NM')}' has been successfully loaded into the {tbl_nm} table."
                        print("JSON 데이터 적재를 완료했습니다.")
                    else :
                        load_result = False 
                        load_result_message = f"Failed to load data from the Excel file '{m_list.get('FILE_NM')}' into the {tbl_nm} table."
                        print("JSON 데이터 적재를 완료했습니다.")

            elif execute_type.upper() == 'JSON_DOWNLOAD' or execute_type.upper() == 'EXCEL_DOWNLOAD' :
                print(f"'{tbl_nm}' 테이블 '{m_list.get('FILE_NM')}' 에 {execute_type} 작업")

                query = "select "
                columns = []
                idx = 0
                for excel_column in column_map :
                    if idx == 0 :
                        query = query + excel_column['COL_NM'] + " AS " + excel_column['VAL_NM']
                    else :
                        query = query + ", " + excel_column['COL_NM'] + " AS " + excel_column['VAL_NM']
                    columns.append(excel_column['COL_NM'])
                    idx += 1  
                query = query + " from " + tbl_nm
                if condition != "NONE" :
                    query = query + " where "  + condition  

                result = db_mgr.select(query)

                if result != None and len(result) > 0 :

                    if execute_type.upper() == 'JSON_DOWNLOAD' :
                        df = pd.DataFrame(result, columns=columns)
                        result_df = df.to_dict(orient='records')
                        json_file_name = m_list.get('FILE_NM')

                        with open(json_file_name, 'w') as select_result_json_file:
                            json.dump(result_df, select_result_json_file, indent=4)
                    else :
                        result_df = pd.DataFrame(result, columns=columns) 
                        excel_file = m_list.get('FILE_NM')  # 저장할 Excel 파일 경로
                        sheet_nm = m_list.get('SHEET_NM')
                        if sheet_nm == None or sheet_nm.strip() == '' :
                            sheet_nm = "RESULT"

                        with xw.App(visible=False) as app:      # Excel 애플리케이션을 숨긴 상태로 실행
                            wb = app.books.add()                # 새로운 워크북 생성
                            sheet = wb.sheets.add(sheet_nm)     # 'result' 시트 추가
                            sheet.range('A1').value = result_df.columns.tolist()  # 컬럼 이름 작성
                            sheet.range('A2').value = result_df.values.tolist()  # 데이터 작성
                            wb.save(excel_file)  # Excel 파일 저장
                            print(f"Data saved to {excel_file} in the 'result' sheet.")
                            wb.close()
            else :
                print("미 분류 작업")

            if load_result == False :
                print(load_result_message)
            else :
                print(load_result_message)

            m_idx += 1

except FileNotFoundError:
    print(f"Error: File '{load_n_unload_map_file}' was not found.")
except PermissionError:
    print(f"Error: Permission denied to access '{load_n_unload_map_file}'. The file might be open in another program.")
except ValueError as ve:
    print(f"ValueError:{str(ve)}")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
    traceback.print_exc()




