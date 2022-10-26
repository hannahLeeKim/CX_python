from abc import *
import csv
import datetime
from genericpath import isdir
import re
import glob
import os
import numpy
import numpy as np
import pandas as pd


class post_processor_replace:
    def __init__(self, replaced_word):
        self.__replaced_word = replaced_word
    def apply(self, next_token):
        return [self.__replaced_word]

class post_processor_AN_NNG:
    def apply(self, next_token):
        if next_token.find("/VV") !=-1:
            return ['안/MAG']
    
        elif next_token in ['되/XSV', '하/XSV']:
            return ['안/MAG']

        return []       # 무시



def load_dictionary(dictionary_path):
    df = pd.read_csv(dictionary_path, encoding='utf-8-sig', header=None)
    df.columns = ["old","new"]
    df.set_index("old",inplace=True)
    return df["new"].to_dict()

#from hanspell import spell_checker
def get_review_fields(src_file):
    df = pd.read_csv(src_file, encoding='utf-8-sig')
    return df.columns

def remove_nul_char(src, dst):
    with open(src, mode="r", encoding='utf-8-sig') as src_file:
        with open(dst, mode="w", encoding = 'utf-8-sig') as dst_file:
            src_lines = src_file.readlines()
            
            for src_line in src_lines:
                dst_file.writelines(src_line.replace('\x00',''))    

def apply_in_a_folder(folder_path, job, filter = None):

    glob_path = folder_path + f"{os.sep}*"
    file_list = glob.glob(glob_path)

    for file in file_list :
        if os.path.isdir(file):
            print(f"** {file} is skipped. it's not file but directory" )    
            continue
        print(f'** {file} is chosen.' )
        if filter:
            if file.find(filter) !=-1:
                job(file, file.split(f'{os.sep}')[-1])
        else:    
            job(file, file.split(f'{os.sep}')[-1])

    
def change_header_csv_file(src, dst, new_header):
    df = pd.read_csv(src)

    df.columns = new_header
    df.to_csv(dst, index = False, encoding = "utf-8-sig", quotechar='"', quoting=csv.QUOTE_ALL)

def count_korean_char_in(sentence):
    cnt = 0
    for c in sentence:
        if ord(c) >= ord('가') and ord(c) <= ord('힣'):
            cnt += 1

    return cnt

def is_korean_sentence(sent, charlimit = 1, printlimit=2):
    cnt = count_korean_char_in(sent)
    if cnt <= printlimit:
        print(f" [korean:{cnt}]{sent}")
    return cnt>charlimit




class HeaderChanger:
    def __init__(self, dst_path, new_header):
        self.__dst_path = dst_path
        self.__header = new_header

    def change(self, source_path, filename):
        if filename.find(".csv")!=-1 :
            change_header_csv_file(source_path, self.__dst_path+os.sep+filename, self.__header)
        else:
            print(f"{filename} skipped")


class PreprocessReview:
    def __init__(self, output_file_name, headers, doWriteResult = True):
        self.__output_file_name = output_file_name
        self.__output_file = None
        self.__headers = headers
        self.__filters = None
        self.__doWriteResult = doWriteResult

    def initialize(self, filters):
        
        self.__csv_writer = None

        if self.__doWriteResult:
            self.__output_file = open(self.__output_file_name, 'w' , encoding='utf-8-sig')
            self.__csv_writer = csv.DictWriter(self.__output_file, fieldnames=self.__headers, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            self.__csv_writer.writeheader()
        self.__filters = filters

    def process(self, review):
        processed = review.do(self)
        print(f'#{processed}  preprocessed')

    def process_review_row(self, row):
        is_valid = True
        result = row
        for f in self.__filters:
            valid, filtered = f.filter(result)
            if valid:
                result = filtered
            else:
                is_valid = False
                break
        if is_valid and self.__doWriteResult:
            self.__csv_writer.writerow(result)  

        return is_valid  

    def finalize(self):
        if self.__output_file:
            self.__output_file.close()

class PpReview:
    def __init__(self, review_file_name):
        self.__input_file_name = review_file_name
        self.__reader = None
        self.error_file_list = []
        
    def do(self, processor):
        num_of_process = 0
        i = 0
#       print(self.__input_file_name)
        with open(self.__input_file_name, "r", encoding="utf-8-sig") as file_in:
            
                reader = csv.DictReader(file_in, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                try:
                    for i,r in enumerate(reader):
        #                print(r)
                        if processor.process_review_row(r):
                            num_of_process += 1
                except Exception as e:
                    print(f"[ERROR] Read error {self.__input_file_name} in {i+2}")
                    self.error_file_list.append(self.__input_file_name)
                    print(e)

        return num_of_process

    def close(self):
        self.__reader = None


class PpFilter(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, row):
        return False, dict()


class PpFilterReplace(PpFilter):
    def __init__(self, key_string, search_word, replace_word, search_word_is_reqular_exp = False):
        self.__search_word = search_word
        self.__key_string = key_string
        self.__replace_word = replace_word
        self.__search_word_is_reqular_exp = search_word_is_reqular_exp

    def filter(self, row):
        is_found = False
        target_string = row[self.__key_string ]
        if self.__search_word_is_reqular_exp:            
            row[self.__key_string] = re.sub(self.__search_word,self.__replace_word, target_string)       
        else:
            if target_string.find(self.__search_word)!=-1:
                is_found = True
                row[self.__key_string] = target_string.replace(self.__search_word,self.__replace_word)
        return True, row

class PpFilterSpellCheck(PpFilter):
    def __init__(self, key_string):
        self.__key_string = key_string
        self.__spacer =  Spacing()
        print("Loading spacing...")
        
    def filter(self, row):
        
        spacing_sentence = self.__spacer(row[self.__key_string])
        
        print(f"[Orin] {row[self.__key_string]}")
        print("-------------------")
        print(f"[Checked] {spacing_sentence}")

        if spacing_sentence == row[self.__key_string]:
            print("Skip")
            return True, row

        yes_no = input("store(y/n/a)?")
        if yes_no =='y':
            row[self.__key_string] = spacing_sentence
            print("stored\n")
        elif yes_no=='a':
            msg = input("new message=")
            row[self.__key_string] = msg
        return True, row

class PpFilterDate(PpFilter):
    
    def __init__(self, date_key_string):
        super().__init__()
        self.__date_key_string = date_key_string

    def get_date(self, row):        
        date_time_token = row[self.__date_key_string].replace('T',' ').split()
        date_token = date_time_token[0].split('-')
        if len(date_token) == 2:
            date_token.append('01')
        return datetime.date(int(date_token[0]), int(date_token[1]), int(date_token[2]))

class PpFilterDateBetween(PpFilterDate):

    def __init__(self, fromdate , todate, date_key_string = 'DATE'):
        super().__init__(date_key_string)
        self.__from = fromdate
        self.__to = todate
        self.__date_key_string = date_key_string

    def filter(self, row):
        dt = self.get_date(row)
        return (dt >=self.__from and dt < self.__to), row

class PpFilterDateAfter(PpFilterDate):

    def __init__(self, fromdate, date_key_string = 'DATE'):
        super().__init__(date_key_string)
        self.__from = fromdate
   
    def filter(self, row):
        return (self.get_date(row)>=self.__from), row

class PpFilterRemoveSpecialCharAndShortSentence(PpFilter):

    def __init__(self, applying_fields, do_remove_Emoticon = True, above_number_of_words = 1, special_charset='[-=_+,#/\\:;&^$#!÷♧♀°⊙○●◇♡♥☆★%^@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]|[ㄱ-ㅎ]|[ㅏ-ㅣ]'):  #  '[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]'
        super().__init__()
        self.__special_charset = special_charset
        self.__applying_fields = applying_fields
        self.__do_remove_Emoticon = do_remove_Emoticon
        self.__above_number_of_words = above_number_of_words
   
    def filter(self, row):
        for f in self.__applying_fields:
            value = row[f]
            without_special_char = re.sub(self.__special_charset,' ', re.sub('\00','',value))
            backup = without_special_char
            if self.__do_remove_Emoticon:
                #try:
                without_special_char = without_special_char.encode('CP949','ignore').decode('CP949')
                #except:
                #    print(f"euc-kr en/decoding error{backup}")
                #    without_special_char = backup
            
            row[f] = ' '.join(without_special_char.split())       
            
        return (len(row[f].split())>self.__above_number_of_words), row


class PpFilterEnglish(PpFilter):
    def __init__(self, applying_fields, no_korean_char_filtering_limit, no_korean_char_printing_limit=2):
        self.__no_korean_char_limit = no_korean_char_filtering_limit
        self.__no_korean_char_printing_limit = no_korean_char_printing_limit
        self.__applying_fields = applying_fields

    def filter(self, row):
        is_found = False
        for f in self.__applying_fields:
            is_found = is_found or is_korean_sentence(row[f], self.__no_korean_char_limit, self.__no_korean_char_printing_limit)
        return is_found, row


class PpFilterUpperCase(PpFilter):
    def __init__(self, applying_fields):
        self.__applying_fields = applying_fields

    def filter(self, row):
        
        for f in self.__applying_fields:
            row[f] = row[f].upper()
        return True, row

class PpFilterAppendPeriod(PpFilter):
    def __init__(self, applying_fields):
        self.__applying_fields = applying_fields

    def filter(self, row):
        
        for f in self.__applying_fields:
            if row[f].rstrip()[-1] not in ['.','?','!']:
                row[f] = row[f] + "."
    
        return True, row

class fake_Kkma:
    def __init__(self, token_file, df_source):
        self.__df_review_token = pd.read_csv(token_file)

        self.__df_review_token.Review = df_source.Review
    
    def pos(self,sentence, flatten=True, join=True):

        sentence = sentence.upper()
        tokens = []
        df_result = self.__df_review_token[self.__df_review_token['Review']==sentence]

        if (df_result.shape[0]==0):
            print(f"[fake_token]Token Error : {sentence}")
        
        else:
            token_string = df_result.iloc[0]['Tokens']

            print(token_string)
            tokens = token_string.split('|')
            if join==False:
                tokens = [ token.split('/')[0] for token in tokens  ]
            if df_result.shape[0]>1:
                print(f"Token Warning: Too many matched sentenses{df_result.shape[1]}: {sentence} ")
        
        return tokens
        
class post_processor_AI_NNG:
    def apply(self, next_token):
        if next_token == '폰/NNG':
            return ['아이폰/NNG',"Phone/OL"]
        elif next_token == '패드/NNG':
            return ['아이패드/NNG',"Phone/OL"]
        return []       # 무시
        
class KkmaTokenizer:
    def pos(self, sentence, flatten = True, join=True):
        return sentence.split('|')

class CustomizedKkma:
    def __init__(self, tokenizer, post_process_dict, post_processor_pos, stop_words, pass_word_noun, pass_tags, join = True, filtering = False):
        self.__dict = post_process_dict
        self.__pos = post_processor_pos
        self.__stop_words = stop_words
        self.__pass_word_noun = pass_word_noun
        self.__pass_tag = pass_tags
        self.__join = join
        self.__filtering = filtering
        self.__tokenzier = tokenizer

    def tokenizer(self, sentence):
        tag_list = self.__tokenzier.pos(sentence, flatten=True, join=True)
        for index, tag in enumerate(tag_list):
            if tag in self.__dict:
                if (index != len(tag_list)-1):
                    next_tkn = tag_list[index+1]
                    result = self.__dict[tag].apply(next_tkn)
                    for offset, new_tag in enumerate(result):
                        print(f"대체:{result}")
                        tag_list[index+offset] = new_tag                    
        print(f"Step1 {tag_list}")
        pos_tag_sentence = '|'.join(tag_list)
        for pos, post_pos in self.__pos:
            sent_len = len(pos_tag_sentence)
            pos_len = len(pos)
            if pos_len>sent_len:
                continue
            inital_pos_tag = pos_tag_sentence[0:pos_len]

            if(inital_pos_tag==pos):
                pos_tag_sentence = post_pos + pos_tag_sentence[pos_len:sent_len]
            temp_pos = "|" + pos
            pos_tag_sentence = pos_tag_sentence.replace(temp_pos, "|"+post_pos)
        
        print("tokenize")
        if self.__filtering == False:
            return pos_tag_sentence.split('|')

        print(f"Step2 {pos_tag_sentence}")
        result = []
        for token in pos_tag_sentence.split('|'):
            if token in self.__stop_words:
                # Skip
                continue
            components = token.split('/')
            if len(components) != 2:
                print(f"Error no tag : {token}")
                continue

            if components[1] not in self.__pass_tag:
                continue
            elif components[1]=='NNG' and len(components[0])==1 and components[0] not in self.__pass_word_noun:
                continue
                
            if self.__join:
                result.append(f"{components[0]}/{components[1]}")
            else:
                result.append(components[0])
        
        print(result)
        print("-----")

        return result