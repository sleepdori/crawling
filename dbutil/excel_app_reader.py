import xlwings as xw
import pandas as pd

class ExcelAppReader:
    def __init__(self, file_name, sheet_index=-1, sheet_name="", start_position='A1', DRM=False):
        """
        Excel 파일을 읽어오는 클래스를 초기화합니다.

        :param file_name: 읽을 Excel 파일 경로
        :param sheet_index: 기본 시트 인덱스 (기본값: -1, 마지막 시트)
        :param sheet_name: 기본 시트 이름 (지정하지 않을 시 인덱스를 사용)
        :param start_position: 읽기 시작 위치 (기본값: 'A1')
        :param DRM: DRM 보호 여부 (True일 경우 xlwings로 처리)
        """
        self.file_name = file_name
        self.sheet_index = sheet_index
        self.sheet_name = sheet_name
        self.start_position = start_position
        self.DRM = DRM

        # Excel 애플리케이션 객체 생성
        self.app = None
        self.wb = None

        if self.DRM:
            try:
                self.app = xw.App(visible=False)
                self.wb = xw.Book(self.file_name)
            except Exception as e:
                self.unload_app()
                raise ValueError(f"Excel 파일을 열 수 없습니다: {e}")

    def load_file(self, sheet_index=-1, sheet_name="", start_position=None, dtype=None):
        """
        Excel 파일이나 시트를 읽어옵니다.

        :param sheet_index: 읽을 시트 인덱스
        :param sheet_name: 읽을 시트 이름
        :param start_position: 읽기 시작 위치 (None일 경우 기본값 사용)
        :param dtype: 읽기 데이터 타입 (str로 설정하면 문자열로 읽음)
        :return: DataFrame으로 반환된 데이터
        """
        try:
            # DRM 여부에 따른 처리
            if self.DRM:
                # 시트 선택
                if sheet_name:
                    sheet = self.wb.sheets[sheet_name]
                elif sheet_index >= 0:
                    sheet = self.wb.sheets[sheet_index]
                else:
                    sheet = self.wb.sheets[self.sheet_index]

                # 시작 위치 설정
                start_idx = start_position if start_position else self.start_position

                # 데이터 읽기 - .current_region.value 사용
                data = sheet.range(start_idx).current_region.value

                # 데이터프레임 변환
                df = pd.DataFrame(data)
                df.columns = df.iloc[0]  # 첫 번째 행을 컬럼 이름으로 사용
                df = df[1:]  # 첫 번째 행 제거

                for col in df.columns:
                    try:
                        # 열의 모든 값이 숫자인지 확인
                        if pd.to_numeric(df[col], errors='coerce').notna().all():
                            # 값이 모두 정수라면 Int64로 변환
                            if (pd.to_numeric(df[col], errors='coerce') % 1 == 0).all():
                                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')  # NaN을 허용하는 정수형
                            else:
                                df[col] = pd.to_numeric(df[col], errors='coerce')  # 실수형으로 변환
                        else:
                            # 숫자와 문자가 섞인 경우 처리
                            df[col] = df[col].astype(str)
                    except Exception as e:
                        print(f"열 {col} 처리 중 오류 발생: {e}")

                return df.reset_index(drop=True)

            else:
                # DRM이 없으면 pandas의 Excel 읽기 사용
                if self.file_name.endswith('.xlsx'):
                    return pd.read_excel(self.file_name, engine='openpyxl', dtype=dtype)
                elif self.file_name.endswith('.csv'):
                    return pd.read_csv(self.file_name, dtype=dtype)
                else:
                    raise ValueError("지원되지 않는 파일 형식입니다.")

        except Exception as e:
            raise ValueError(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    def load_sheet(self, sheet_index=-1, sheet_name="", start_position=None, dtype=None):
        """
        특정 시트만 읽어옵니다.

        :param sheet_index: 읽을 시트 인덱스
        :param sheet_name: 읽을 시트 이름
        :param start_position: 읽기 시작 위치 (None일 경우 기본값 사용)
        :param dtype: 읽기 데이터 타입 (str로 설정하면 문자열로 읽음)
        :return: DataFrame으로 반환된 데이터
        """
        return self.load_file(sheet_index, sheet_name, start_position, dtype)

    def unload_app(self):
        """
        Excel 애플리케이션 종료
        """
        if self.DRM:
            try:
                if self.wb:
                    self.wb.close()
                if self.app:
                    self.app.kill()
            except Exception as e:
                print(f"Excel 애플리케이션을 종료하는 중 오류 발생: {e}")
            finally:
                self.app = None
                self.wb = None

    def __del__(self):
        """
        객체 소멸 시 Excel 애플리케이션 종료
        """
        self.unload_app()

if __name__ == "__main__":
    # 사용 예제
    file_name = r"C:\work\project\import\test.xlsx"
    sheet_name = "Sheet1"
    start_position = "A1"

    reader = ExcelAppReader(file_name, sheet_name=sheet_name, start_position=start_position, DRM=True)
    try:
        df = reader.load_sheet(dtype=None) # 데이터를 문자열로 읽기
        print(df.head())
    except ValueError as e:
        print(f"오류 발생: {e}")
    finally:
        reader.unload_app()