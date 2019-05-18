import PyPDF2
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

def tokenize(path):
    # open PDF
    pdf = PyPDF2.PdfFileReader(open(str(path), "rb"))
    factory = StopWordRemoverFactory()
    stopword_list = factory.get_stop_words()

    # read PDF file in a list
    pdf_content = []
    for page in pdf.pages:
        pdf_content.append(page.extractText())

    # tokenize all the words in the resume
    tokenize = []
    for line in pdf_content:
        tokenize = filter(None, (line.split(" ")))

    # remove punctuations and case-fold
    no_punctuations = []
    for token in tokenize:
        no_punctuations.append(token.rstrip(",:|.-").lower())

    # remove stop words
    without_stop_words = []

    for word in filter(None, no_punctuations):
        if word not in stopword_list:
            without_stop_words.append(word)

    return without_stop_words

from math import log

'''
Using the following formula to calculate BM25
((k3 + 1)q)/((k3 + q)) * ((k1 + 1)f)/((K + f)) * log((r + 0.5)(N − n − R + r + 0.5))/((n − r + 0.5)(R − r + 0.5))
REFERENCE: https://xapian.org/docs/bm25.html
'''

# DEFINING CONSTANTS

k1 = 1.2
b = 0.75
k2 = 100
R = 0  # Since no relevance info is available


# MAIN METHOD
def BM25(docLen, avDocLen, n, N, f, q, r):
    p1 = ((k2 + 1) * q) / (k2 + q)
    p2 = ((k1 + 1) * f) / (getK(docLen, avDocLen) + f)
    p3 = log((r + 0.5) * (N - n - R + r + 0.5)) / ((n - r + 0.5) * (R - r + 0.5))
    return p1 * p2 * p3


def getK(docLen, avDocLen):
    return k1 * ((1 - b) + b * (float(docLen) / float(avDocLen)))

import operator
# from retrieval import BM25
# get average document length
def get_avdl(length_index):
    corpus_length = 0
    for document in length_index:
        corpus_length += length_index[document]
    return float(corpus_length) / float(len(length_index))


def search(query):
    inv_index_file = open("project/DocumentSearch/dependency/indexes/inverted_index.json","r+")
    inverted_index = json.load(inv_index_file)

    length_index_file = open("project/DocumentSearch/dependency/indexes/length_index.json","r+")
    length_index = json.load(length_index_file)

    scores = defaultdict(list)
    query_tokens = query.split()
    for token in query_tokens:
        for entry in inverted_index[token]:
            scores[entry[0]] = BM25(length_index[entry[0]], get_avdl(length_index), len(inverted_index[token]),
                                    len(length_index), entry[1], 1, 0)
    return sorted(scores.items(), key=operator.itemgetter(1))

from collections import defaultdict
import glob
import json

def get_file_names():
    files = []
    for file in glob.glob(
            "D:/Kuliah/Semester 8/INRE/Document-Search-Information-Retrieval-BM25-master/dependency/documents/*.pdf"):
        files.append(file)
    return files


def make_index(tokens, document_name, index, length):
    for term in set(tokens):
        index[term].append([document_name, tokens.count(term)])
        length[document_name] = len(set(tokens))


def generator():
    files = get_file_names()
    inverted_index = defaultdict(list)
    length_index = defaultdict(list)
    for file in files:
        make_index(tokenize(file), file, inverted_index, length_index)
    write(inverted_index, length_index)


#     print("Indexes generated")


# def write(inverted_index, length_index):
#     inv_index_file = open(
#         "D:/Kuliah/Semester 8/INRE/Document-Search-Information-Retrieval-BM25-master/dependency/indexes/inverted_index.json",
#         "w")
#     json.dump(inverted_index, inv_index_file)
#
#     length_index_file = open(
#         "D:/Kuliah/Semester 8/INRE/Document-Search-Information-Retrieval-BM25-master/dependency/indexes/length_index.json",
#         "w")
#     json.dump(length_index, length_index_file)