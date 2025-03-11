import zipfile
import os

def zip_directory(directory, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory)  # 압축 내 경로 유지
                zipf.write(file_path, arcname)
    print(f"{zip_name} 파일이 생성되었습니다.")

if __name__ == '__main__' :
  # 사용 예시
  zip_directory('C:\Temp\project', 'c:\work\project.zip')
