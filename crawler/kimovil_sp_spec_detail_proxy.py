import re
import time
import requests
import base64
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

class kimovil_sp_spec_detail:
    def __init__(self):

        self.proxies = {
            "http": SCRAPE_DO_PROXY,
            "https": SCRAPE_DO_PROXY
        }
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }       

    def runCrawling(self, model_info):
        device_link = model_info['device_link']
        device_model = {}
        success = True

        if device_link != None :
            base_url = device_link.replace('－', '-')
        else :
            return False, f"device link info : None, {model_info}"

        try:
            response = None
            try :
                response = requests.get(base_url, headers=self.headers, proxies=self.proxies, verify=False)
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

            if response is not None :
                print(f"request url : {base_url} ==== response code : {response.status_code}")
            
            if response is not None and response.status_code == 404 :
                return False, "404 Not Found.."
                
            retry_count = 0
            while response is not None and response.status_code != 200 :
                if response is not None and response.status_code == 404 :
                    return False, "404 Not found.."
                    
                if retry_count > 20 :
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

                if response is not None :
                    print(f"Retry count : {retry_count}, request url : {base_url} ==== response code ; {response.status_code}")

            # json_response = response.json()
            # print(json_response.keys())
            # html_content = json_response['content']  

            if response.status_code == 200 : 

                # soup = BeautifulSoup(html_content, "html.parser")
                soup = BeautifulSoup(response.text, "html.parser")
                detail_body_tag = soup.find("article", class_="container-datasheet")
                if detail_body_tag != None:
                    wrapper_tag = detail_body_tag.find("div", class_="wrapper")
                    if wrapper_tag != None :
                        idx = 0
                        brand_table_tag = wrapper_tag.find_all("table", class_="k-dltable")
                        if brand_table_tag :
                            device_model['site'] = 'kimovil'
                            device_model['link_url'] = base_url
                            device_model['brand_model'] = model_info['device_name']
                            device_model['model_version'] = model_info['device_version'] 
                                                      
                            for brand_table_tag in wrapper_tag.find_all("table", class_="k-dltable") :
                                rows = brand_table_tag.find_all('tr')
                                td_tag = rows[0].find_all('td')
                                if idx == 0 :
                                    brand_name = td_tag[0].find('a').get_text(strip=True)
                                    device_model['category'] = brand_name
                                    device_model['brand_name'] = brand_name
                                    print(f"brand_name : {brand_name}")
                                
                                if idx == 1 :
                                    release_date = td_tag[0].get_text(strip=True).split(',')[0]
                                    device_model['release_date'] = release_date
                                    print(f"release_date : {release_date}")

                                idx += 1
                        else :
                            dl_tags = wrapper_tag.find_all("dl", class_="k-dl")
                            if dl_tags : 
                                idx = 0
                                for dl_tag in dl_tags :
                                    dt_text = dl_tag.find('dt').get_text(strip=True).upper() 
                                    if dt_text == "BRAND" :
                                        brand_name = dl_tag.find('dd').get_text(strip=True)
                                        device_model['category'] = brand_name
                                        device_model['brand_name'] = brand_name
                                        print(f"brand_name : {brand_name}")
                                    if dt_text == "RELEASE DATE" :
                                        release_date = dl_tag.find('dd').get_text(strip=True)
                                        device_model['release_date'] = release_date
                                        print(f"release_date : {release_date}")

                        price_tbl_tag = wrapper_tag.find_all("table", class_="version-prices-table k-datatable") 
                        if price_tbl_tag != None :
                            for price_tag in price_tbl_tag :
                                rows = price_tag.find_all('tr')
                                price_idx = 0
                                for row in rows :
                                    p_price = row.find_all('td')[0].get_text(strip=True)
                                    if p_price != None and p_price != '' :
                                        price_idx += 1
                                        p_model = row.find_all('th')[0].get_text(strip=True).upper()
                                        if p_model != None and p_model.strip() != '' :
                                            price_model, price_detail_model = p_model.split('•')
                                            device_model[f'price_model{price_idx}'] = price_model
                                            if price_detail_model != None and price_detail_model.strip() != '' :
                                                price_regn, price_memory, price_storage = price_detail_model.split('·')[:3]
                                                device_model[f'price_regn{price_idx}'] = price_regn.strip()
                                                device_model[f'price_memory{price_idx}'] = price_memory.strip()
                                                device_model[f'price_storage{price_idx}'] = price_storage.strip()
                                        
                                        device_model[f'p_price{price_idx}'] = p_price.strip()
                                        print(f"price_model{price_idx} = {price_model}     \
                                                          , price_regn{price_idx} = {price_regn}               \
                                                          , price_memory{price_idx} = {price_memory.strip()}   \
                                                          , price_storage{price_idx} = {price_storage.strip()} \
                                                          , price{price_idx} = {p_price.strip()}")
                                      
                    section_tag = detail_body_tag.find('section', class_='kc-container white container-sheet-design')
                    if section_tag != None :
                        idx = 0
                        for table_tag in section_tag.find_all("table", class_="k-dltable") :   
                            if idx == 1 :
                                rows = table_tag.find_all('tr')  
                                for row in rows :
                                    if "SIZE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        device_size =  row.find_all('td')[0].find('a').get_text(strip=True).replace("See more details", '')
                                        device_model['model_size'] = device_size
                                        print(f"device_size : {device_size}")
                                    if "WEIGHT" in row.find_all('th')[0].get_text(strip=True).upper() :    
                                        device_weight = row.find_all('td')[0].get_text(strip=True)
                                        device_model['model_weight'] = device_weight
                                        print(f"device_weight : {device_weight}")
                                    if "RESISTANCE " in row.find_all('th')[0].get_text(strip=True).upper() :
                                        Resistance_certificates = row.find_all('td')[0].get_text(strip=True).replace("See more details", '')
                                        device_model['Resistance_certificates'] = Resistance_certificates
                                        print(f"Resistance_certificates : {Resistance_certificates}")
                                    if "COLORS " in row.find_all('th')[0].get_text(strip=True).upper() :
                                        device_color = row.find_all('td')[0].get_text(strip=True).replace("See more details", '')
                                        print(f"device_color : {device_color}")

                            if idx == 2 :
                                rows = table_tag.find_all('tr') 
                                for row in rows :
                                    if "DIAGONAL" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        screen_size = row.find_all('td')[0].get_text(strip=True).replace("See more details", '')
                                        device_model['screen_size'] = screen_size
                                        print(f"screen_size : {screen_size}")

                                    if "TYPE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        screen_type = row.find_all('td')[0].get_text(strip=True)
                                        device_model['screen_type'] = screen_type
                                        print(f"screen_type : {screen_type}")

                                    if "ASPECT" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        screen_aspect_ratio = row.find_all('td')[0].get_text(strip=True)
                                        device_model['screen_aspect_ratio'] = screen_aspect_ratio
                                        print(f"screen_aspect_ratio : {screen_aspect_ratio}")

                                    if "RESOLUTION" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        screen_resolution = row.find_all('td')[0].get_text(strip=True)
                                        device_model['screen_resolution'] = screen_resolution
                                        print(f"screen_resolution : {screen_resolution}")

                                    if "DENSITY" in row.find_all('th')[0].get_text(strip=True).upper() :    
                                        screen_density = row.find_all('td')[0].get_text(strip=True)
                                        device_model['screen_density'] = screen_density
                                        print(f"screen_density : {screen_density}")

                                    if "OTHERS" in row.find_all('th')[0].get_text(strip=True).upper() : 
                                        screen_others = ''
                                        cnt = 0
                                        for li_tag in row.find_all('td')[0].find_all('li') :
                                            if cnt == 0 :
                                                screen_others = li_tag.get_text(strip=True)
                                            else :
                                                screen_others = screen_others + ", " + li_tag.get_text(strip=True)
                                            cnt += 1
                                        device_model['screen_others'] = screen_others
                                        print(f"screen_others : {screen_others}")
                            idx += 1

                    section_tag = detail_body_tag.find('section', class_='kc-container white container-sheet-hardware')
                    if section_tag != None :
                        for table_tag in section_tag.find_all("table", class_="k-dltable") :  
                            rows = table_tag.find_all('tr') 
                            cpu_yn = False
                            ram_yn = False 
                            capacity_yn = False
                            for row in rows :
                                if "MODEL" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    processor_model  = row.find_all('td')[0].get_text(strip=True)
                                    device_model['processor_model'] = processor_model
                                    print(f"processor_model : {processor_model}")

                                if "CPU" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    processor_cpu  = row.find_all('td')[0].get_text(strip=True)
                                    device_model['processor_cpu'] = processor_cpu
                                    print(f"processor_cpu : {processor_cpu}")
                                    cpu_yn = True

                                if "TYPE" in row.find_all('th')[0].get_text(strip=True).upper() and cpu_yn :
                                    processor_type = row.find_all('td')[0].get_text(strip=True)
                                    device_model['processor_type'] = processor_type
                                    print(f"processor_type : {processor_type}")

                                if "NANOMETER" in row.find_all('th')[0].get_text(strip=True).upper() :    
                                    processor_nanometer = row.find_all('td')[0].get_text(strip=True)
                                    device_model['processor_nanometer'] = processor_nanometer
                                    print(f"processor_nanometer : {processor_nanometer}")

                                if "FREQUENCY" in row.find_all('th')[0].get_text(strip=True).upper() :    
                                    processor_frequency = row.find_all('td')[0].get_text(strip=True)
                                    device_model['processor_frequency'] = processor_frequency
                                    print(f"processor_frequency : {processor_frequency}")

                                if "BITS" in row.find_all('th')[0].get_text(strip=True).upper() : 
                                    processor_64bit = row.find_all('td')[0].get_text(strip=True)
                                    device_model['processor_64bit'] = processor_64bit
                                    print(f"processor_64bit : {processor_64bit}") 
     
                                if "GPU" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    graphics_gpu  = rows[0].find_all('td')[0].get_text(strip=True)
                                    device_model['graphics_gpu'] = graphics_gpu
                                    print(f"graphics_gpu : {graphics_gpu}")

                                if "RAM" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    ram_size  = row.find_all('td')[0].get_text(strip=True)
                                    device_model['ram_size'] = ram_size
                                    print(f"ram_size : {ram_size}")
                                    ram_yn = True

                                if "TYPE" in row.find_all('th')[0].get_text(strip=True).upper() and ram_yn:
                                    ram_type = row.find_all('td')[0].get_text(strip=True)
                                    device_model['ram_type'] = ram_type
                                    print(f"ram_type : {ram_type}")

                                if "SCORE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    antutu_score  = row.find_all('td')[0].get_text(strip=True).replace('•', ' ( ').replace('v10O', 'v10 ), - O').replace('See more details', '')
                                    device_model['antutu_score'] = antutu_score
                                    print(f"antutu_score : {antutu_score}")

                                if "CAPACITY" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    storage_capacity  = row.find_all('td')[0].get_text(strip=True)
                                    device_model['storage_capacity'] = storage_capacity
                                    print(f"storage_capacity : {storage_capacity}")
                                    capacity_yn = True

                                if "SLOT" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    storage_SD_slot = re.sub(r'\s+', ' ', row.find_all('td')[0].get_text(strip=True).replace('\n', ' ')).strip()
                                    device_model['storage_SD_slot'] = storage_SD_slot
                                    print(f"storage_SD_slot : {storage_SD_slot}") 

                                if "TYPE" in row.find_all('th')[0].get_text(strip=True).upper() and capacity_yn:
                                    storage_type = row.find_all('td')[0].get_text(strip=True)
                                    device_model['storage_type'] = storage_type
                                    print(f"storage_type : {storage_type}")
                                    
                                if "AUDIO" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    li_tag  = rows[0].find_all('td')[0].find_all('li')
                                    li_cnt = 0
                                    audio = ''
                                    for li in li_tag :
                                        if li_cnt == 0 :
                                            audio = li.get_text(strip=True)
                                        else :
                                            audio = audio + ", " + li.get_text(strip=True)
                                        li_cnt += 1

                                    device_model['audio'] = audio
                                    print(f"audio : {audio}")                                 

                    section_tag = detail_body_tag.find('section', class_='kc-container dark black-isometric container-sheet-camera')
                    if section_tag != None :
                        h3_tag = section_tag.find('h3', class_='k-h4')
                        camera_desc = h3_tag.get_text(strip=True)
                        device_model['camera_desc'] = camera_desc
                        print(f"camera_desc : {camera_desc}")

                        idx = 0
                        for div_tag in section_tag.find_all("div", class_="k-column-blocks g-2-cols") :
                            
                            if idx == 0 :
                                c_tag = div_tag.find_all("div", class_="w50")
                                print(f"camera_count : {len(c_tag)}")
                                for camera_tag in c_tag :
                                    c_idx = 0
                                    camera_number = 1                                    
                                    table_tag = camera_tag.find('table', class_="k-dltable")
                                    
                                    if table_tag != None :
                                        rows = table_tag.find_all('tr') 
                                        for row in rows :
                                            if c_idx == 0 :
                                                camera_number = row.find_all('td')[0].get_text(strip=True)
                                                camera_kind = row.find_all('th')[0].get_text(strip=True)
                                                device_model[f'camera_number{camera_number}'] = camera_number
                                                device_model[f'camera_kind{camera_number}'] = camera_kind
                                                print(f"camera_number{camera_number} : {camera_number}")
                                                print(f"camera_kind{camera_number} : {camera_kind}")

                                            if "RESOLUTION" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                camera_resolution  = row.find_all('td')[0].get_text(strip=True)
                                                device_model[f'camera_resolution{camera_number}'] = camera_resolution
                                                print(f"camera_resolution{camera_number} : {camera_resolution}")

                                            if "SENSOR" in row.find_all('th')[0].get_text(strip=True).upper() and "SIZE" not in row.find_all('th')[0].get_text(strip=True).upper():
                                                camera_sensor  = row.find_all('td')[0].get_text(strip=True)
                                                device_model[f'camera_sensor{camera_number}'] = camera_sensor
                                                print(f"camera_sensor{camera_number} : {camera_sensor}")

                                            if "TYPE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                camera_type  = row.find_all('td')[0].get_text(strip=True)
                                                device_model[f'camera_type{camera_number}'] = camera_type
                                                print(f"camera_type{camera_number} : {camera_type}")

                                            if "APERTURE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                camera_aperture  = row.find_all('td')[0].get_text(strip=True)
                                                device_model[f'camera_aperture{camera_number}'] = camera_aperture
                                                print(f"camera_aperture{camera_number} : {camera_aperture}")

                                            if "ISO" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                camera_iso  = row.find_all('td')[0].get_text(strip=True)
                                                device_model[f'camera_iso{camera_number}'] = camera_iso
                                                print(f"camera_iso{camera_number} : {camera_iso}") 
                                            
                                            if "PIXEL SIZE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                camera_pixel_size  = row.find_all('td')[0].get_text(strip=True)
                                                device_model[f'camera_pixel_size{camera_number}'] = camera_pixel_size
                                                print(f"camera_pixel_size{camera_number} : {camera_pixel_size}")
                                            
                                            if "BINNING" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                camera_pixel_binning  = row.find_all('td')[0].get_text(strip=True)
                                                device_model[f'camera_pixel_binning{camera_number}'] = camera_pixel_binning
                                                print(f"camera_pixel_binning{camera_number} : {camera_pixel_binning}") 
                                            
                                            if "SENSOR SIZE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                camera_sensor_size  = row.find_all('td')[0].get_text(strip=True)
                                                device_model[f'camera_sensor_size{camera_number}'] = camera_sensor_size
                                                print(f"camera_sensor_size{camera_number} : {camera_sensor_size}") 
                                            
                                            c_idx += 1
                                    else :
                                        dl_tag = camera_tag.find('dl', class_="k-dl")
                                        dt_list = dl_tag.find_all('dt')
                                        dd_list = dl_tag.find_all('dd')

                                        for dt, dd in zip(dt_list, dd_list) :
                                            if c_idx == 0 :
                                                camera_number = dd.get_text(strip=True)
                                                camera_kind = dt.get_text(strip=True)
                                                device_model[f'camera_number{camera_number}'] = camera_number
                                                device_model[f'camera_kind{camera_number}'] = camera_kind
                                                print(f"camera_number{camera_number} : {camera_number}")
                                                print(f"camera_kind{camera_number} : {camera_kind}")

                                            if "RESOLUTION" in dt.get_text(strip=True).upper() :
                                                camera_resolution  = dd.get_text(strip=True)
                                                device_model[f'camera_resolution{camera_number}'] = camera_resolution
                                                print(f"camera_resolution{camera_number} : {camera_resolution}")

                                            if "SENSOR" in dt.get_text(strip=True).upper() and "SIZE" not in dt.get_text(strip=True).upper() :
                                                camera_sensor  = dd.get_text(strip=True)
                                                device_model[f'camera_sensor{camera_number}'] = camera_sensor
                                                print(f"camera_sensor{camera_number} : {camera_sensor}")

                                            if "TYPE" in dt.get_text(strip=True).upper() :
                                                camera_type  = dd.get_text(strip=True)
                                                device_model[f'camera_type{camera_number}'] = camera_type
                                                print(f"camera_type{camera_number} : {camera_type}")

                                            if "APERTURE" in dt.get_text(strip=True).upper() :
                                                camera_aperture  = dd.get_text(strip=True)
                                                device_model[f'camera_aperture{camera_number}'] = camera_aperture
                                                print(f"camera_aperture{camera_number} : {camera_aperture}")

                                            if "ISO" in dt.get_text(strip=True).upper() :
                                                camera_iso  = dd.get_text(strip=True)
                                                device_model[f'camera_iso{camera_number}'] = camera_iso
                                                print(f"camera_iso{camera_number} : {camera_iso}") 
                                            
                                            if "PIXEL SIZE" in dt.get_text(strip=True).upper() :
                                                camera_pixel_size  = dd.get_text(strip=True)
                                                device_model[f'camera_pixel_size{camera_number}'] = camera_pixel_size
                                                print(f"camera_pixel_size{camera_number} : {camera_pixel_size}")
                                            
                                            if "BINNING" in dt.get_text(strip=True).upper() :
                                                camera_pixel_binning  = dd.get_text(strip=True)
                                                device_model[f'camera_pixel_binning{camera_number}'] = camera_pixel_binning
                                                print(f"camera_pixel_binning{camera_number} : {camera_pixel_binning}") 
                                            
                                            if "SENSOR SIZE" in dt.get_text(strip=True).upper() :
                                                camera_sensor_size  = dd.get_text(strip=True)
                                                device_model[f'camera_sensor_size{camera_number}'] = camera_sensor_size
                                                print(f"camera_sensor_size{camera_number} : {camera_sensor_size}") 
                                            
                                            c_idx += 1

                            if idx == 1 :

                                selfie_yn = 'Yes'
                                device_model['selfie_yn'] = selfie_yn
                                print(f"selfie_yn : {selfie_yn}")

                                for camera_tag in div_tag.find_all("div", class_="w50") :
                                    table_tag = camera_tag.find('table', class_="k-dltable")
                                    if table_tag :
                                        rows = table_tag.find_all('tr') 

                                        for row in rows :
                                            if "RESOLUTION" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                selfie_resolution  = row.find_all('td')[0].get_text(strip=True)
                                                device_model['selfie_resolution'] = selfie_resolution
                                                print(f"selfie_resolution : {selfie_resolution}")

                                            if "SENSOR" in row.find_all('th')[0].get_text(strip=True).upper() and "SIZE" not in row.find_all('th')[0].get_text(strip=True).upper() :
                                                selfie_sensor  = row.find_all('td')[0].get_text(strip=True)
                                                device_model['selfie_sensor'] = selfie_sensor
                                                print(f"selfie_sensor : {selfie_sensor}")

                                            if "TYPE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                selfie_type  = row.find_all('td')[0].get_text(strip=True)
                                                device_model['selfie_type'] = selfie_type
                                                print(f"selfie_type : {selfie_type}")

                                            if "APERTURE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                selfie_aperture  = row.find_all('td')[0].get_text(strip=True)
                                                device_model['selfie_aperture'] = selfie_aperture
                                                print(f"selfie_aperture : {selfie_aperture}")

                                            if "PIXEL SIZE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                selfie_pixel_size  = row.find_all('td')[0].get_text(strip=True)
                                                device_model['selfie_pixel_size'] = selfie_pixel_size
                                                print(f"selfie_pixel_size : {selfie_pixel_size}")

                                            if "BINNING" in row.find_all('th')[0].get_text(strip=True).upper() :
                                                selfie_pixel_binning  = row.find_all('td')[0].get_text(strip=True)
                                                device_model['selfie_pixel_binning'] = selfie_pixel_binning
                                                print(f"selfie_pixel_binning : {selfie_pixel_binning}")                                        
                                            
                                            if "SENSOR SIZE" in row.find_all('th')[0].get_text(strip=True).upper() :  
                                                selfie_sensor_size  = row.find_all('td')[0].get_text(strip=True)
                                                device_model['selfie_sensor_size'] = selfie_sensor_size
                                                print(f"selfie_sensor_size : {selfie_sensor_size}") 
                                    else :
                                        dl_tag = camera_tag.find('dl', class_="k-dl")
                                        if dl_tag :
                                            dt_list = dl_tag.find_all('dt')
                                            dd_list = dl_tag.find_all('dd')

                                            for dt, dd in zip(dt_list, dd_list) :                                 
                                                if "RESOLUTION" in dt.get_text(strip=True).upper() :
                                                    selfie_resolution  = dd.get_text(strip=True)
                                                    device_model['selfie_resolution'] = selfie_resolution
                                                    print(f"selfie_resolution : {selfie_resolution}")

                                                if "SENSOR" in dt.get_text(strip=True).upper() and "SIZE" not in dt.get_text(strip=True).upper() :
                                                    selfie_sensor  = dd.get_text(strip=True)
                                                    device_model['selfie_sensor'] = selfie_sensor
                                                    print(f"selfie_sensor : {selfie_sensor}")

                                                if "TYPE" in dt.get_text(strip=True).upper() :
                                                    selfie_type  = dd.get_text(strip=True)
                                                    device_model['selfie_type'] = selfie_type
                                                    print(f"selfie_type : {selfie_type}")

                                                if "APERTURE" in dt.get_text(strip=True).upper() :
                                                    selfie_aperture  = dd.get_text(strip=True)
                                                    device_model['selfie_aperture'] = selfie_aperture
                                                    print(f"selfie_aperture : {selfie_aperture}")

                                                if "PIXEL SIZE" in dt.get_text(strip=True).upper() :
                                                    selfie_pixel_size  = dd.get_text(strip=True)
                                                    device_model['selfie_pixel_size'] = selfie_pixel_size
                                                    print(f"selfie_pixel_size : {selfie_pixel_size}")
                                                
                                                if "BINNING" in dt.get_text(strip=True).upper() :
                                                    selfie_pixel_binning  = dd.get_text(strip=True)
                                                    device_model['selfie_pixel_binning'] = selfie_pixel_binning
                                                    print(f"selfie_pixel_binning : {selfie_pixel_binning}")     
                                                
                                                if "SENSOR SIZE" in dt.get_text(strip=True).upper() :
                                                    selfie_sensor_size  = dd.get_text(strip=True)
                                                    device_model['selfie_sensor_size'] = selfie_sensor_size
                                                    print(f"selfie_sensor_size : {selfie_sensor_size}") 
                                        else :
                                            device_model['selfie_yn'] = "No"
                                            print(f"selfie_yn : No")
                            idx += 1

                        flash_tbl_tag = section_tag.find_all('table', class_='k-dltable')

                        for flash_tag in flash_tbl_tag :
                            rows = flash_tag.find_all('tr') 
                            # print(f"flash_tag rows : {len(flash_tbl_tag)},  {rows}")   
                            
                            for row in rows :
                                if "FLASH" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    camera_flash  = row.find_all('td')[0].get_text(strip=True)
                                    device_model['camera_flash'] = camera_flash
                                    print(f"camera_flash : {camera_flash}")
                                
                                if "STABILISATION" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    camera_optical_stabilisation  = row.find_all('td')[0].get_text(strip=True)
                                    device_model['camera_optical_stabilisation'] = camera_optical_stabilisation
                                    print(f"camera_optical_stabilisation : {camera_optical_stabilisation}")

                                if "SLOW MOTION VIDEO" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    camera_slow_motion_video  = rows[2].find_all('td')[0].get_text(strip=True)
                                    device_model['camera_slow_motion_video'] = camera_slow_motion_video
                                    print(f"camera_slow_motion_video : {camera_slow_motion_video}")

                                if "FEATURES" in row.find_all('th')[0].get_text(strip=True).upper() :
                                    camera_features = ''
                                    cnt = 0
                                    for li_tag in rows[3].find_all('td')[0].find_all('li') :
                                        if cnt == 0 :
                                            camera_features = li_tag.get_text(strip=True)
                                        else :
                                            camera_features = camera_features + ", " + li_tag.get_text(strip=True)
                                        cnt += 1       
                                    device_model['camera_features'] = camera_features  
                                    print(f"camera_features : {camera_features}")                       

                        dl_tags = section_tag.find_all('dl', class_='k-dl')
                        if dl_tags :
                            for dl_tag in dl_tags :
                                dt_text = dl_tag.find('dt').get_text(strip=True).upper()
                                if dt_text == "EXTRA" :
                                    dd_tag = dl_tag.find('dd')

                                    li_tag  = dd_tag.find_all('li')
                                    li_cnt = 0
                                    camera_extra = ''
                                    for li in li_tag :
                                        if li_cnt == 0 :
                                            camera_extra = li.get_text(strip=True)
                                        else :
                                            camera_extra = camera_extra + ", " + li.get_text(strip=True)
                                        li_cnt += 1
                                    device_model['camera_extra'] = camera_extra
                                    print(f"camera_extra : {camera_extra}")  
                                    
                    section_tag = detail_body_tag.find('section', class_='kc-container white container-sheet-battery')
                    if section_tag != None :

                        idx = 0
                        try :
                            for table_tag in section_tag.find_all("table", class_="k-dltable") :  
                                
                                rows = table_tag.find_all('tr') 
                                for row in rows :
                                    if "CAPACITY" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        battery_capacity  = row.find_all('td')[0].get_text(strip=True).replace('See more details', '')
                                        device_model['battery_capacity'] = battery_capacity
                                        print(f"battery_capacity : {battery_capacity}")

                                    if "TYPE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        battery_type  = row.find_all('td')[0].get_text(strip=True)
                                        device_model['battery_type'] = battery_type
                                        print(f"battery_type : {battery_type}")

                                    if "FAST CHARGE" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        battery_fast_charge = row.find_all('td')[0].get_text(strip=True)
                                        device_model['battery_fast_charge'] = battery_fast_charge
                                        print(f"battery_fast_charge : {battery_fast_charge}")

                                    if "OTHERS" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        battery_other = ''
                                        cnt = 0
                                        for li_tag in row.find_all('td')[0].find_all('li') :
                                            if cnt == 0 :
                                                battery_other = li_tag.get_text(strip=True)
                                            else :
                                                battery_other = battery_other + ", " + li_tag.get_text(strip=True)
                                            cnt += 1     
                                        device_model['battery_other'] = battery_other
                                        print(f"battery_other : {battery_other}")

                                    if "EXTRA" in row.find_all('th')[0].get_text(strip=True).upper() :
                                        battery_extra = ''
                                        cnt = 0
                                        for li_tag in row.find_all('td')[0].find_all('li') :
                                            if cnt == 0 :
                                                battery_extra = li_tag.get_text(strip=True)
                                            else :
                                                battery_extra = battery_extra + ", " + li_tag.get_text(strip=True)
                                            cnt += 1     
                                        device_model['battery_extra'] = battery_extra
                                        print(f"battery_extra : {battery_extra}")  

                        except Exception as ee :
                            print(f"battery parsing Error : {str(ee)}")

                    section_tag = detail_body_tag.find('section', class_='kc-container white container-sheet-software')
                    if section_tag != None :

                        idx = 0
                        for table_tag in section_tag.find_all("table", class_="k-dltable") :  
                            rows = table_tag.find_all('tr') 
                            td_tag = rows[0].find_all('td')[0]
                            for element in td_tag.find_all('div'):
                                element.extract()

                            operating_system  = re.sub(r'\s+', ' ', td_tag.get_text(strip=True).replace('\n', ' ')).strip()
                            device_model['operating_system'] = operating_system
                            print(f"operating_system : {operating_system}")

                else :
                    print('soup.find("div", class_="lay-main") tag not found...')
                    return False, 'soup.find("div", class_="lay-main") tag not found...'
                    
        except Exception as e:
            success = False
            return success, [f"Error occurred: {str(e)}"]

        return success, device_model

if __name__ == "__main__":
    # 사용 예시
    proxies = {
        'http': 'http://12.26.204.100:8080',
        'https': 'http://12.26.204.100:8080'
    }

    model_info = {'device_link' : "https://www.kimovil.com/en/where-to-buy-asus-zenfone-7-6gb", 'device_name' : 'Asus ZenFone 7', 'device_version' : 'Global', 'media_name':'kimovil', 'category':'Asus'}

    crawler = kimovil_sp_spec_detail(proxies)
    success, results = crawler.runCrawling(model_info)

    print(f"{success}, {results}")
