import requests
import json
import time
import socket
import concurrent.futures
import itertools
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
import warnings

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

def gamarena_new_sp_list(output_file_nm) :

    proxies = {
        "http": SCRAPE_DO_PROXY,
        "https": SCRAPE_DO_PROXY
    }
    # proxies = {
    #     "http": f"http://proxy.scrape.do:8080",
    #     "https": f"http://proxy.scrape.do:8080"
    # }    
     # 요청에 사용할 User-Agent (Cloudflare 우회 대비)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {SCRAPE_DO_TOKEN}"
    }
    auth = (SCRAPE_DO_TOKEN, "customHeaders=false")
    brand_list_urls = [
                            {'BRAND' :'SAMSUNG' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=9'     }      
                            , {'BRAND' :'APPLE' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=48'      }
                            , {'BRAND' :'HUAWEI' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=58'     }
                            , {'BRAND' :'NOKIA' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=1'       }
                            , {'BRAND' :'SONY' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=7'        }
                            , {'BRAND' :'LG' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=20'         }
                            , {'BRAND' :'MOTOROLA' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=4'    }   
                            , {'BRAND' :'XIAOMI' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=80'     }
                            , {'BRAND' :'GOOGLE' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=107'    } 
                            , {'BRAND' :'HONOR' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=121'     }
                            , {'BRAND' :'OPPO' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=82'       }
                            , {'BRAND' :'REALME' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=118'    } 
                            , {'BRAND' :'ONEPLUS' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=95'    }  
                            , {'BRAND' :'VIVO' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=98'       }
                            , {'BRAND' :'INFINIX' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=119'   }   
                            , {'BRAND' :'TECNO' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=120'     }
                            , {'BRAND' :'ITEL' , 'device_link' : 'https://www.gsmarena.com/results.php3?nYearMin={}&sMakers=131'      }
                            , {'BRAND' :'RUMORE' , 'device_link' : 'https://www.gsmarena.com/rumored.php3'                            }      
                        ]

    output_file = output_file_nm
    all_links = []  # 모든 페이지의 링크 정보를 저장할 리스트
    # 현재 날짜 가져오기
    today = datetime.today()

    get_year = (today - relativedelta(months=1)).year

    for brand_info in brand_list_urls :

        brand_name = brand_info['BRAND']
        base_url = brand_info['device_link']
        
        url = base_url.format(get_year)
        print(f"[INFO] GSMARENA 페이지 호출 중: {url}")

        # 요청 보내기
        print(f"proxy server : {proxies}")
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
        except Exception as re :
            print(re)
   
        retry_count = 0
        while response is not None and response.status_code != 200:

            if response is not None and response.status_code == 404 :
                return False, "404 Not found.."
                
            if retry_count > 10 :
                return False, f"max retry count error ! response code = {response.status_code}"
                
            wait_time = 10
            if response is not None and response.status_code == 429 :
                retry_after = response.headers.get('Retry-After')
                print(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                
            print(f"wait time : {wait_time}")
            time.sleep(wait_time)
            
            retry_count += 1
            print(f"proxy server : {proxies}")
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
            except Exception as re :
                print(re)
           
        # print(response.text)
        # 응답 확인
        if response.status_code == 200:
            print(f"[INFO] {brand_name} 페이지 로드 성공")
            # print(response)
            # # BeautifulSoup으로 HTML 파싱
            # json_response = response.json()
            # print(json_response.keys())
            # html_content = json_response['content']

            # soup = BeautifulSoup(html_content, "html.parser")
            soup = BeautifulSoup(response.text, "html.parser")

            ul_element = soup.find("div", class_="makers")
            li_elements = ul_element.find_all("li") if ul_element else []

            if li_elements:
                for li_tag in li_elements:
                    link_tag = li_tag.find('a')
                    device_link = link_tag['href'].strip() if link_tag else ""
                    if device_link != '' :
                        device_link = 'https://www.gsmarena.com/' + device_link

                    span_tag = link_tag.find('span')
                    texts = span_tag.decode_contents().split('<br/>')
                    texts = [text.strip() for text in texts]
                    
                    print(f"len : {len(texts)}, content : {texts}")
                    if len(texts) > 1 :
                        device_name = texts[1]
                    else : 
                        brand_name, device_name = texts[0].split(' ', 1)
                    if device_name != '' :
                        device_info = {
                                'brand_name' : brand_name.upper() ,
                                'device_name': device_name,
                                'device_link': device_link
                            }

                    all_links.append(device_info)

            else:
                print(f"[INFO] {brand_name}에 {get_year} 년 이후 상품 데이터가 없습니다. ")
                
        else:
            print(f"[ERROR] 페이지 {brand_name} 로드 실패. 상태 코드: {response.status_code}, {response}")
            break

        print(f"[INFO] 페이지 {brand_name} 크롤링 완료.")

        # JSON 파일로 저장
        print(f"[INFO] 총 {len(all_links)}개의 장치 정보를 저장합니다.")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_links, f, ensure_ascii=False, indent=4)    

        time.sleep(20)  # 요청 간 딜레이 추가
            
        print(f"[INFO] 모든 링크 정보가 {output_file}에 저장되었습니다.")


    
