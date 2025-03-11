import requests
import socket
import concurrent.futures

# 프록시 리스트 가져오기
def get_proxies():
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
    response = requests.get(url)
    return response.text.strip().split("\n")

# 프록시 서버의 포트가 열려 있는지 확인
def check_proxy(proxy):
    ip, port = proxy.split(":")
    port = int(port)
    
    try:
        with socket.create_connection((ip, port), timeout=3):  # 3초 내 응답 없으면 타임아웃
            return proxy  # 정상적으로 연결되면 proxy 반환
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None  # 포트가 닫혀있으면 None 반환

# 병렬로 프록시 확인
def filter_working_proxies(proxies):
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_proxy, proxies)

    for proxy in results:
        if proxy:
            working_proxies.append(proxy)
    
    return working_proxies

if __name__ == "__main__":
    proxies = get_proxies()
    print(f"총 {len(proxies)}개의 프록시를 확인 중...")

    working_proxies = filter_working_proxies(proxies)

    print(f"\n🔹 서비스 가능한 프록시 ({len(working_proxies)}개):")
    for proxy in working_proxies:
        print(proxy)
