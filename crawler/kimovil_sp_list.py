import cloudscraper
import json
import time
from bs4 import BeautifulSoup
import re
import base64

all_brand = [
                  ["360"             ,"360"                ]
                , ["acer"            ,"Acer"               ]
                , ["aermoo"          ,"Aermoo"             ]
                , ["agm"             ,"AGM"                ]
                , ["alcatel"         ,"Alcatel"            ]
                , ["allcall"         ,"Allcall"            ]
                , ["allview"         ,"Allview"            ]
                , ["amigoo"          ,"Amigoo"             ]
                , ["amoi"            ,"Amoi"               ]
                , ["apple"           ,"Apple"              ]
                , ["archos"          ,"Archos"             ]
                , ["asus"            ,"Asus"               ]
                , ["axgio"           ,"Axgio"              ]
                , ["black-shark"     ,"BlackShark"         ]
                , ["blackberry"      ,"BlackBerry"         ]
                , ["blackview"       ,"Blackview"          ]
                , ["blu"             ,"BLU"                ]
                , ["bluboo"          ,"Bluboo"             ]
                , ["bq"              ,"BQ"                 ]
                , ["bsimb"           ,"Bsimb"              ]
                , ["cagabi"          ,"Cagabi"             ]
                , ["cat"             ,"Cat"                ]
                , ["caterpillar"     ,"Caterpillar"        ]
                , ["centric"         ,"Centric"            ]
                , ["china-mobile"    ,"ChinaMobile"        ]
                , ["cong"            ,"Cong"               ]
                , ["coolpad"         ,"Coolpad"            ]
                , ["cubot"           ,"Cubot"              ]
                , ["Dakele"          ,"Dakele"             ]
                , ["doogee"          ,"Doogee"             ]
                , ["doopro"          ,"Doopro"             ]
                , ["eandl"           ,"E&L"                ]
                , ["e-l"             ,"E&L"                ]
                , ["ecoo"            ,"Ecoo"               ]
                , ["elephone"        ,"Elephone"           ]
                , ["energizer"       ,"Energizer"          ]
                , ["energy-sistem"   ,"Energy"             ]
                , ["essential"       ,"Essential"          ]
                , ["estar"           ,"EStar"              ]
                , ["faea"            ,"Faea"               ]
                , ["fairphone"       ,"Fairphone"          ]
                , ["flipkart"        ,"Flipkart"           ]
                , ["auto"            ,"Fossibot"           ]
                , ["geotel"          ,"Geotel"             ]
                , ["gigabyte"        ,"Gigabyte"           ]
                , ["gigaset"         ,"Gigaset"            ]
                , ["gionee"          ,"Gionee"             ]
                , ["gome"            ,"Gome"               ]
                , ["google"          ,"Google"             ]
                , ["goophone"        ,"Goophone"           ]
                , ["gretel"          ,"Gretel"             ]
                , ["hafury"          ,"Hafury"             ]
                , ["haier"           ,"Haier"              ]
                , ["hike"            ,"Hike"               ]
                , ["hisense"         ,"HiSense"            ]
                , ["hmd"             ,"HMD"                ]
                , ["homtom"          ,"HomTom"             ]
                , ["honor"           ,"Honor"              ]
                , ["hotwav"          ,"Hotwav"             ]
                , ["hp"              ,"HP"                 ]
                , ["htc"             ,"HTC"                ]
                , ["huawei"          ,"Huawei"             ]
                , ["i-kall"          ,"IKall"              ]
                , ["iiif150"         ,"iiiF150"            ]
                , ["ila"             ,"iLA"                ]
                , ["iman"            ,"iMan"               ]
                , ["inew"            ,"iNew"               ]
                , ["infinix"         ,"Infinix"            ]
                , ["infocus"         ,"InFocus"            ]
                , ["innjoo"          ,"InnJoo"             ]
                , ["innos"           ,"Innos"              ]
                , ["intex"           ,"Intex"              ]
                , ["iocean"          ,"iOcean"             ]
                , ["irulu"           ,"iRULU"              ]
                , ["itel"            ,"itel"               ]
                , ["iuni"            ,"IUNI"               ]
                , ["ivoomi"          ,"iVooMi"             ]
                , ["jesy"            ,"Jesy"               ]
                , ["jiake"           ,"Jiake"              ]
                , ["jiayu"           ,"Jiayu"              ]
                , ["karbonn"         ,"Karbonn"            ]
                , ["kazam"           ,"Kazam"              ]
                , ["keecoo"          ,"Keecoo"             ]
                , ["kenxinda"        ,"Kenxinda"           ]
                , ["kingsing"        ,"KingSing"           ]
                , ["kingzone"        ,"KingZone"           ]
                , ["kodak"           ,"Kodak"              ]
                , ["kolina"          ,"Kolina"             ]
                , ["koolnee"         ,"Koolnee"            ]
                , ["landvo"          ,"Landvo"             ]
                , ["laude"           ,"Laude"              ]
                , ["lava"            ,"Lava"               ]
                , ["leagoo"          ,"Leagoo"             ]
                , ["letv"            ,"LeBest(LeEco/LeTV)" ]
                , ["leica"           ,"Leica"              ]
                , ["lenovo"          ,"Lenovo"             ]
                , ["leotec"          ,"Leotec"             ]
                , ["leree"           ,"LeRee"              ]
                , ["lg"              ,"LG"                 ]
                , ["ly-mobile"       ,"Ly"                 ]
                , ["lyf"             ,"Lyf"                ]
                , ["m-horse"         ,"M-Horse"            ]
                , ["mnet"            ,"M-Net"              ]
                , ["mann"            ,"Mann"               ]
                , ["maze"            ,"Maze"               ]
                , ["meiigoo"         ,"Meiigoo"            ]
                , ["meitu"           ,"Meitu"              ]
                , ["meizu"           ,"Meizu"              ]
                , ["micromax"        ,"Micromax"           ]
                , ["microsoft"       ,"Microsoft"          ]
                , ["mijue"           ,"Mijue"              ]
                , ["milai"           ,"Milai"              ]
                , ["mlais"           ,"Mlais"              ]
                , ["morefine"        ,"Morefine"           ]
                , ["motorola"        ,"Motorola"           ]
                , ["mpie"            ,"Mpie"               ]
                , ["mstar"           ,"Mstar"              ]
                , ["multilaser"      ,"Multilaser"         ]
                , ["mywigo"          ,"MyWigo"             ]
                , ["neken"           ,"Neken"              ]
                , ["neo"             ,"Neo"                ]
                , ["newman"          ,"Newman"             ]
                , ["nio"             ,"NIO"                ]
                , ["no1"             ,"NO.1"               ]
                , ["noa"             ,"Noa"                ]
                , ["nokia"           ,"Nokia"              ]
                , ["nomu"            ,"Nomu"               ]
                , ["nothing"         ,"Nothing"            ]
                , ["nubia"           ,"Nubia"              ]
                , ["nzone"           ,"NZone"              ]
                , ["oneplus"         ,"OnePlus"            ]
                , ["oppo"            ,"Oppo"               ]
                , ["otium"           ,"Otium"              ]
                , ["oukitel"         ,"Oukitel"            ]
                , ["palm"            ,"Palm"               ]
                , ["panasonic"       ,"Panasonic"          ]
                , ["pantech"         ,"Pantech"            ]
                , ["pepsi"           ,"Pepsi"              ]
                , ["phicomm"         ,"Phicomm"            ]
                , ["philips"         ,"Philips"            ]
                , ["phonemax"        ,"Phonemax"           ]
                , ["plunk"           ,"Plunk"              ]
                , ["poco"            ,"POCO"               ]
                , ["pomp"            ,"Pomp"               ]
                , ["poptel"          ,"Poptel"             ]
                , ["positivo"        ,"Positivo"           ]
                , ["pptv"            ,"PPTV"               ]
                , ["prestigio"       ,"Prestigio"          ]
                , ["qiku"            ,"Qiku"               ]
                , ["quantum"         ,"Quantum"            ]
                , ["ramos"           ,"Ramos"              ]
                , ["razer"           ,"Razer"              ]
                , ["realme"          ,"realme"             ]
                , ["runbo"           ,"Runbo"              ]
                , ["samsung"         ,"Samsung"            ]
                , ["sharp"           ,"Sharp"              ]
                , ["silent-circle"   ,"SilentCircle"       ]
                , ["siswoo"          ,"Siswoo"             ]
                , ["smartisan"       ,"Smartisan"          ]
                , ["snopow"          ,"Snopow"             ]
                , ["sony"            ,"Sony"               ]
                , ["sony-ericsson"   ,"SonyEricsson"       ]
                , ["star"            ,"Star"               ]
                , ["swipe"           ,"Swipe"              ]
                , ["tcl"             ,"TCL"                ]
                , ["tecno"           ,"Tecno"              ]
                , ["tengda"          ,"Tengda"             ]
                , ["thl"             ,"THL"                ]
                , ["tianhe"          ,"Tianhe"             ]
                , ["timmy"           ,"Timmy"              ]
                , ["tp-link"         ,"TP-Link"            ]
                , ["ubro"            ,"Ubro"               ]
                , ["uhans"           ,"Uhans"              ]
                , ["uhappy"          ,"Uhappy"             ]
                , ["uimi"            ,"Uimi"               ]
                , ["ukozi"           ,"Ukozi"              ]
                , ["ulefone"         ,"Ulefone"            ]
                , ["umi"             ,"UMi"                ]
                , ["umidigi"         ,"UMiDIGI"            ]
                , ["unihertz"        ,"Unihertz"           ]
                , ["vargo"           ,"Vargo"              ]
                , ["vernee"          ,"Vernee"             ]
                , ["viewsonic"       ,"ViewSonic"          ]
                , ["vivo"            ,"vivo"               ]
                , ["vkworld"         ,"VKworld"            ]
                , ["voto"            ,"Voto"               ]
                , ["VPhone"          ,"VPhone"             ]
                , ["vsmart"          ,"Vsmart"             ]
                , ["weimei"          ,"Weimei"             ]
                , ["wico"            ,"Wico"               ]
                , ["wiko"            ,"Wiko"               ]
                , ["wileyfox"        ,"Wileyfox"           ]
                , ["wolder"          ,"Wolder"             ]
                , ["woxter"          ,"Woxter"             ]
                , ["xiaomi"          ,"Xiaomi"             ]
                , ["xolo"            ,"Xolo"               ]
                , ["yota-devices"    ,"YotaDevices"        ]
                , ["yu"              ,"YU"                 ]
                , ["zoji"            ,"Zoji"               ]
                , ["zopo"            ,"Zopo"               ]
                , ["zte"             ,"ZTE"                ]
                , ["zuk"             ,"Zuk"                ]
            ]

def crawling_sp_list(output_file_nm) :
    proxies = {
        'http': 'http://12.26.204.100:8080',
        'https': 'http://12.26.204.100:8080'
    }
    # Cloudflare 보안 우회를 위한 CloudScraper 생성
    scraper = cloudscraper.create_scraper()

    # 크롤링 대상 URL
    base_url = "https://www.kimovil.com/en/compare-smartphones/order.dm+unveiledDate,i_m+code.Global:Intern:Americ:NA:Latam:BR:CN:IN:Sudasi:KR:JP,i_b+slug.{},page.{}"
    output_file = output_file_nm
    all_links = []  # 모든 페이지의 링크 정보를 저장할 딕셔너리
    model_idx = 0
    for url_tag , brand_nm in all_brand :
        print(f"url tag : {url_tag}, brand_nm : {brand_nm}")
        
        page_count = 1
        while True:
            url = base_url.format(url_tag, page_count)
            print(f"[INFO] 페이지 호출 중: {url}")

            # 삼성 내부에서 수행시
            response = scraper.get(url, proxies=proxies)

            # 삼성 외부에서 수행시
            # response = self.scraper.get(url)

            cf_ray = response.headers.get("CF-RAY")
            
            if cf_ray is None :
                print(f"CF-RAY N: {cf_ray}")
                scraper.close()
                scraper = cloudscraper.create_scraper()
            else :
                print(f"CF-RAY Y: {cf_ray}, {type(cf_ray)}")

            while response.status_code != 200:
                if response.status_code == 404 :
                    return False, "404 Not Found.."
                
                time.sleep(10)

                # 삼성 내부에서 수행시
                response = scraper.get(url, proxies=proxies)

                # 삼성 외부에서 수행시
                # response = self.scraper.get(url)

                cf_ray = response.headers.get("CF-RAY")

                if cf_ray is None :
                    print(f"CF-RAY N: {cf_ray}")
                    scraper.close()
                    scraper = cloudscraper.create_scraper()
                else :
                    print(f"CF-RAY Y: {cf_ray}, {type(cf_ray)}")
                    print(f"Retry request url :{url} ===== response code : {response.status_code}")

            # 응답 확인
            if response.status_code == 200:
                print(f"[INFO] 페이지 {page_count} 로드 성공")
                # BeautifulSoup으로 HTML 파싱
                soup = BeautifulSoup(response.text, "html.parser")

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
                                    'media_name' : 'kimovil',
                                    'brand_name' : brand_nm,
                                    'device_name': device_name,
                                    'device_link': device_link,
                                    'device_version': device_version,
                                    'device_memory_size': device_memory_size,
                                    'device_storage_size': device_storage_size,
                                    'device_available': device_available.strip()
                                }

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
                                device_info['device_seq'] = model_idx 

                                all_links.append(device_info)
                                model_idx += 1

                else:
                    print(f"[INFO] 페이지 {page_count}에 더 이상 'kiid_' 데이터가 없습니다. 크롤링을 종료합니다.")
                    break
            else:
                print(f"[ERROR] 페이지 {page_count} 로드 실패. 상태 코드: {response.status_code}, {response}")
                break

            print(f"[INFO] 페이지 {page_count} 크롤링 완료. Model Count : {model_idx}")

            # JSON 파일로 저장
            print(f"[INFO] 총 {len(all_links)}개의 장치 정보를 저장합니다.")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_links, f, ensure_ascii=False, indent=4)    

            time.sleep(10)  # 요청 간 딜레이 추가
            page_count += 1

        print(f"[INFO] 모든 링크 정보가 {output_file}에 저장되었습니다.")
    
    time.sleep(5)  # 요청 간 딜레이 추가
