#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:02:28 2021

@author: santealtamura
"""

import string
from nltk.tokenize import word_tokenize
from collections import Counter
import math
from statistics import mean

MIN_PARAGRAPH_LEN = 50

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
        query_string = ';' + word + '_' #la ricerca avviene nel secondo approccio
        nasari_vectors = get_Nasari_vectors(query_string)
        if word not in nasari_vectors_for_bag_of_words.keys() and nasari_vectors:
            nasari_vectors_for_bag_of_words[word] = nasari_vectors
    return nasari_vectors_for_bag_of_words

    
def get_title_topic(document):
    title = document[0]
    return get_Nasari_vectors_for_bag_of_words(bag_of_words(title))
    

def get_context_paragraph(paragraph):
    return get_Nasari_vectors_for_bag_of_words(bag_of_words(paragraph))

#resistuisce il massimo weighted_overlap tra due concetti associati a due parole
#i concetti sono liste di vettori, quindi massimizza il weighted_overlap tra due liste di
#vettori NASARI
def similarity(vector_list1, vector_list2):
    max_overlap = 0
    
    for vector1 in vector_list1:
        for vector2 in vector_list2:
            overlap = compute_weighted_overlap(vector1,vector2)
            if overlap > max_overlap:
                max_overlap = overlap
    return max_overlap

#calcola il weighted_overlap tra due vettori NASARI
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
            
#restituisce le chiavi (dimensioni) comuni tra due vettori NASARI
def get_common_keys(vector1, vector2):
    common_keys = []
    for word1,score1 in vector1:
        for word2, score2 in vector2:
            if word1 == word2:
                common_keys.append(word1)
    return common_keys

#calcola il rango di una chiave (dimensione) all'interno del vettore NASARI in input
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
    
    for index,line in enumerate(lines):
        if line != "" and not "#" in line and (len(line) > MIN_PARAGRAPH_LEN or index == 3):
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

#tokenizza una frase in input
def tokenize(sentence):
    return word_tokenize(sentence)

#restituisce la bag of word per la frase o il paragrafo in oggetto
#effettua il pre-processing, ovvero la rimozione delle stopwords, punteggiatura e lemmatizzazione(?)-> per ora no  
def bag_of_words(sentence):
    return remove_stopwords(remove_punctuation(tokenize(sentence)))


#PRECISION e RECALL sui termini più importanti
def BLUE_ROUGE_terms_evaluation(gold_summary,system_summary):
    
    gold_important_words = get_important_words(gold_summary)
    
    system_important_words = get_important_words(system_summary)

    print("Gold important words: \n", gold_important_words)
    print("\nSystem important words: \n", system_important_words)
    
    precision = len(list(set(gold_important_words) & set(system_important_words))) / len(set(system_important_words))
    
    recall = len(list(set(gold_important_words) & set(system_important_words))) / len(set(gold_important_words))

    
    return precision,recall


def get_tf_dictionary(gold_summary):
    tf_dictionary = dict()
    for paragraph in gold_summary[1:]:
        bag_of_words_par = (bag_of_words(paragraph))
        tf_par = Counter(bag_of_words_par)
        for word in tf_par.keys():
            if word not in tf_dictionary.keys(): tf_dictionary[word] = [tf_par[word] / len(bag_of_words_par)]
            else: tf_dictionary[word].append(tf_par[word] / len(bag_of_words_par))
    return tf_dictionary       
            
            
def get_idf_dictionary(gold_summary,tf_dictionary):
    idf_dictionary = dict()
    n_paragraph = len(gold_summary[1:])
    for word in tf_dictionary.keys():
        n_paragraph_contains_word = 0
        for paragraph in gold_summary[1:]:
            if word in bag_of_words(paragraph):
                n_paragraph_contains_word += 1
        idf_dictionary[word] = math.log(n_paragraph / n_paragraph_contains_word)
    return idf_dictionary


def get_tf_idf_dictionary(tf_dictionary,idf_dictionary):
    tf_idf_dictionary = dict()
    for word in tf_dictionary.keys():
        tfs_score = tf_dictionary[word] #tutti i term frequency associati alla word
        idf_score = idf_dictionary[word] #idf associato alla word
        tf_idf_dictionary[word] = mean([tf * idf_score for tf in tfs_score])
    return tf_idf_dictionary
        
def get_important_words(summary):
    #word -> tf1,tf2,tf3,...
    #ogni tf è relativo al termine per un paragrafo
    #un termine avrà n tf per ogni paragrafo in cui compare del gold summary
    tf_dictionary = get_tf_dictionary(summary)
   
    #word -> idf
    #un termine avrà un solo idf
    idf_dictionary = get_idf_dictionary(summary, tf_dictionary)
    
    #un termine avrà un solo idf
    #un termine avrà n tf-idf. verrà preso il tf-idf medio
    tf_idf_dictionary = get_tf_idf_dictionary(tf_dictionary, idf_dictionary)
    
    #vengono ordinati in modo decrescente gli score tf-idf
    sorted_tf_idf = sorted(tf_idf_dictionary.items(), key=lambda x: x[1], reverse=True)
    
    #vengono scelte le parole che superano la media di tf-idf di tutti i termini
    important_words = []
    average_tf_idf = mean([item[1] for item in sorted_tf_idf])
    for item in sorted_tf_idf:
        if item[1] >= average_tf_idf:
            important_words.append(item[0])
            
    return important_words