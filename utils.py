#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:02:28 2021

@author: santealtamura
"""

import string
from nltk.tokenize import word_tokenize



#quello che vogliamo fare è inividuare il topic come un insieme di set di vettori Nasari
#cioè individuiamo il bag_of_words del titolo o della prima sentence (nel caso del topic)
#oppure il bag_of_words relativo un paragrafo
#ed assegniamo ad ogni word un set di vettori Nasari corrispondenti

#MAPPING - 2 APPROCCI:
# 1. associare ad una word il set di vettori NASARI facendo matchare il wikititlepage del vettore
# 2. associare ad una word il set di vettori NASARI facendo matchare con le dimensioni dei vettori, ovvero i lemmi a cui sono associati gli score

#se la ricerca dei vettori avviene con la stringa del tipo ;Word; allora verrà
#implementato l'approccio 1, restituendo le righe corrispondenti ai vettori
#che contengono quella stringa

#se la ricerca dei vettori avviene con la stringa del tipo ;word_ allora verrà
#implementato l'approccio 2, restituendo le righe corrispondenti ai vettori
#che contengono quella stringa
def get_Nasari_vectors(query_string):
    nasari_vectors = list()
    file = open('utils/NASARI_vectors/dd-small-nasari-15.txt', 'r' , encoding="utf8")
    for line in file:
        if query_string in line:
            nasari_vectors.append(vector_format(line))
    file.close()
    return nasari_vectors
                   
#riceve in input una riga del file NASARI small e restituisce
#un vettore NASARI formattato, per esempio, nel seguente modo:
#[('million', '209.35'), ('number', '146.31'), ('mathematics', '61.3'), 
#('long scale', '53.31'), ('real number', '50.43'), ('numeral', '50.35'), 
#('short scale', '50.12'), ('digit', '42.17'), ('bally', '41.77'), ('millionaire', '41.31'), 
#('penguin', '41.11'), ('markov', '40.61'), ('complex number', '38.37'), ('infinity', '36.79')]
def vector_format(nasari_line):
    line_splitted = nasari_line.replace("\n", "").split(";")
    word_score_list = []
    for item in line_splitted[2:]:
        if "_" in item:
            word, score = item.split("_")
            word_score_list.append((word,score))
            
    return word_score_list

#restituisce un dizionario, dove, ad ogni parola (chiave) è associata 
#una lista di vettori NASARI
def get_Nasari_vectors_for_bag_of_words(bag_of_words):
    nasari_vectors_for_bag_of_words = dict()
    for word in bag_of_words:
        query_string = ';' + word + '_' #la ricerca avviene nel secondo modo
        nasari_vectors = get_Nasari_vectors(query_string)
        if word not in nasari_vectors_for_bag_of_words.keys() and nasari_vectors:
            nasari_vectors_for_bag_of_words[word] = nasari_vectors
    return nasari_vectors_for_bag_of_words

#individuare il topic: se il titolo dei testi da riassumere non è abbastanza informativo
#allora il topic verrà individuato nella prima frase del primo paragrafo    
def get_title_topic(document):
    title = document[0]
    return get_Nasari_vectors_for_bag_of_words(bag_of_words(title))
    

def get_context_paragraph(paragraph):
    return get_Nasari_vectors_for_bag_of_words(bag_of_words(paragraph))


def similarity(vector_list1, vector_list2):
    max_overlap = 0
    
    for vector1 in vector_list1:
        for vector2 in vector_list2:
            overlap = compute_weighted_overlap(vector1,vector2)
            if overlap > max_overlap:
                max_overlap = overlap
    return max_overlap


def compute_weighted_overlap(vector1,vector2):
    overlap = 0
    common_keys = get_common_keys(vector1, vector2)
    
    if len(common_keys) > 0:
        numerator = 0
        for q in common_keys:
            numerator += (1 / (rank(q, vector1) + rank(q, vector2)))
        
        denominator = 0
        for i in range(1, len(common_keys) + 1):
            denominator += 1/ (2 * i)
        
        overlap = numerator / denominator
        
    return overlap
            

def get_common_keys(vector1, vector2):
    common_keys = []
    for word1,score1 in vector1:
        for word2, score2 in vector2:
            if word1 == word2:
                common_keys.append(word1)
    return common_keys


def rank(key, vector):
    for index,(word,value) in enumerate(vector):
        if word == key: return index + 1
            

#Rimuove le stopwords da una lista di parola
def remove_stopwords(words_list):
    stopwords_list = get_stopwords()
    new_words_list = []
    for word in words_list:
        word_lower = word.lower()
        if word_lower not in stopwords_list:
            new_words_list.append(word_lower)
    return new_words_list

#Rimuove la punteggiatura da una lista di parole
def remove_punctuation(words_list):
    new_words_list = []
    for word in words_list:
        temp = word
        if not temp.strip(string.punctuation) == "":
            new_word = word.lower()
            new_word = new_word.replace("'","")
            new_words_list.append(new_word)
    return new_words_list

#Restituisce una lista di paragrafi del documento in input
#il primo paragrafo rappresenta il titolo
def parse_document(doc):
    document = []
    data = doc.read_text(encoding='utf-8')
    lines = data.split('\n')
    
    for line in lines:
        if line != "" and not "#" in line:
            line = line.replace("\n", "")
            document.append(line)
    return document
   

#Restituisce la l'insieme di stopwords dal file delle stopwords
def get_stopwords():
    stopwords = open("stop_words_FULL.txt", "r")
    stopwords_list = []
    for word in stopwords:
        stopwords_list.append(word.replace('\n', ''))
    stopwords.close()
    return stopwords_list

def tokenize(sentence):
    return word_tokenize(sentence)

#restituisce la bag of word per la frase o il paragrafo in oggetto
#effettua il pre-processing, ovvero la rimozione delle stopwords, punteggiatura e lemmatizzazione(?)-> per ora no  
def bag_of_words(sentence):
    return remove_stopwords(remove_punctuation(tokenize(sentence)))
    
    
    
