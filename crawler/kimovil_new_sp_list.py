import cloudscraper
import requests
import json
import time
from bs4 import BeautifulSoup
import re
import base64

def get_response(url):
    data = {
        "url": f"{url}",
        "httpResponseBody": True
    }

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': '5a860887-0729-4600-84eb-8be3d1217fb5'
    }

    response = requests.post('https://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request', headers=headers, json=data)

    if response.status_code == 200:
        return True, response
    else:
        return False, f"Error: {response.status_code}"  
        
def crawling_new_sp_list(output_file_nm) :
    proxies = {
        'http': 'http://12.26.204.100:8080',
        'https': 'http://12.26.204.100:8080'
    }
    # Cloudflare 보안 우회를 위한 CloudScraper 생성
    scraper = cloudscraper.create_scraper()

    # 크롤링 대상 URL
    base_url = "https://www.kimovil.com/en/compare-smartphones/order.dm+unveiledDate,i_m+code.Global:Intern:Americ:NA:Latam:BR:CN:IN:Sudasi:KR:JP,page.{}"
    page_count = 1
    output_file = output_file_nm
    all_links = []  # 모든 페이지의 링크 정보를 저장할 딕셔너리
    new_list_finish = False
    sp_no_seq = 1

    while True:
        url = base_url.format(page_count)
        print(f"[INFO] 페이지 호출 중: {url}")

        # 요청 보내기
        request_success, response = get_response(url)
        # response = scraper.get(url, proxies=proxies)
        # response = scraper.get(url)

        # 응답 확인
        if request_success and response.status_code == 200:
            print(f"[INFO] 페이지 {page_count} 로드 성공")
            # BeautifulSoup으로 HTML 파싱
            json_response = response.json()

            if 'browserHtml' in json_response['data']:
                html_content = json_response['data']['browserHtml']
            else:
                # html_content = base64.b64decode(json_response['data']['httpResponseBody']).decode()               
                html_content = base64.b64decode(json_response['data']['httpResponseBody'], validate=True).decode('utf-8', errors='ignore')  

            soup = BeautifulSoup(html_content, "html.parser")

            # soup = BeautifulSoup(response.text, "html.parser")

            ul_element = soup.find("ul", id="results-list")
            li_elements = ul_element.find_all("li", id=re.compile(r"^kiid_")) if ul_element else []

            if li_elements:
                for li_tag in li_elements:
                    item_tag = li_tag.find('div', class_='item-wrap')
                    if item_tag:
                        link_tag = item_tag.find('a', class_='device-link')
                        device_link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "Unknown"
                        if device_link == "Unknown" :
                            encoded_url = link_tag['data-kdecode']
                            device_link = base64.b64decode(encoded_url).decode('utf-8')

                        name_div_tag = link_tag.find('div', class_='device-name') if link_tag else None
                        if name_div_tag:
                            name_tag = name_div_tag.find('div', class_='title')
                            device_name = name_tag.text.strip() if name_tag else "Unknown"

                            version_div = name_div_tag.find("div", class_="version")
                            if version_div:
                                device_version = version_div.find("span", class_="market").text.strip() if version_div.find("span", class_="market") else "Unknown"
                                remaining_text = version_div.get_text(separator=" ", strip=True)
                                details = remaining_text.replace(device_version, "").strip().split("·")
                                device_memory_size = details[0].strip() if len(details) > 0 else "Unknown"
                                device_storage_size = details[1].strip() if len(details) > 1 else "Unknown"
                            else:
                                device_version = "Unknown"
                                device_memory_size = "Unknown"
                                device_storage_size = "Unknown"

                            device_available = ''
                            status_tag = name_div_tag.find("div", class_="status available")
                            if status_tag :
                                device_available = status_tag.get_text(strip=True).strip()
                            else :
                                status_tag = name_div_tag.find("div", class_="status new")
                                if status_tag : 
                                    device_available = "New"
                                else :
                                    status_tag = name_div_tag.find("div", class_="status rummors")
                                    if status_tag :
                                        device_available = "Rumor"
                                    else :
                                        status_tag = name_div_tag.find("div", class_="status presell")
                                        if status_tag :
                                            device_available = "Presell"
                        
                            device_info = {
                                'device_name': device_name,
                                'device_link': device_link,
                                'device_version': device_version,
                                'device_memory_size': device_memory_size,
                                'device_storage_size': device_storage_size,
                                'device_available': device_available.strip()
                            }

                            print(f'{device_name}, {device_version}, {device_memory_size}, {device_storage_size}, {device_available} - is new : {device_available != "New" and device_available != "Rumor"}')
                            if  device_available != "New" and device_available != "Rumor" and device_available != "Presell" :
                                new_list_finish = True

                        data_tag = item_tag.find('div', class_='device-data')
                        features_tag = data_tag.find('div', class_='ki-features') if data_tag else None
                        data_list_tag = features_tag.find_all('div', class_='data')
                        if data_list_tag :
                            size_info = data_list_tag[0].get_text(strip=True)
                            device_size = ""
                            device_weight = ""                        
                            if size_info.strip() != '' :
                                device_size , device_weight = size_info.split('·')
                            else :
                                device_size = "Unknown"
                                device_weight = "Unknown"
                            device_battery_power = data_list_tag[1].get_text(strip=True)
                            if device_battery_power.strip() == "" :
                                device_battery_power = "Unknown"

                            device_info['device_size'] = device_size
                            device_info['device_weight'] = device_weight  
                            device_info['device_battery_power'] = device_battery_power  
                            device_info['device_seq'] = sp_no_seq
                            device_info['media_name'] = "kimovil"
                            
                            if new_list_finish == False :
                                all_links.append(device_info)
                                sp_no_seq += 1
                                # if device_name in all_links:
                                #     all_links[device_name].append(device_info)
                                # else:
                                #     all_links[device_name] = [device_info]

            else:
                print(f"[INFO] 페이지 {page_count}에 더 이상 'kiid_' 데이터가 없습니다. 크롤링을 종료합니다.")
                break
        else:
            print(f"[ERROR] 페이지 {page_count} 로드 실패. 상태 코드: {response.status_code}, {response}")
            break

        print(f"[INFO] 페이지 {page_count} 크롤링 완료.")

        # JSON 파일로 저장
        print(f"[INFO] 총 {len(all_links)}개의 장치 정보를 저장합니다.")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_links, f, ensure_ascii=False, indent=4)    

        print(f"new continue : {new_list_finish}")
        if new_list_finish :
            break
        time.sleep(10)  # 요청 간 딜레이 추가
        page_count += 1



    print(f"[INFO] 모든 링크 정보가 {output_file}에 저장되었습니다.")
    
