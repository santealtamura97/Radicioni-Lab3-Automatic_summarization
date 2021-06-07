#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:42:15 2021

@author: santealtamura
"""

import utils
from pathlib import Path

#effettua il riassunto di un documento
def summarization(document, reduction, relevance_criteria):
    
    if relevance_criteria == 'title':
        topic = utils.get_title_topic(document)
    elif relevance_criteria == 'cue':
        topic = utils.get_topic(document)
    
    print()
    print("Topic of the file: ")
    print(topic)
    
    paragraphs_overlap = []
    for paragraph in document[1:]:
        paragraph_context = utils.get_context_paragraph(paragraph)
        
        average_topic_paragraph_overlap = 0 #overlap medio sul pragrafo corrente
        match_count = 0 #conteggio totale degli overlap calcolati
        for key1 in paragraph_context.keys():
            for key2 in topic.keys():
                #calcolo e sommo iterativamente la massimizzazione della similarità tra due concetti
                #uno individuato dalla chiave nel contesto del paragrafo
                #uno individuato dalla chiave nel topic
                #ad ogni chiave corrisponde un concetto, individuato come una lista di vettori NASARI
                average_topic_paragraph_overlap += utils.similarity(paragraph_context[key1],
                                                                               topic[key2])
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
                    
    #ordiniamo i paragrafi nella lista list_of_paragraphs tenendo conto dell'ordine in cui i paragrafi
    #compaiono nel documento originale
    summary = []
    summary.append(document[0]) #aggiungiamo il titolo come primo paragrafo del riassunto
    list_of_paragraphs = [paragraph[0] for paragraph in paragraphs_overlap]
    for paragraph in document[1:]: 
        if paragraph in list_of_paragraphs: 
            summary.append(paragraph)
            
    
    return summary        
        
    
def main():
    #l'utente può riassumere un insieme di file
    #prendiamo la lista di file con estensione .txt nella cartella docs
    files = Path('utils/docs/').glob('*.txt')
    for file in files:
        print("file name : ",file.name)
    files.close()
    
    #l'utente inserisce il nome del file che vuole riassumere
    file_name = input("Inserire il nome del file da riassumere (compreso di .txt):\n")
    
    #l'utente inserisce la percentuale di riduzione del riassunto
    reduction = int(input("Inserire la percentuale di riduzione (10,20,30):\n"))
    
    #-------FASE DI SUMMARIZATION--------#
    files = Path('utils/docs/').glob('*.txt')
    document = None
    for file in files:
        if file.name == file_name:
            document = file
            summary = summarization(utils.parse_document(file), reduction, relevance_criteria='cue')
            print("_______________________________________________________________")
            print("\nRIASSUNTO:\n")
            for par in summary:
                print(par)
                print()
            print("_______________________________________________________________")
    files.close()
    
    #-------VALUTAZIONE SUI TERMINI------#
    print("_______________________________________________________________")
    precision,recall = utils.BLUE_ROUGE_terms_evaluation(utils.parse_document(document),summary, reduction)
    
    print("_______________________________________________________________")
    #BLUE evaluation
    print("Precision sui termini significativi: ",precision)
    
    #ROUGE evaluation
    print("Recall sui termini significativi: ",recall)

main()
