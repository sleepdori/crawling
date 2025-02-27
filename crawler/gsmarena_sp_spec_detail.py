import requests
import time
import base64
import re
from bs4 import BeautifulSoup

class gsmarena_sp_spec_detail :
    def __init__(self) :
        self.model_info = None
        self.base_url = None
        
    def to_print(self, device_model) :
        for key, value in device_model.items() :
            print(f"{key} : {value}")
    
    def get_response(self, url):
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
            # response = requests.get(base_url)
            request_success, response = self.get_response(base_url)
            print(f"request url :{request_success},  {base_url} ==== response code : {response.status_code}")
            
            if response.status_code == 404 :
                return False, "404 Not Found.."
                
            retry_count = 0
            while response.status_code != 200 :
                if response.status_code == 404 :
                    return False, "404 Not found.."
                    
                if retry_count > 5 :
                    return False, f"max retry count error ! response code = {response.status_code}"
                    
                wait_time = 20
                if response.status_code == 429 :
                    retry_after = response.headers.get('Retry-After')
                    print(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                    wait_time = int(retry_after)/20
                    
                print(f"wait time : {wait_time}")
                time.sleep(wait_time)
                
                retry_count += 1
                # response = requests.get(base_url)
                request_success, response = self.get_response(base_url)
                print(f"Retry count : {retry_count}, request url : {base_url} ==== response code ; {response.status_code}")

            json_response = response.json()
            if 'browserHtml' in json_response['data']:
                html_content = json_response['data']['browserHtml']
            else:
                # html_content = base64.b64decode(json_response['data']['httpResponseBody']).decode()               
                html_content = base64.b64decode(json_response['data']['httpResponseBody'], validate=True).decode('utf-8', errors='ignore')  

            if response.status_code == 200 :
                soup = BeautifulSoup(html_content, "html.parser")
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
            return success, [f"Error occurred : {str(e)}"]
        
        # self.to_print(device_model)
        
        return success, device_model
        

