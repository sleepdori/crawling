import requests
import json
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta

def gamarena_new_sp_list(output_file_nm) :
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
        response = requests.get(url)

        # 응답 확인
        if response.status_code == 200:
            print(f"[INFO] {brand_name} 페이지 로드 성공")
            # BeautifulSoup으로 HTML 파싱
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

        time.sleep(10)  # 요청 간 딜레이 추가
            
        print(f"[INFO] 모든 링크 정보가 {output_file}에 저장되었습니다.")


    
