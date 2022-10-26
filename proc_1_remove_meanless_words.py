
from lguhome.preprocessor import PpReview
from lguhome.preprocessor import PreprocessReview
from lguhome.preprocessor import PpFilterDateBetween
from lguhome.preprocessor import PpFilterDateAfter
from lguhome.preprocessor import PpFilterRemoveSpecialCharAndShortSentence
from lguhome.preprocessor import PpFilterEnglish
from lguhome.preprocessor import PpFilterReplace
from lguhome.preprocessor import PpFilterUpperCase
from lguhome.preprocessor import get_review_fields

import pandas as pd

error_files = []


 
def remove_special_char_meanless_sentence(source_file, output_file, field = ['Review']):
    reviews = PpReview(review_file_name = source_file)
    # 필터되어 출력될 파일, 출력할 헤더값 지정
    processor = PreprocessReview(output_file, headers = get_review_fields(source_file))
    filters = [ PpFilterRemoveSpecialCharAndShortSentence(field),\
                 PpFilterEnglish(field, no_korean_char_filtering_limit=2),\
                    PpFilterReplace(field[0], "[.]{2,}",".",True),PpFilterReplace(field[0], "[?]{2,}","?",True), \
                        PpFilterUpperCase(field) ]

    processor.initialize(filters)
    processor.process(reviews)
    processor.finalize()

    if len(reviews.error_file_list)>0:        
        error_files.append(reviews.error_file_list)

#P_X : 특수문자 제거
#P_X_2 : 영어문장 제거

source_file = "C:\\Work\\Customer Exprience\\customerexp\\data\\googleplay\\target\\googleplay_reviews_[OTT][wave]kr.co.captv.pooqV2_2209162357.csv"
target_file = "C:\\Work\\Customer Exprience\\customerexp\\data\\googleplay\\target\\P1_2_[OTT][wave]_2209162357.csv"


remove_special_char_meanless_sentence(source_file, target_file)


print('--Error--------------------------')
print(error_files)