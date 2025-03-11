import requests
import json
import time
import warnings
from bs4 import BeautifulSoup
import re
import base64

# SSL 경고 메시지 숨기기
warnings.simplefilter("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Scrape.do 프록시 설정
SCRAPE_DO_TOKEN = ["d635764e256a4fddb14381e5fcdeb4e97794bf28689", "be079bbf72724e4a877f36979e057b20d165b4360c9", "2c7448f542bd4555a617d17d53f2bd855250f3ad2bf"]
SCRAPE_DO_TOKEN_IDX = 0
MAX_SCRAPE_DO_TOKEN_IDX = len(SCRAPE_DO_TOKEN) - 1
SCRAPE_DO_PROXY = f"http://{SCRAPE_DO_TOKEN[SCRAPE_DO_TOKEN_IDX]}:customHeaders=false@proxy.scrape.do:8080"

def next_proxy():
    global SCRAPE_DO_TOKEN_IDX, SCRAPE_DO_PROXY

    if SCRAPE_DO_TOKEN_IDX < MAX_SCRAPE_DO_TOKEN_IDX:
        SCRAPE_DO_TOKEN_IDX += 1
        SCRAPE_DO_PROXY = f"http://{SCRAPE_DO_TOKEN[SCRAPE_DO_TOKEN_IDX]}:customHeaders=false@proxy.scrape.do:8080"
        proxies = {
            "http": SCRAPE_DO_PROXY,
            "https": SCRAPE_DO_PROXY
        }
        print(f"✅ SCRAPE_DO_TOKEN_IDX = {SCRAPE_DO_TOKEN_IDX}, 변경된 토큰: {SCRAPE_DO_TOKEN[SCRAPE_DO_TOKEN_IDX]}")
        return True, proxies  # ✅ 올바르게 (성공여부, proxies) 반환
    else:
        return False, "⚠️ 모든 토큰의 허용량을 사용했습니다. (한 달 허용량: 3000 Call)"

# Kimovil 크롤링 함수 (프록시 적용)
def crawling_new_sp_list(output_file_nm):
    proxies = {
        "http": SCRAPE_DO_PROXY,
        "https": SCRAPE_DO_PROXY
    }
    # proxies = {
    #     "http": '201.91.177.177:59229',
    #     "https": '201.91.177.177:59229'
    # }
     # 요청에 사용할 User-Agent (Cloudflare 우회 대비)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    # 크롤링 대상 URL
    base_url = "https://www.kimovil.com/en/compare-smartphones/order.dm+unveiledDate,i_m+code.Global:Intern:Americ:NA:Latam:BR:CN:IN:Sudasi:KR:JP,page.{}"
    page_count = 1
    output_file = output_file_nm
    all_links = []  # 모든 페이지의 링크 정보를 저장할 리스트
    new_list_finish = False
    sp_no_seq = 1

    while True:
        url = base_url.format(page_count)

        print(f"[INFO] 페이지 호출 중: {url} | 프록시: {proxies}")

        try:
            response = None 
            try :
                response = requests.get(url, headers=headers, proxies=proxies, verify=False)
                print(f"response = {response}, response code : {response.status_code}, {type(response.status_code)}")
                if response.status_code == 401 :
                    next_status, next_proxies = next_proxy()
                    if next_status :
                        proxies = next_proxies
                        print(f"proxies 토큰 변경 : {proxies}, {next_proxies}")
                    else :
                        print(f"Error : {next_proxies}")  
                        exit(1)                  
            except Exception as ee :
                print(ee)
            if response is not None :
                print(f"request url : {url} ==== response code ; {response.status_code}")
            retry_count = 0
            while response is not None and response.status_code != 200 :
                if response is not None and response.status_code == 404 :
                    return False, "404 Not found.."
                    
                if retry_count > 10 :
                    return False, f"max retry count error ! response code = {response}"
                    
                wait_time = 10
                if response is not None and response.status_code == 429 :
                    retry_after = response.headers.get('Retry-After')
                    print(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                    
                print(f"wait time : {wait_time}")
                time.sleep(wait_time)
                
                retry_count += 1
                # response = requests.get(base_url)
                try :
                    response = requests.get(url, headers=headers, proxies=proxies, verify=False)
                    if response.status_code == 401 :
                        next_status, next_proxies = next_proxy()
                        if next_status :
                            proxies = next_proxies
                            print(f"proxies 토큰 변경 : {proxies}, {next_proxies}")
                        else :
                            print(f"Error : {next_proxies}")  
                            exit(1)                     
                except Exception as ee :
                    print(ee)

                if response is not None :
                    print(f"Retry count : {retry_count}, request url : {url} ==== response code ; {response.status_code}")
            
            print(f"response code = {response.status_code}")
            if response.status_code == 200:
                print(f"[INFO] 페이지 {page_count} 로드 성공")
                # BeautifulSoup으로 HTML 파싱
                # json_response = response.json()
                # print(json_response.keys())
                # html_content = json_response['content']

                # soup = BeautifulSoup(html_content, "html.parser")
                soup = BeautifulSoup(response.text, "html.parser")

                ul_element = soup.find("ul", id="results-list")
                li_elements = ul_element.find_all("li", id=re.compile(r"^kiid_")) if ul_element else []

                if li_elements:
                    for li_tag in li_elements:
                        item_tag = li_tag.find('div', class_='item-wrap')
                        if item_tag:
                            link_tag = item_tag.find('a', class_='device-link')
                            device_link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "Unknown"
                            if device_link == "Unknown":
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
                                if status_tag:
                                    device_available = status_tag.get_text(strip=True).strip()
                                else:
                                    status_tag = name_div_tag.find("div", class_="status new")
                                    if status_tag:
                                        device_available = "New"
                                    else:
                                        status_tag = name_div_tag.find("div", class_="status rummors")
                                        if status_tag:
                                            device_available = "Rumor"
                                        else:
                                            status_tag = name_div_tag.find("div", class_="status presell")
                                            if status_tag:
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
                                if device_available != "New" and device_available != "Rumor" and device_available != "Presell":
                                    new_list_finish = True

                        data_tag = item_tag.find('div', class_='device-data')
                        features_tag = data_tag.find('div', class_='ki-features') if data_tag else None
                        data_list_tag = features_tag.find_all('div', class_='data')
                        if data_list_tag:
                            size_info = data_list_tag[0].get_text(strip=True)
                            device_size, device_weight = size_info.split('·') if "·" in size_info else ("Unknown", "Unknown")
                            device_battery_power = data_list_tag[1].get_text(strip=True) if len(data_list_tag) > 1 else "Unknown"

                            device_info['device_size'] = device_size
                            device_info['device_weight'] = device_weight  
                            device_info['device_battery_power'] = device_battery_power  
                            device_info['device_seq'] = sp_no_seq
                            device_info['media_name'] = "kimovil"

                            if not new_list_finish:
                                all_links.append(device_info)
                                sp_no_seq += 1

                else:
                    print(f"[INFO] 페이지 {page_count}에 데이터 없음. 크롤링 종료.")
                    break
            else:
                print(f"[ERROR] 페이지 {page_count} 로드 실패. 상태 코드: {response.status_code}")
                break
        except requests.RequestException as e:
            print(f"[ERROR] 요청 실패: {e}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_links, f, ensure_ascii=False, indent=4)

        if new_list_finish:
            break
        time.sleep(20)
        page_count += 1

    print(f"[INFO] 모든 데이터가 {output_file}에 저장되었습니다.")
