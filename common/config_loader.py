import os
import yaml
from dotenv import load_dotenv
from util.myutil import get_path_separator

# 환경 변수 로드
load_dotenv()

class ConfigLoader:
    def __init__(self, config_filename="configuration.yaml"):
        # 프로젝트 홈 디렉토리 설정
        # project_home = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        project_home = os.getenv("PROJECT_HOME", os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        # conf 디렉토리 기준으로 설정 파일 경로 지정
        self.config_file = os.path.join(project_home, "conf", config_filename)

        # 마지막 수정 시간 추적
        self.last_modified_time = None
        self.config = {}
        self._load_config()

    def _load_config(self):
        """YAML 파일 로드 및 환경별 설정 병합."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        current_modified_time = os.path.getmtime(self.config_file)

        # 파일이 변경되지 않았다면 로드하지 않음
        if self.last_modified_time == current_modified_time:
            return

        # 파일 변경 시간 갱신 및 설정 로드
        self.last_modified_time = current_modified_time
        with open(self.config_file, "r", encoding='utf-8') as f:
            full_config = yaml.safe_load(f)

        # 기본 및 환경별 설정 병합
        environment = os.getenv("ENVIRONMENT", full_config["default"]["Environment"])
        default_config = full_config.get("default", {})
        env_config = full_config.get(environment, {})
        self.config = {**default_config, **env_config}

    def get(self, *keys, default=None):
        """
        계층 구조에서 특정 항목을 동적으로 가져옴.
        keys: 탐색할 키 경로를 나타내는 가변 인수.
        default: 키가 없을 때 반환할 기본값.
        """
        value = self.config
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                if default is not None:
                    return default
                raise KeyError(f"Key path '{' -> '.join(keys)}' not found in configuration.")
            value = value[key]
        return value
    
    def get_path_separator(self) :
        return get_path_separator()