
import os
import datetime
import re
import json
import pandas as pd
import numpy as np

def get_path_separator():
    # 운영체제를 파악하여 디렉토리 구분자를 반환
    return os.path.sep

def utf8_length(value):
    if isinstance(value, str):
        # UTF-8에서 각 문자의 바이트 길이 계산
        return sum(1 + (ord(char) > 127) + (ord(char) > 2047) for char in value)
    return 0

def read_json(json_file, read_type=None):
    if not os.path.exists(json_file):
        print(f"File not found: {json_file}")
        return None
    data = []
    try:
        # JSON 읽기 시도
        with open(json_file, "r", encoding="utf-8") as f:
            all_links = json.load(f)  

        df = pd.DataFrame(all_links)
        if read_type != None :
            df = df.astype(str)

        return df
    except Exception as e:
        print(f"An unexpected error occurred while reading {json_file}: {e}")
        raise

# csv 파일을 읽고 DataFrame 반환하는 함수
def read_csv_file(file_path, encoding=None):
    # csv 파일을 읽기 위한 Pandas 함수
    try:
        # 만약 인코딩이 지정되어 있으면 CSV로 처리하고, 엑셀 파일이면 인코딩 없이 처리
        if file_path.endswith('.csv'):
            # CSV 파일일 경우, encoding을 지정해서 읽음
            if encoding is None:
                encoding = 'cp949'  # 기본적으로 CP949를 사용
            df = pd.read_csv(file_path, encoding=encoding)
        else:
            # 엑셀 파일일 경우, 인코딩을 신경쓸 필요가 없음
            df = pd.read_excel(file_path)
        
        return df
    
    except Exception as e:
        print(f"파일 읽기 중 오류 발생: {e}")
        return None    
    
def replace_nan_in_dict(data):
   
    for record in data:
        for key, value in record.items():
            if pd.isna(value) :  # NaN 값 확인
                record[key] = None  # NaN을 None으로 변경
            else :
                dtype = type(value)
                if np.issubdtype(dtype, np.number) : 
                    try:
                        pd.to_numeric(value, errors='raise')  # 변환 시도
                    except ValueError:
                        print(f"key = {key}, value = {value}")
                        record[key] = None    

    return data

def utf8_length(value):
    if isinstance(value, str):
        # UTF-8에서 각 문자의 바이트 길이 계산
        return sum(1 + (ord(char) > 127) + (ord(char) > 2047) for char in value)
    return 0    

# 공백 제거 함수
def strip_whitespace(value):
    if isinstance(value, str):
        return value.strip()  # 문자열의 앞뒤 공백 제거
    return value

def clean_column_names(df):
    """
    데이터프레임의 컬럼명을 정리:
    - 공백을 밑줄(_)로 대체
    - 영숫자가 아닌 문자를 제거
    - 첫 글자가 숫자인 경우 앞에 'a'를 추가
    """
    cleaned_columns = []
    for col in df.columns:
        # 공백 및 특수문자 제거, 밑줄로 대체
        clean_col = re.sub(r'[^\w]+', '_', col.strip())
        # 첫 글자가 숫자인 경우 앞에 'a' 추가
        if clean_col and clean_col[0].isdigit():
            clean_col = f'a{clean_col}'
        cleaned_columns.append(clean_col)
    
    df.columns = cleaned_columns
    return df

def convert_date_format(date_str):
    try:
        # 입력 문자열을 datetime 객체로 변환
        date_object = datetime.datetime.strptime(date_str, "%b-%y")
        # 원하는 형식으로 변환
        return date_object.strftime("%Y%m")
    except ValueError:
        # 변환 중 에러가 발생하면 원래 데이터를 반환
        return date_str

# 컬럼 값이 특정 형태인지 확인하는 함수
def validate_and_convert(date_str):
    try:
        # datetime 형태로 변환 시도
        date = pd.to_datetime(date_str, format='%Y-%m-%d %H:%M:%S')
        # 'YYYYMM' 형태로 변환
        return date.strftime('%Y%m')
    except ValueError:
        # 변환 실패 시 None 반환
        return date_str

