import requests
import json
import base64
import time
from bs4 import BeautifulSoup
import re

def get_response(url):

    data = {
        "url": f"{url}",
        "httpResponseBody": True
    }

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': 'fa43d9f7-ec8c-4ef5-a6b6-afba22c7a5fd'
    }

    response = requests.post('https://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request', headers=headers, json=data)

    if response.status_code == 200:
        return True, response
    else:
        return False, f"Error: {response.status_code}"
    
def gamarena_sp_list(output_file_nm) :
    
    brand_list_urls = [
             {'BRAND' : 'APPLE', 'device_link': 'https://www.gsmarena.com/apple-phones-f-48-0-p{}.php'}
           , {'BRAND' : 'SAMSUNG', 'device_link' : 'https://www.gsmarena.com/samsung-phones-f-9-0-p{}.php' }
           , {'BRAND' : 'HUAWEI', 'device_link' : 'https://www.gsmarena.com/huawei-phones-f-58-0-p{}.php'}
           , {'BRAND' : 'NOKIA', 'device_link' : 'https://www.gsmarena.com/nokia-phones-f-1-0-p{}.php'}
           , {'BRAND' : 'SONY', 'device_link' : 'https://www.gsmarena.com/sony-phones-f-7-0-p{}.php'}
           , {'BRAND' : 'LG', 'device_link' : 'https://www.gsmarena.com/lg-phones-f-20-0-p{}.php'}
           , {'BRAND' : 'HTC', 'device_link' : 'https://www.gsmarena.com/htc-phones-f-45-0-p{}.php'}
           , {'BRAND' : 'MOTOROLA', 'device_link' : 'https://www.gsmarena.com/motorola-phones-f-4-0-p{}.php'}
           , {'BRAND' : 'LENOVO', 'device_link' : 'https://www.gsmarena.com/lenovo-phones-f-73-0-p{}.php'}
           , {'BRAND' : 'XIAOMI', 'device_link' : 'https://www.gsmarena.com/xiaomi-phones-f-80-0-p{}.php'}
           , {'BRAND' : 'GOOGLE', 'device_link' : 'https://www.gsmarena.com/google-phones-f-107-0-p{}.php'}
           , {'BRAND' : 'HONOR', 'device_link' : 'https://www.gsmarena.com/honor-phones-f-121-0-p{}.php'}
           , {'BRAND' : 'OPPO', 'device_link' : 'https://www.gsmarena.com/oppo-phones-f-82-0-p{}.php'}
           , {'BRAND' : 'REALME', 'device_link' : 'https://www.gsmarena.com/realme-phones-f-118-0-p{}.php'}
           , {'BRAND' : 'ONEPLUS', 'device_link' : 'https://www.gsmarena.com/oneplus-phones-f-95-0-p{}.php'}
           , {'BRAND' : 'NOTHING', 'device_link' : 'https://www.gsmarena.com/nothing-phones-f-128-0-p{}.php'}
           , {'BRAND' : 'VIVO', 'device_link' : 'https://www.gsmarena.com/vivo-phones-f-98-0-p{}.php'}
           , {'BRAND' : 'MEIZU', 'device_link' : 'https://www.gsmarena.com/meizu-phones-f-74-0-p{}.php'}
           , {'BRAND' : 'ASUS', 'device_link' : 'https://www.gsmarena.com/asus-phones-f-46-0-p{}.php'}
           , {'BRAND' : 'ALCATEL', 'device_link' : 'https://www.gsmarena.com/alcatel-phones-f-5-0-p{}.php'}
           , {'BRAND' : 'ZTE', 'device_link' : 'https://www.gsmarena.com/zte-phones-f-62-0-p{}.php'}
           , {'BRAND' : 'MICROSOFT', 'device_link' : 'https://www.gsmarena.com/microsoft-phones-f-64-0-p{}.php'}
           , {'BRAND' : 'UMIDIGI', 'device_link' : 'https://www.gsmarena.com/umidigi-phones-f-135-0-p{}.php'}
           , {'BRAND' : 'COOLPAD', 'device_link' : 'https://www.gsmarena.com/coolpad-phones-f-105-0-p{}.php'}
           , {'BRAND' : 'CAT', 'device_link' : 'https://www.gsmarena.com/cat-phones-f-89-0-p{}.php'}
           , {'BRAND' : 'SHARP', 'device_link' : 'https://www.gsmarena.com/sharp-phones-f-23-0-p{}.php'}
           , {'BRAND' : 'MICROMAX', 'device_link' : 'https://www.gsmarena.com/micromax-phones-f-66-0-p{}.php'}
           , {'BRAND' : 'INFINIX', 'device_link' : 'https://www.gsmarena.com/infinix-phones-f-119-0-p{}.php'}
           , {'BRAND' : 'ULEFONE', 'device_link' : 'https://www.gsmarena.com/ulefone-phones-f-124-0-p{}.php'}
           , {'BRAND' : 'TECNO', 'device_link' : 'https://www.gsmarena.com/tecno-phones-f-120-0-p{}.php'}
           , {'BRAND' : 'DOOGEE', 'device_link' : 'https://www.gsmarena.com/doogee-phones-f-129-0-p{}.php'}
           , {'BRAND' : 'BLACKVIEW', 'device_link' : 'https://www.gsmarena.com/blackview-phones-f-116-0-p{}.php'}
           , {'BRAND' : 'CUBOT', 'device_link' : 'https://www.gsmarena.com/cubot-phones-f-130-0-p{}.php'}
           , {'BRAND' : 'OUKITEL', 'device_link' : 'https://www.gsmarena.com/oukitel-phones-f-132-0-p{}.php'}
           , {'BRAND' : 'ITEL', 'device_link' : 'https://www.gsmarena.com/itel-phones-f-131-0-p{}.php'}
           , {'BRAND' : 'TCL', 'device_link' : 'https://www.gsmarena.com/tcl-phones-f-123-0-p{}.php'}
        ]
    
    all_links = []    

    for brand_info in brand_list_urls :
    
        brand_name = brand_info['BRAND']
        base_url = brand_info['device_link']
        
        page_count = 1
        output_file = output_file_nm

        
        while True :
            url = base_url.format(page_count)
            print(f"[INFO] GAMAREAN web page request : {url}")
            
            # response = requests.get(url)
            succ, response = get_response(url)
            if succ == False :
                print(succ, response)
                time.sleep(5)
                continue

            json_response = response.json()
            
            if 'browserHtml' in json_response['data']:
                html_content = json_response['data']['browserHtml']
            else:
                html_content = base64.b64decode(json_response['data']['httpResponseBody']).decode()      
    
            if response.status_code == 200 :
                print(f"[INFO] web page {page_count} load OK !!")
                # soup = BeautifulSoup(response.text, "html.parser")
                soup = BeautifulSoup(html_content, "html.parser")
                
                ul_element = soup.find("div", class_="makers")
                li_elements = ul_element.find_all("li") if ul_element else []
                
                if li_elements :
                    for li_tag in li_elements :
                        link_tag = li_tag.find('a')
                        device_link = link_tag['href'].strip() if link_tag else ""
                        if device_link != '' :
                            device_link = f"https://www.gsmarena.com/{device_link}"
                            
                        span_tag = link_tag.find('span')
                        texts = span_tag.decode_contents().split('<br/>')
                        texts = [text.strip() for text in texts]
                        
                        device_name = texts[0]
                        
                        if device_name != '' :
                            device_info = {
                                'brand_name' : brand_name ,
                                'device_name' : device_name , 
                                'device_link' : device_link
                            }
                        
                        all_links.append(device_info)
                            
                else :
                    print(f"[INFO] 페이지 {page_count} 에  이상 데이터가 없습니다.  작업을 종료합니다 {html_content}")
                    break
            else :
                print(f"[ERROR] page {page_count} 로드 실패, 상태코드 : {response.status_code}, {response}")
                break
                
            print(f"[INFO] page {page_count} crawling finish! ")
            
            print(f"[INFO] total {len(all_links)} 개의 장치 정보를 저장합니다.")
            with open(output_file, 'w', encoding='utf-8') as f :
                json.dump(all_links, f, ensure_ascii=False, indent=4)
                
            time.sleep(5)
            page_count += 1
            
            
        print(f"[INFO] 모든 링크 정보가 { output_file} 에 저장되었습니다. {all_links}")
        
