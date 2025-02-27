import sys
import logging
import inspect
from datetime import datetime
import os

class PrintToLogger:
    def __init__(self, log_dir="logs", log_file_prefix="myapp", loglevel="DEBUG"):
        # 로그 디렉토리 확인 및 생성
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 날짜별 로그 파일 이름 생성
        today = datetime.today().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{log_file_prefix}_{today}.log")

        # 로거 설정
        self.logger = logging.getLogger("RedirectedPrint")
        if loglevel == "INFO" :
            self.logger.setLevel(logging.INFO)
        elif loglevel == "DEBUG" :
            self.logger.setLevel(logging.DEBUG)
        elif loglevel == "WARN" :
             self.logger.setLevel(logging.WARN)
        elif loglevel == "ERROR" :
             self.logger.setLevel(logging.ERROR)
        elif loglevel == "FATAL" :
             self.logger.setLevel(logging.FATAL)
        else :
            self.logger.setLevel(logging.NOTSET)

        # 파일 핸들러 설정
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(name)s %(funcName)s %(lineno)d %(levelname)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "[%(asctime)s] %(name)s %(funcName)s %(lineno)d %(levelname)s: %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def write(self, message):
        if message.strip():
            # 호출한 프로그램 코드의 위치를 추적
            frame = inspect.currentframe().f_back
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            funcname = frame.f_code.co_name

            # 로그 메시지에 호출 위치 포함
            self.logger.log(self.logger.level, f"{message.strip()} (called from {filename}, line {lineno}, function {funcname})")

    def flush(self):
        pass  # 표준 출력의 인터페이스 요구사항

# 로그 리다이렉트 함수 정의
def redirect_print_to_log(log_dir="logs", log_file_prefix="myapp", loglevel="DEBUG"):
    sys.stdout = PrintToLogger(log_dir=log_dir, log_file_prefix=log_file_prefix, loglevel=loglevel)

# ----- 사용 예제 -----
if __name__ == "__main__":
    # 로그 파일 경로와 이름 설정
    redirect_print_to_log(log_dir="logs", log_file_prefix="myapp", loglevel="DEBUG")

    # 기존 프로그램 출력
    print("프로그램 시작!")
    print("이 메시지는 로그 파일과 콘솔에 동시에 출력됩니다.")
    for i in range(3):
        print(f"반복 {i + 1}")
    print("프로그램 종료!")
