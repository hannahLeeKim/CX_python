import pandas as pd
import csv

def update_dictionary(sentence, dictionary):
    for word in sentence.split():
        if word not in dictionary:
            dictionary.update({word:1})
        else:
            dictionary[word] += 1

d = {}

source_file = "C:\\Work\\Customer Exprience\\customerexp\\data\\googleplay\\target\\P1_2_[OTT][wave]_2209162357.csv"
target_file_format = "C:\\Work\\Customer Exprience\\customerexp\\data\\googleplay\\target\\{}_[OTT][wave]_2209162357.csv"

def check_duplicate_sentence(s):
    result = { 'min' : 0 ,'max' : 0 , 'sentence' : ''}
    l=[]
    for t in s:
        l.append(ord(t))

    series  = pd.Series(l)

    array = [series.autocorr(lag=i) for i in range(1,len(s)//2)]
    result['min'] = min(array)
    result['max'] = max(array)
    result['sentence'] = s
    return result;

def generate_dictionary(source_file,target_file):
    df = pd.read_csv(source_file, encoding='utf-8-sig')

    for s in df.Review:
        update_dictionary(s, d)

    with open(target_file, 'w' , encoding='utf-8-sig') as csv_out:
        csv_writer = csv.writer(csv_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        
        for k in d:
            csv_writer.writerow([k,d[k]])

def generate_corelation(source_file,target_file):
    df = pd.read_csv(source_file, encoding='utf-8-sig')

    with open(target_file, 'w' , encoding='utf-8-sig') as csv_out:
        csv_writer = csv.writer(csv_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    
        for s in df.Review:
            result =  check_duplicate_sentence(s)
            csv_writer.writerow([result['sentence'],result['min'],result['max']])
    
        
def generate_word_corelation(source,target_file, min_length_of_word = 9):
    df = pd.read_csv(source_file, encoding='utf-8-sig')

    with open(target_file, 'w' , encoding='utf-8-sig') as csv_out:
        csv_writer = csv.writer(csv_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        
        for s in df.Review:
            for k in s.split():
                if len(k)>min_length_of_word:
                    result =  check_duplicate_sentence(k)
                    csv_writer.writerow([result['sentence'],result['min'],result['max']])


# P2_2 반복되는 문장이 있는지 체크
generate_corelation(source_file, target_file_format.format('P2_2'))
       
# 단어단위에서 반복되는 단어가 있는지 체크
generate_word_corelation(source_file,target_file_format.format('P2_3') )
