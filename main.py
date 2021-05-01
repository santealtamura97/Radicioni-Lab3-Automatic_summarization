#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:42:15 2021

@author: santealtamura
"""

import utils
from pathlib import Path

def summarization(document, reduction):
    title_topic = utils.get_title_topic(document)

    paragraphs_overlap = []
    for paragraph in document[1:]:
        paragraph_context = utils.get_context_paragraph(paragraph)
        
        average_topic_paragraph_overlap = 0 #overlap medio sul pragrafo corrente
        match_count = 0 #conteggio dei match
        for key1 in paragraph_context.keys():
            for key2 in title_topic.keys():
                #sommiamo tutti gli overlap massimi dati dalla parola nel paragrafo con le parole nel titolo
                average_topic_paragraph_overlap += utils.similarity(paragraph_context[key1],
                                                                               title_topic[key2])
                match_count += 1
        
        if match_count != 0:
            average_topic_paragraph_overlap = average_topic_paragraph_overlap / match_count
            paragraphs_overlap.append((paragraph,average_topic_paragraph_overlap))
        
    
    for paragraph, overlap in paragraphs_overlap:
        print("====================")
        print(paragraph)
        print()
        print()
        print(overlap)
        print("====================")
                    
    
    
def main():
    #prendiamo la lista di file con estensione .txt nella cartella docs
    files = Path('utils/docs/').glob('*.txt')
    i = 0
    for file in files:
        print("===================")
        summary = summarization(utils.parse_document(file), 10)
        i += 1
        if i ==1 : break

main()


