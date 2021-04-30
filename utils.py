#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:02:28 2021

@author: santealtamura
"""

import string

"""
#Restituisce una struttura dati che rappresenta l'insieme
#di vettori NASARI. La struttura dati è un dizionario
#che ha come chiavi la word_label che rappresenta il babel synset
#e come valori delle liste di coppie (word,score)

#es. {'Million': [('million', '209.35'), ('number', '146.31'), ('mathematics', '61.3'), 
#('long scale', '53.31'), ('real number', '50.43'), ('numeral', '50.35'), 
#('short scale', '50.12'), ('digit', '42.17'), ('bally', '41.77'), ('millionaire', '41.31'), 
#('penguin', '41.11'), ('markov', '40.61'), ('complex number', '38.37'), ('infinity', '36.79')]}
def get_Nasari_vectors():
    nasari_vectors = dict()
    file = open('utils/NASARI_vectors/dd-small-nasari-15.txt', 'r' , encoding="utf8")
    for line in file:
        line_splitted = line.replace("\n", "").split(";")
        word_score_list = []
        for item in line_splitted[2:]:
            if "_" in item:
               word, score = item.split("_")
               word_score_list.append((word,score))
        word_label = line_splitted[1]
        nasari_vectors[word_label] = word_score_list
        
    file.close()    
    return nasari_vectors
"""
#individuare il topic: se il titolo dei testi da riassumere non è abbastanza informativo
#allora il topic verrà individuato nella prima frase del primo paragrafo

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

#restituisce un dizionario, dove, per ogni parola (chiave) è associata 
#una lista di vettori NASARI
def get_Nasari_vectors_for_bag_of_words(bag_of_words):
    return


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

#Restituisce la l'insieme di stopwords dal file delle stopwords
def get_stopwords():
    stopwords = open("stop_words_FULL.txt", "r")
    stopwords_list = []
    for word in stopwords:
        stopwords_list.append(word.replace('\n', ''))
    stopwords.close()
    return stopwords_list

#restituisce la bag of word per la frase o il paragrafo in oggetto
#effettua il pre-processing, ovvero la rimozione delle stopwords, punteggiatura e lemmatizzazione(?)-> per ora no  
def bag_of_words(sentence):
    return remove_stopwords(remove_punctuation(sentence))
    
    
    
