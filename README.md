# LexSemMapping
Python script and material for automatic lexico-semantic mapping of DEAF data using python. 

## folder *py* contains 
* main script mapping.py
* data_poc.py: the manually created data for the Proof of Concept; the structure is, for each list, 'lexeme from RDF data', 'definition from RDF data', 'keyword fr', 'keyword engl'. 
Depending on the implementation, the algorithm either uses the English keyword (to query for English Wikipedia entries) or the French keyword (to query French Wikipedia entries with automatic search for corresponding English Wikipedia entries through the Wikipedia API).
* blacklist.py: this file contains the list of words to be generally ignored by the algorithm, i.e., articles, pronouns, prepositions, etc.; also words that occur in many definitions but lead to false results, e.g.,  
_changeant_, present participle of _changer_ (to change), which maps to `List_of_Star_Trek_aliens#Changeling', a fictitious species of the Star-Trek universe.

## folder *material ttl* contains RDF-ttl data  
* data_rd_non_nomina.ttl: data for the non-noun method
* DEAF articles with sense definitions of all kinds

## folder *results* 
* data_poc.json: result of mapping data_poc
* data_rd_non_nomina_mapped.ttl: result of non-noun method
* the respective files for each DEAF article
