#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:02:28 2021

@author: santealtamura
"""

from nltk.tokenize import word_tokenize
from collections import Counter
import math
from statistics import mean
import re

from nltk.corpus import wordnet as wn
import nltk
from nltk.stem.wordnet import WordNetLemmatizer

MIN_PARAGRAPH_LEN = 50

#Le stigma words ci permettono di capire che NON stanno per essere dette cose importanti
def get_stigma_words():
    return ['no','not','i','you','she','he','we','they','it','me','him','her','us','them','mine','ours',
            'hers','theirs','ourselves','myself','himself','who','whose','which','what','this','that',
            'these','those','whom','whose']

#Le bonus words ci permettono di capire che stanno per essere dette cose importanti
def get_bonus_words():
    return  ['better', 'worse', 'less', 'more', 'further', 'farther', 'best', 'worst', 'least', 'most',
             'furthest', 'farthest', 'more', 'important','seen', 'all', 'fact', 'final', 'analysis',
             'whole', 'brief', 'altogether', 'obviously','overall', 'ultimately', 'ordinarily',
             'definitely','usually', 'emphasize', 'result','henceforth', 'additionally', 'main', 
             'aim','purpose', 'outline', 'investigation']


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
#MAPPING -APPROCCIO:
#associare ad una word il set di vettori NASARI facendo matchare il wikititlepage del vettore
#se la ricerca dei vettori avviene con la stringa del tipo ;Word; allora verrà
#implementato l'approccio 1, restituendo le righe corrispondenti ai vettori
#che contengono quella stringa
def get_Nasari_vectors_for_bag_of_words(bag_of_words):
    nasari_vectors_for_bag_of_words = dict()
    for word in bag_of_words:
        query_string = ';' + word.capitalize() + ';' #la ricerca avviene nel secondo approccio
        nasari_vectors = get_Nasari_vectors(query_string)
        if word not in nasari_vectors_for_bag_of_words.keys() and nasari_vectors:
            nasari_vectors_for_bag_of_words[word] = nasari_vectors
    return nasari_vectors_for_bag_of_words

"""Approccio TITLE"""
#Metodo utilizzato nell'approccio TITLE
#il topic viene preso dal primo paragrafo del documento che in generale è il titolo
def get_title_topic(document):
    title = document[0]
    return get_Nasari_vectors_for_bag_of_words(bag_of_words(title))
"""Approccio TITLE"""

"""Approccio CUE"""
#Medoto utilizzato nell'approccio CUE
#Restituisce il topic del paragrafo più importante del documento
#il paragrafo più importante del documento è scelto in base alla prensenza di stigma word o bonus word
#ad ogni paragrafo viene associato un punteggio che aumenta di 1 per ogni bonus word
#e diminuisce di 1 per ogni stigma word al suo interno
#viene stilato un ranking e come topic viene scelto il paragrafo con il punteggio più alto
def get_topic(document):
    paragraph_score = []
    for paragraph in document:
        paragraph_score.append((paragraph, get_CUE_score(paragraph)))
    more_important_paragraph =  sorted(paragraph_score, key=lambda x: x[1], reverse = True)[0] #prendo il primo in classifica
    print("MORE IMPORTANT PARAGRAPH: \n", more_important_paragraph)
    print(bag_of_words(more_important_paragraph[0]))
    return get_Nasari_vectors_for_bag_of_words(bag_of_words(more_important_paragraph[0]))

#Restituisce uno score per il paragrafo in input
#direttamente proporzionale alle bonus word e inversamente proporzionale alle stigma word
#lo score è un numero intero positivo o negativo
def get_CUE_score(paragraph):
    word_list = tokenize(remove_punctuation(paragraph))
    score = 0
    for word in word_list:
        if word in get_bonus_words(): score += 1
        elif word in get_stigma_words(): score -= 1
    return score
"""Approccio CUE"""   
      
def get_context_paragraph(paragraph):
    return get_Nasari_vectors_for_bag_of_words(bag_of_words(paragraph))


#resistuisce il massimo weighted_overlap tra due concetti associati a due parole
#i concetti sono liste di vettori, quindi massimizza il weighted_overlap tra due liste di
#vettori NASARI
def similarity(vector_list1, vector_list2):
    max_overlap = 0
    
    for vector1 in vector_list1:
        for vector2 in vector_list2:
            overlap = math.sqrt(compute_weighted_overlap(vector1,vector2))
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


"""Funzioni di supporto"""

#rimuove le stowords da una lista di parole
def remove_stopwords(words_list):
    stopwords_list = get_stopwords()
    return [value.lower() for value in words_list if value.lower() not in stopwords_list]

#Rimuove la punteggiatura da una sentence
#Restituisce la sentence senza punteggiature
def remove_punctuation(sentence):
    return re.sub(r'[^\w\s]','',sentence)
   

#Restituisce la l'insieme di stopwords dal file delle stopwords
def get_stopwords():
    stopwords = open("stop_words_FULL.txt", "r")
    stopwords_list = []
    for word in stopwords:
        stopwords_list.append(word.replace('\n', ''))
    stopwords.close()
    return stopwords_list


#Tokenizza la frase in input e ne affettua anche la lemmatizzazione della sue parole
def tokenize(sentence):
    words_list = []
    lmtzr = WordNetLemmatizer()
    for tag in nltk.pos_tag(word_tokenize(sentence)):
        if (tag[1][:2] == "NN"):
            words_list.append(lmtzr.lemmatize(tag[0], pos = wn.NOUN))
        elif (tag[1][:2] == "VB"):
             words_list.append(lmtzr.lemmatize(tag[0], pos = wn.VERB))
        elif (tag[1][:2] == "RB"):
             words_list.append(lmtzr.lemmatize(tag[0], pos = wn.ADV))
        elif (tag[1][:2] == "JJ"):
             words_list.append(lmtzr.lemmatize(tag[0], pos = wn.ADJ))
    return words_list

#restituisce la bag of word per la frase o il paragrafo in oggetto
#effettua il pre-processing, ovvero la rimozione delle stopwords, punteggiatura e lemmatizzazione(?)-> per ora no  
def bag_of_words(sentence):
    return set(remove_stopwords(tokenize(remove_punctuation(sentence))))


"""Funzioni per la valutazione"""

#PRECISION e RECALL sui termini più importanti
def BLUE_ROUGE_terms_evaluation(document,system_summary, reduction):
     
    gold_important_words = get_important_words(document, reduction)
    system_words = get_words(system_summary)

    print("Document's important words: \n", gold_important_words)
    print("\nSystem summary words: \n", system_words)
    
    precision = len(gold_important_words.intersection(system_words)) / len(system_words)
    
    recall = len(gold_important_words.intersection(system_words)) / len(gold_important_words)

    return precision,recall
    
#restituisce il dizionario dei tf per ogni parola nel documento
#ogni parola avrà tanti tf quanti sono i paragrafi del documento
def get_tf_dictionary(document):
    tf_dictionary = dict()
    for paragraph in document[1:]:
        bag_of_words_par = remove_stopwords(tokenize(remove_punctuation(paragraph)))
        tf_par = Counter(bag_of_words_par)
        for word in tf_par.keys():
            if word not in tf_dictionary.keys(): tf_dictionary[word] = [tf_par[word] / len(bag_of_words_par)]
            else: tf_dictionary[word].append(tf_par[word] / len(bag_of_words_par))
    return tf_dictionary       
            
            
def get_idf_dictionary(document,tf_dictionary):
    idf_dictionary = dict()
    n_paragraph = len(document[1:])
    for word in tf_dictionary.keys():
        n_paragraph_contains_word = 0
        for paragraph in document[1:]:
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

#restituisce una lista di coppie (word, tf-idf) relative a document 
#ordinate secondo il valore di tf-idf        
def get_important_words(document, reduction):
    #word -> tf1,tf2,tf3,...
    #ogni tf è relativo al termine per un paragrafo
    #un termine avrà n tf per ogni paragrafo del documento
    tf_dictionary = get_tf_dictionary(document)
   
    #word -> idf
    #un termine avrà un solo idf
    idf_dictionary = get_idf_dictionary(document, tf_dictionary)
    
    #un termine avrà n tf-idf. verrà preso il tf-idf medio
    tf_idf_dictionary = get_tf_idf_dictionary(tf_dictionary, idf_dictionary)
    
    #calcoliamo il numero di termini da mantenere (saranno quelle più importanti)
    #il numero di parole è dato da len(tf_idf_dictionary) * (100 - reduction)/100
    percentage = (100 - reduction)/100
    important_words_number = int(round(len(tf_idf_dictionary) * percentage))
    
    #vengono ordinati in modo decrescente gli score tf-idf
    sorted_tf_idf = sorted(tf_idf_dictionary.items(), key=lambda x: x[1], reverse=True)[:important_words_number]
    
    #restituisco solo i termini (senza score)
    important_words = set()
    for item in sorted_tf_idf: important_words.add(item[0])
    
    return important_words

#restituisce il bag of words di un documento
def get_words(document):
    bag_of_words_document = set()
    for paragraph in document[1:]:
        bag_of_words_par = (bag_of_words(paragraph))
        bag_of_words_document = bag_of_words_document | bag_of_words_par
    return bag_of_words_document