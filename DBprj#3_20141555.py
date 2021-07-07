#-*- coding: utf-8 -*-

import datetime
import time
import sys
import MeCab
from pymongo import MongoClient
import sys
import pprint
from operator import itemgetter
import collections
import math
import operator

def printMenu():
    print "1. WordCount"
    print "2. TF-IDF"
    print "3. Similarity"
    print "4. MorpAnalysis"
    print "5. CopyData"


def MorpAnalysis(docs, col_tfidf):
    print "MorpAnalysis"
    t = MeCab.Tagger('d/user/local/lib/mecab/dic/mecab-ko-dic')
    oid = raw_input("Insert Object ID: ")
    found = 0

    reload(sys)
    sys.setdefaultencoding('utf-8')

    stop_word = {}
    f = open("wordList.txt",'r')
    while True:
        line = f.readline()
        if not line: break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()

    IDmorp = []
    for doc in docs:
#        if str(doc['_id']) == oid:
        content = doc['content']
        nodes = t.parseToNode(content.encode('utf-8'))

        MorpList = []
        while nodes:
            if nodes.feature[0] == 'N' and nodes.feature[1] == 'N':
                w = nodes.surface
                if not w in stop_word:
                    MorpList.append(w)
            nodes = nodes.next

        contentDic = {}
        for key in doc.keys():
            contentDic[key] = doc[key] 
        contentDic['morp'] = MorpList
        col_tfidf.update({'_id':contentDic['_id']},contentDic,True)

        if str(doc['_id']) == oid:
            found = 1
            IDmorp = MorpList

    if found==0:
        print "ID does not exist"
    else:
        print "Morp List in 'ID: " + oid +"'"
        for i in IDmorp:
            print i

def WordCount(docs, col_tfidf):
    print "WordCount"
    t = MeCab.Tagger('d/user/local/lib/mecab/dic/mecab-ko-dic')
    oid = raw_input("Insert Object ID: ")

    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    stop_word = {}
    f = open("wordList.txt",'r')
    while True:
        line = f.readline()
        if not line: break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()

    found = 0
    wordCnt = {}
    for doc in docs:
        content = doc['content']
        nodes = t.parseToNode(content.encode('utf-8'))

        MorpList = []  
        wordCnt.clear()
        while nodes:
            if nodes.feature[0] == 'N' and nodes.feature[1] == 'N':
                w = nodes.surface
                if not w in stop_word:
                   MorpList.append(w)
            nodes = nodes.next

        for morp in MorpList:
            if not morp in wordCnt:
                wordCnt[morp] = 1
            else:
                wordCnt[morp] = wordCnt[morp]+1

        contentDic = {}
        for key in doc.keys():
            contentDic[key] = doc[key]
        contentDic['WordCount'] = wordCnt
        col_tfidf.update({'_id':contentDic['_id']},contentDic,True)

    docs = col_tfidf.find()
    tmp = {}
    for doc in docs:
        if str(doc['_id'])==oid:
            found = 1
            tmp = doc['WordCount']
            print "Word         Count"
            for y in tmp:
                print("%-13s %d" % (str(y),tmp[y]))
            break

    if found == 0:
        print "ID does not exit"

def TfIdf(docs, col_tfidf):
    print "TF-IDF"
    t = MeCab.Tagger('d/user/local/lib/mecab/dic/mecab-ko-dic')
    oid = raw_input("Insert Object ID: ")

    reload(sys)
    sys.setdefaultencoding('utf-8')

    stop_word = {}
    f = open("wordList.txt",'r')
    while True:
        line = f.readline()
        if not line: break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()

    WordCnt = {}
    IDFdic = {}
    TFdic = {}
    totCnt = 0
    wct = 0
    for doc in docs:
        totCnt += 1
        words = doc['WordCount'] 
        for word in words:
            if not word in IDFdic:
                IDFdic[word] = 1
            else:
                IDFdic[word] = IDFdic[word]+1
    
    for tf in IDFdic:
#        print tf,IDFdic[tf]
        IDFdic[tf] = math.log(float(totCnt)/IDFdic[tf])
    
    TFIDFdic = {}
    tot_cnt = 0
    docs = col_tfidf.find()
    for doc in docs:
        TFdic.clear()
        TFIDFdic.clear()
        tot_cnt = 0
        dic = doc['WordCount']
        for word in dic:
            TFdic[word] = int(dic[word])
            tot_cnt = tot_cnt + int(dic[word])
        for word in dic:
            TFIDFdic[word] = float(TFdic[word])
            TFIDFdic[word] = TFIDFdic[word] / tot_cnt * IDFdic[word]
        contentDic = {}
        for key in doc.keys():
            contentDic[key] = doc[key]
        contentDic['TFIDF'] = TFIDFdic
        col_tfidf.update({'_id':contentDic['_id']},contentDic,True)

        if (oid == str(doc['_id'])):
            i=0;
            for y,v in sorted(TFIDFdic.items(),key=lambda TFIDFdic:TFIDFdic[1],reverse=True):
                print("%-20s" % (str(y))) ,v
                i=i+1
                if(i>9): break
 
def Similarity(docs, col_tfidf):
    print "Similarity"
    t = MeCab.Tagger('d/user/local.lib/mecab/dic/mecab-ko-dic')
    aid = raw_input("Insert Object ID: ")
    bid = raw_input("Insert Object ID: ")

    
    reload(sys)
    sys.setdefaultencoding('utf-8')

    stop_word={}
    f = open("wordList.txt",'r')
    while True:
        line = f.readline()
        if not line: break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()

    ATF={}
    BTF={}
    Uwordlist=[]
    AtotCnt=0
    BtotCnt=0

    for doc in docs:
        if str(doc['_id']) == aid:
            tfidfs = doc['TFIDF']
            for tfidf in tfidfs:
                if not tfidf in Uwordlist:
                    Uwordlist.append(tfidf)
            for tfidf in tfidfs:
                ATF[tfidf] = tfidfs[tfidf]
        if str(doc['_id']) == bid:
            tfidfs = doc['TFIDF']
            for tfidf in tfidfs:
                if not tfidf in Uwordlist:
                    Uwordlist.append(tfidf)
            for tfidf in tfidfs:
                BTF[tfidf] = tfidfs[tfidf]

    a=0
    b=0
    denom=0
    numer=0
    for i in Uwordlist:
        if i in ATF.keys() and i in BTF.keys():
            numer += ATF[i]*BTF[i]
        if i in ATF.keys():
            a+=ATF[i]*ATF[i]
        if i in BTF.keys():
            b+=BTF[i]*BTF[i]
    denom = math.sqrt(a)*math.sqrt(b)
    Sim = float(numer)/float(denom)
    print Sim

def copyData(docs,col_tfidf):
    col_tfidf.drop()
    for doc in docs:
        contentDic = {}
        for key in doc.keys():
            if key != "_id":
               contentDic[key] = doc[key]
        col_tfidf.insert(contentDic)

conn = MongoClient('localhost')
db = conn['db20141555']
db.authenticate('db20141555','db20141555')
col = db['news']
col_tfidf = db['news_tfidf']

printMenu()
selector = input()


docs = col_tfidf.find()
if selector ==1:
    WordCount(docs,col_tfidf)
elif selector == 2:
    TfIdf(docs,col_tfidf)
elif selector == 3:
    Similarity(docs,col_tfidf)
elif selector == 4:
    MorpAnalysis(docs,col_tfidf)
elif selector == 5:
    docs = col.find()
    copyData(docs,col_tfidf)

