from common.config_loader import ConfigLoader
from crawler.kimovil_new_sp_list import crawling_new_sp_list

config = ConfigLoader()

path_separator = config.get_path_separator()
project_home = config.get("project_home")

crawling_out_path = config.get("crawling", "out_path")
use_connection_nm = config.get("crawling", "use_connection_nm")
load_database_type = config.get("crawling", "load_database_type")

kimovil_new_sp_list_target_nm = config.get("crawling", "kimovil", "new_sp_list_target")

out_file_nm = f'{project_home}{path_separator}{crawling_out_path}{path_separator}{kimovil_new_sp_list_target_nm}'
print(out_file_nm)

crawling_new_sp_list(out_file_nm)
