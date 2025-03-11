import pandas as pd
import json

file_nm = 'kimovil_Exynos2400_spec_info'
json_file = rf"C:\work\mywork\examples\crawling\json\{file_nm}.json"
with open(json_file, 'r', encoding='utf-8') as file :
    data = json.load(file)
    
df = pd.DataFrame(data)

excel_file = f"{file_nm}.xlsx"
df.to_excel(excel_file)

print(f"data has been saved to {excel_file}")



