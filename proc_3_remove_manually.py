
from lguhome.preprocessor import PpReview
from lguhome.preprocessor import PreprocessReview
from lguhome.preprocessor import PpFilterDateAfter

import pandas as pd
import datetime

# Proc2의 워드 분포를 확인하고 불필요한 것은 수동으로 삭제한다.

# 형태소 분석 전
# 주세요 -> 형태소 분석이 잘 안됨. 주세요 -> "주세요." 으로 변경
# ~하면 -> 뛰어쓰기 되어 있으면 명사로 분류되네 





#P_3 : 수작업 삭제
#P_3_1 : 오래된 리뷰 제거



error_files = []

def get_review_fields(src_file):
    df = pd.read_csv(src_file, encoding='utf-8-sig')
    return df.columns
 
def remove_old_sentence(source_file, output_file, date_after, field = 'Date'):
    reviews = PpReview(review_file_name = source_file)
    # 필터되어 출력될 파일, 출력할 헤더값 지정
    processor = PreprocessReview(output_file, headers = get_review_fields(source_file))
    filters = [ PpFilterDateAfter(fromdate=date_after, date_key_string=field)]

    processor.initialize(filters)
    processor.process(reviews)
    processor.finalize()

    if len(reviews.error_file_list)>0:        
        error_files.append(reviews.error_file_list)


date_after = datetime.date(2021,9,1)
source_file = "C:\\Work\\Customer Exprience\\customerexp\\data\\googleplay\\target\\P3_[OTT][wave]_2209162357.csv"
target_file = "C:\\Work\\Customer Exprience\\customerexp\\data\\googleplay\\target\\{}_[OTT][wave]_2209162357.csv"


remove_old_sentence(source_file, target_file.format('P3_1'),date_after)