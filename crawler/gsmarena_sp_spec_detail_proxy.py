import requests
import time
import base64
import re
from bs4 import BeautifulSoup
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


class gsmarena_sp_spec_detail :
    def __init__(self) :

        self.proxies = {
            "http": SCRAPE_DO_PROXY,
            "https": SCRAPE_DO_PROXY
        }
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }           
        self.model_info = None
        self.base_url = None
        
    def to_print(self, device_model) :
        for key, value in device_model.items() :
            print(f"{key} : {value}")
    
    def run_crawling(self, model_info) :
        self.model_info = model_info
        self.base_url = model_info['device_link']        
        device_model = {}
        success = True
        brand_name = self.model_info['brand_name']
        brand_model = self.model_info['device_name']
        base_url = self.model_info['device_link']
        device_model['brand_name'] = brand_name
        device_model['brand_model'] = brand_model
        
        if self.base_url != None :
            base_url = self.base_url.replace('-', '-')
        else : 
            return False, f"device line info : None, {self.model_info}"
            
        try :
            response = None 
            try :
                response = requests.get(base_url, headers=self.headers, proxies=self.proxies, verify=False)
                print(f"response = {response}, response code : {response.status_code}, {type(response.status_code)}")
                if response.status_code == 401 :
                    next_status, next_proxies = next_proxy()
                    if next_status :
                        self.proxies = next_proxies
                        print(f"proxies 토큰 변경 : {self.proxies}, {next_proxies}")
                    else :
                        print(f"Error : {next_proxies}")  
                        exit(1)                  
            except Exception as ee :
                print(ee)            
            
            print(f"request url : {base_url} ==== response code : {response.status_code}")
            
            if response is not None and response.status_code == 404 :
                return False, "404 Not Found.."
                
            retry_count = 0
            while response is not None and response.status_code != 200 :
                if response is not None and response.status_code == 404 :
                    return False, "404 Not found.."
                    
                if retry_count > 15 :
                    return False, f"max retry count error ! response code = {response.status_code}"
                    
                wait_time = 10
                if response is not None and response.status_code == 429 :
                    retry_after = response.headers.get('Retry-After')
                    print(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                    
                print(f"wait time : {wait_time}")
                time.sleep(wait_time)
                
                retry_count += 1
                try :
                    response = requests.get(base_url, headers=self.headers, proxies=self.proxies, verify=False)
                    print(f"response = {response}, response code : {response.status_code}, {type(response.status_code)}")
                    if response.status_code == 401 :
                        next_status, next_proxies = next_proxy()
                        if next_status :
                            self.proxies = next_proxies
                            print(f"proxies 토큰 변경 : {self.proxies}, {next_proxies}")
                        else :
                            print(f"Error : {next_proxies}")  
                            exit(1)                      
                except Exception as ee :
                    print(ee) 

                print(f"Retry count : {retry_count}, request url : {base_url} ==== response code ; {response.status_code}")

            if response.status_code == 200 :
                # json_response = response.json()
                # print(json_response.keys())
                # html_content = json_response['content']
                # soup = BeautifulSoup(html_content, "html.parser")
                soup = BeautifulSoup(response.text, "html.parser")
                specs_list_tag = soup.find('div', id="specs-list")

                if specs_list_tag :
                    tables_tag = specs_list_tag.find_all('table')
                    print(f"table count = {len(tables_tag)}")
                    for idx, tbl_tag in enumerate(tables_tag, start=1) :
                        # print(tbl_tag)
                        first_th = tbl_tag.find("th")
                        
                        s_title = ""
                        first_title = first_th.get_text(strip=True).lower()
                        if "network" in first_title :
                            print(f"Network Extract {idx} th table")
                            s_title = "network_"
                        elif "launch" in first_title :
                            print(f"LAUNCH Extract {idx} th Table")
                            s_title = "launch_"
                        elif "body" in first_title :
                            print(f"BODY Extract {idx} th Table")
                            s_title = "body_"
                        elif "display" in first_title :
                            print(f"DISPLAY Extract {idx} th Table")
                            s_title = "display_"
                        elif "platform" in first_title :
                            print(f"Platform Extract {idx} th Table")
                            s_title = "platform_"
                        elif "memory" in first_title :
                            print(f"MEMORY Extract {idx} th Table")
                            s_title = "memory_"
                        elif "main camera" in first_title :
                            print(f"Main Camera Extract {idx} th Table")
                            s_title = "main_camera_"
                        elif "selfie camera" in first_title :
                            print(f"SELFIE CAMERA Extract {idx} th Table")
                            s_title = "selfie_camera_"
                        elif "sound" in first_title :
                            print(f"SOUND Extract {idx} th Table")
                            s_title = "sound_"
                        elif "comms" in first_title :
                            print(f"Comms Extract {idx} th Table")
                            s_title = "comms_"
                        elif "features" in first_title :
                            print(f"Features Extract {idx} th Table")
                            s_title = "feature_"
                        elif "battery" in first_title :
                            print(f"Battery Extract {idx} th Table")
                            s_title = "battery_"
                        elif "misc" in first_title :
                            print(f"MISC Extract {idx} th Table")
                            s_title = "misc_"
                        elif "tests" in first_title :
                            print(f"Tests Extract {idx} th Table")
                            s_title = "tests_"

                        if s_title != '' :
                            rows = tbl_tag.find_all("tr")

                            b_contents = ""
                            b_key_word = ""

                            for row in rows :
                                td = row.find_all("td")

                                if td and len(td) == 2 :
                                    
                                    key_word = td[0].get_text(strip=True).replace(" ", "_").lower()

                                    texts = re.split(r'<br(?:\s*/?)?>', td[1].decode_contents()) 
                                    texts = [re.sub(r'<a.*?>.*?</a>', '', text.strip()).replace('</br>', '') for text in texts]
                                    contents = '\n '.join(texts)
                                    if contents == "" or key_word == 'battery_(new)' :
                                        contents = td[1].get_text(strip=True)
                                    
                                    if key_word == "" :
                                        b_contents = '\n '.join([b_contents, contents]) if b_contents else contents
                                    else :
                                      b_key_word = key_word
                                      b_contents = contents

                                    device_model[f'{s_title}{b_key_word}'] = b_contents

        except Exception as e :
            success = False
            print(e)
            return success, [f"Error occurred : {str(e)}"]
        
        # self.to_print(device_model)
        
        return success, device_model
        
