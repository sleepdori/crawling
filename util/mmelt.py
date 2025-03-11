import pandas as pd

class mmelt:
    def __init__(self, id_col_vars, filter_keyword=None):
        """
        행렬 전환 클래스 초기화.

        :param id_col_vars: 고유 식별자 역할을 할 컬럼 이름 (예: 'device_seq')
        :param filter_keyword: 피봇팅할 그룹 컬럼에 포함되어야 할 문자열 (예: 'temp')
        """
        self.id_col_vars = id_col_vars
        self.filter_keyword = filter_keyword

    def mmelt(self, df) :
        """
        동일한 머리말을 가지고 뒤에 1,2,3,4와 같은 일련번호를 가진 컬럼을 행렬 전환.

        :param df: 변환할 DataFrame
        :return: 변환된 DataFrame
        """
        # 컬럼 이름에서 그룹과 인덱스를 추출
        melted = pd.melt(
            df,
            id_vars=[self.id_col_vars],
            var_name='attribute',
            value_name='value'
        )

        melted['group'] = melted['attribute'].str.extract(r'([a-zA-Z_]+)')
        melted['index'] = melted['attribute'].str.extract(r'(\d+)$')

        # 필터 키워드가 제공된 경우 그룹 필터링
        if self.filter_keyword:
            filtered_melted = melted[melted['group'].str.contains(self.filter_keyword, na=False)]
        else:
            filtered_melted = melted

        # 데이터 피벗
        pivoted = filtered_melted.pivot(index=[self.id_col_vars, 'index'], columns='group', values='value').reset_index()

        # 컬럼 이름 정리 (피봇된 컬럼에서만 '_' 제거)
        pivoted.columns.name = None
        pivoted.columns = [
            col.replace('_', '') if col not in [self.id_col_vars, 'index'] else col
            for col in pivoted.columns
        ]
        pivoted = pivoted.sort_values([self.id_col_vars, 'index']).drop(columns=['index'])

        # 필터링되지 않은 컬럼 제외
        excluded_columns = [col for col in df.columns if col not in pivoted.columns and col != self.id_col_vars]
        final_df = df.drop(columns=excluded_columns, errors='ignore')

        # 피벗 결과와 병합
        final_df = pd.merge(final_df, pivoted, on=self.id_col_vars, how='outer')

        return final_df
