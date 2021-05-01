#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:42:15 2021

@author: santealtamura
"""

import utils
from pathlib import Path

#effettua il riassunto di un documento
def summarization(document, reduction):
    title_topic = utils.get_title_topic(document)

    paragraphs_overlap = []
    for paragraph in document[1:]:
        paragraph_context = utils.get_context_paragraph(paragraph)
        
        average_topic_paragraph_overlap = 0 #overlap medio sul pragrafo corrente
        match_count = 0 #conteggio dei match
        for key1 in paragraph_context.keys():
            for key2 in title_topic.keys():
                #calcolo e sommo iterativamente la massimizzazione della similarità tra due concetti
                #uno individuato dalla chiave nel contesto del paragrafo
                #uno individuato dalla chiave nel topic
                #ad ogni chiave corrisponde un concetto, individuato come una lista di vettori NASARI
                average_topic_paragraph_overlap += utils.similarity(paragraph_context[key1],
                                                                               title_topic[key2])
                match_count += 1
        
        #calcolo la media per il paragrafo corrente e aggiunto il paragrafo con il suo score
        # in una lista di tuple (paragrafo,score)
        if match_count != 0:
            average_topic_paragraph_overlap = average_topic_paragraph_overlap / match_count
            paragraphs_overlap.append((paragraph,average_topic_paragraph_overlap))
    
    #calcoliamo il numero di paragrafi da manterenere nel riassunto
    number_of_paragraphs = len(paragraphs_overlap) - int(round((reduction / 100) * len(paragraphs_overlap), 0))
    
    #ordiniamo in modo descrescente la lista di tuple (paragrafo, score)
    paragraphs_overlap = sorted(paragraphs_overlap, key=lambda x: x[1], reverse = True)[:number_of_paragraphs]
    
    for paragraph, score in paragraphs_overlap:
        print(paragraph)
        print()
        print()
        print(score)
                    
    #ordiniamo i paragrafi nella lista list_of_paragraphs tenendo conto dell'ordine in cui i paragrafi compaiono nel documento originale
    #list_of_paragraphs = sorted(paragraphs_overlap, key = lambda x: x[0])
    
    

def main():
    #prendiamo la lista di file con estensione .txt nella cartella docs
    files = Path('utils/docs/').glob('*.txt')
    i = 0
    
    for file in files:
        print("====================================")
        print("====================================")
        summarization(utils.parse_document(file), 30)
        i += 1
        if i ==2 : break

main()
