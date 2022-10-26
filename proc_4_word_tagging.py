from lguhome.preprocessor import get_review_fields
from lguhome.preprocessor import PpFilterReplace
from lguhome.preprocessor import PreprocessReview
from lguhome.preprocessor import PpFilterAppendPeriod
from lguhome.preprocessor import PpReview
from lguhome.preprocessor import CustomizedKkma
from lguhome.preprocessor import KkmaTokenizer
from lguhome.preprocessor import post_processor_AN_NNG
from lguhome.preprocessor import post_processor_replace
from lguhome.preprocessor import load_dictionary

from konlpy.tag import Kkma

import pandas as pd
import csv
import os

error_files = []
stop_words = []
pass_words = []
pass_tags = []


def update_pos_dictionary(w,d):
    if w not in d:
        d.update({w:1})
    else:
        d[w] += 1

def correct_typo(source_file, output_file, typo_dict, field = ['Review']):
    reviews = PpReview(review_file_name = source_file)
    # 필터되어 출력될 파일, 출력할 헤더값 지정
    processor = PreprocessReview(output_file, headers = get_review_fields(source_file))
    filters = [ PpFilterReplace(field[0], k,typo_dict[k],False) for k in typo_dict ]
    filters.append( PpFilterAppendPeriod(field) )
    processor.initialize(filters)
    processor.process(reviews)
    processor.finalize()

    if len(reviews.error_file_list)>0:        
        error_files.append(reviews.error_file_list)




def generate_postag(source_file,target_file, post_process_dict, post_processor_pos, search_word = None):
    df = pd.read_csv(source_file, encoding='utf-8-sig')
    tagging_result = []
    dictionary = {}

    search_result = []
 
    analyzer = CustomizedKkma(Kkma(), post_process_dict, post_processor_pos,stop_words,pass_words, pass_tags, join = True, filtering = False)

    for s in df.Review:
        tag_list = analyzer.tokenizer(s)
    
        pos_tag_sentence = "|".join(tag_list)
        if search_word != None and search_word in tag_list:
            search_result.append(pos_tag_sentence)
        
        tagging_result.append([s,pos_tag_sentence])
        
        for word_pos in pos_tag_sentence.split('|'):
            update_pos_dictionary(word_pos, dictionary)
            
    with open(target_file, 'w' , encoding='utf-8-sig') as csv_out:
        csv_writer = csv.writer(csv_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        
        for k in tagging_result:
            csv_writer.writerow([k[0],k[1]])
    
    with open(target_file+"_dict.csv", 'w' , encoding='utf-8-sig') as csv_out:
        csv_writer = csv.writer(csv_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        
        for k in dictionary:
            csv_writer.writerow([k,dictionary[k]])
    
    if search_word:
        with open(target_file+"_search.csv", 'w' , encoding='utf-8-sig') as csv_out:
            csv_writer = csv.writer(csv_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            
            for k in search_result:
                csv_writer.writerow([k])



def refine_postag(source_file, target_file, post_process_dict, post_processor_pos, search_word = None ):
    df = pd.read_csv(source_file, encoding='utf-8-sig', header=None)
    df.columns = ['Original','PosTag']
    analyzer = CustomizedKkma(KkmaTokenizer(), post_process_dict, post_processor_pos,stop_words,pass_words, pass_tags, join = True, filtering = True)
 
    df['Filtered'] = df.PosTag.map(analyzer.tokenizer) 
    df.drop(['PosTag'], axis = 1, inplace=True)
    df.to_csv(target_file, encoding='utf-8-sig', header=False, index=False, quoting=csv.QUOTE_ALL)
    


##################################################################################################
# Start
work_folder = "C:\\Work\\Customer Exprience\\customerexp\\data\\googleplay\\target"
source_file_format = work_folder + os.sep + "{}_[OTT][wave]_2209162357.csv"
target_file_format = work_folder + os.sep + "{}_[OTT][wave]_2209162357.csv"
dict_file_format   = work_folder + os.sep + "{}.csv"

stop_words = ['아/VV','들이/VV','다그/VV','어/VV','그/VV','저/VV','드/VV','느/VV','시/VV',"블/VV","결하/VV"]
pass_words = ['앱',"돈","안","탭", "별", "잘", "왜", "안", "못"]
pass_tags = ['NNG','MAG','VV','VX',"VA","VXA","VXV","XSV"]


post_process_typo = load_dictionary(dict_file_format.format("typo_netflix"))
post_process_dict_data = load_dictionary(dict_file_format.format("dict_netflix"))
post_process_pos_data = load_dictionary(dict_file_format.format("pos_netflix"))

post_process_dict = {  key_pos:post_processor_replace(replaced_word=post_process_dict_data[key_pos]) for key_pos in post_process_dict_data  }
post_process_dict.update({'안/NNG':post_processor_AN_NNG()})

post_processor_pos = [ (key_pos,post_process_pos_data[key_pos] ) for key_pos in post_process_pos_data  ]

print("1--------------")
#correct_typo(source_file_format.format("P3"), target_file_format.format("P4_1_1"), post_process_typo)
print("2--------------")
generate_postag(source_file_format.format("P4_1_1"), target_file_format.format('P4_2'), post_process_dict, post_processor_pos)
print("3----------------")
refine_postag(source_file_format.format("P4_2"), target_file_format.format('P4_3'), post_process_dict, post_processor_pos)