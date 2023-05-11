import wikipediaapi
import json
import rdflib
import re
from data_poc import data_poc
from blacklist import blacklist
from rdflib import URIRef, Literal
from rdflib.namespace import Namespace


graph = rdflib.Graph()
# graph.parse('data_rdf.ttl') # remote: g.parse("https://...") data_rdf_non_nomina.ttl / data_rdf.ttl
# graph.parse('/Users/stittel/Documents/habil/XSLT/SemanticMapping/Definitionen_haendisch.ttl') # Datensatz mit 236 Substantiven
graph.parse('/Users/stittel/Documents/habil/XSLT/Kurzartikel/papier.ttl')
# graph.parse('/Users/stittel/Documents/habil/XSLT/Langartikel-d-f/flaüte.ttl')
# graph.parse('/Users/stittel/Documents/habil/XSLT/Langartikel-g-k/hote.ttl')
    # jurer Extension_(semantics) => _\(..\)
    # hart zweimal Extension_(semantics) => _\(..\)
    # herde Extension_(semantics) => _\(..\)

ontolex = URIRef('http://www.w3.org/ns/lemon/ontolex#')
dbr = URIRef('https://dbpedia.org/resource/')
skos = URIRef('http://www.w3.org/2004/02/skos/core#')
deaf = URIRef('https://deaf-server.adw.uni-heidelberg.de#')
# für data_rdf.ttl: deaf = URIRef('https://deaf-server.adw.uni-heidelberg.de/lemme/')
vartrans = URIRef('http://www.w3.org/ns/lemon/vartrans#')
synsem = URIRef('http://www.w3.org/ns/lemon/synsem#')
dct = URIRef('http://purl.org/dc/terms/')
cc = URIRef('http://creativecommons.org/ns#')
rdf = Namespace(' <http://www.w3.org/1999/02/22-rdf-syntax-ns#')
rdfs = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
lexinfo = URIRef('https://lexinfo.net/ontology/3.0/lexinfo#')
foaf = URIRef('http://xmlns.com/foaf/0.1/')
xsd = URIRef('http://www.w3.org/2001/XMLSchema#')
olia = URIRef('http://purl.org/olia/olia.owl#')
decomp = URIRef('http://www.w3.org/ns/lemon/decomp#')
lemonety = URIRef('http://lari-datasets.ilc.cnr.it/lemonEty#')
lexvo = URIRef('http://lexvo.org/id/iso639-3/')
lime = URIRef('http://www.w3.org/ns/lemon/lime#')
lexicog = URIRef('http://www.w3.org/ns/lemon/lexicog#')
semshift = URIRef('http://www.deaf-page.de/ns/semshift#')

wiki_wiki = wikipediaapi.Wikipedia('fr') # ('en')

# result = re.sub('.*\((.*)(\ L\.)\).*', r'\1', 'abc xy 12 (de fgh L.) i')
# result = re.sub(r'.*(?<=\bsorte de\s)(\w+).*', r'\1', 'plante, sorte de céréale')
# result = re.sub('^(\w+\ ?\w+)\??$', r'\1', 'goutte goutte goutte?')
# result = re.sub('(.*\ )\(([A-Z]\w+|[A-Z]\w+\ \w+)\)(.*)', r'\2', 'abc xy 12 (Viola) i')
# result = re.sub(r'.*(?<=\bsorte de|\bsorte d\')(?:\sgrand|\sgrande|\spetit|\spetite|\sgros|\sgrosse){0,1}\ {0,1}(\w+)(.*)', r'\1', 'test sorte d\'éponge')
# result = re.sub('(.*\ )([A-Z]\w+)(\ L.){0,1}', r'\2', 'test Wort L.')
# result = re.sub('(.*)(\,[^\,\r\n]|\;[^\,\r\n])(\w+\ ?\w+)(\ et sim.|,\ et sim.){0,1}(\??)(\ \(\?\))?$', r'\3', 'souffle (du vent); respiration (?)')
# print('result:', result)

# regex to find Linné terminology in brackets with 'L.'
linne = re.compile(r'\(.* L\.\)')

# regex to find Linné terminology in brackets without ' L.'
linne_unobvious = re.compile(r'\(([A-Z]\w+|[A-Z]\w+\ \w+)\)')

# regex to find Linné terminologie without brackets, with 'L.', by capitalized term + second term
linne_cap = re.compile(r'([A-Z]\w+\ \w+(\ L.))')

# regex to find Linné terminologie without brackets, with 'L.', by capitalized single term
linne_cap_single = re.compile(r'([A-Z]\w+(\ L.))')

# regex to find Linné terminologie without brackets, without 'L.', by capitalized term + second term
# priority after single word and last word hits
linne_cap_unobvious = re.compile(r'([A-Z]\w+\ \w+)')

# regex to find Linné terminologie without brackets, without 'L.', by capitalized single term
# priority after single word and last word hits
linne_cap_single_unobvious = re.compile(r'([A-Z]\w+)')

# regex to find the text (modern French synonyms) at the end of the definition;
# ignore ' et sim' / ', et sim.' / ? / (?) at end of definition
last_word = re.compile(r'(\,[^\,\r\n]|\;[^\,\r\n])(\w+\ ?\w+)(\ et sim.|,\ et sim.){0,1}(\??)(\ \(\?\))?$')

# find keyword after 'sorte de' / 'sorte d'' and 'espèce de' / 'espèce d'' resp.;
# blacklist: grand, grande, petit, petite, gros, grosse
sorte = "sorte de"
sorte_apostr = "sorte d'"
espece = "espèce de"
espece_apostr = "espèce d'"

# regex to find single or two words definition (here: no spaces around |)
single_word = re.compile(r'^(\w+\ ?\w+)\??$')


def map_rdf(graph):
    """
    :param graph: RDF triples (ttl) with examples of lexemes skos:definition ".."
    result: adds new triple with mapping to dbr to RDF triples; writes into graph
    """
    for s, p, o in graph:
        if p == (skos + 'definition') and type(o) == rdflib.term.Literal:
            if linne.search(o):
                keyword = concat(normalize(re.sub('.*\((.*)(\ L\.)\).*', r'\1', o)))
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue

            if linne_unobvious.search(o):
                keyword = concat(normalize(re.sub('(.*\ )\(([A-Z]\w+|[A-Z]\w+\ \w+)\)(.*)', r'\2', o))) # (here: no spaces around |)
                # exclude (qn):
                if keyword != 'qn':
                    page_py = wiki_wiki.page(keyword)
                    if page_py.exists():
                        make_langlinks(s, page_py)
                        continue

            if linne_cap.search(o):
                keyword = concat(normalize(re.sub('(.*\ )([A-Z]\w+\ \w+)(\ L.)(.*)', r'\2', o)))
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue

            if linne_cap_single.search(o):
                keyword = normalize(re.sub('(.*\ )([A-Z]\w+)(\ L.)', r'\2', o))
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue

            if single_word.search(o):
                keyword = concat(normalize(re.sub('^(\w+)$ | ^(\w+\ ?\w+)$', r'\1', o))) # (here: spaces around |)
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue
            # ^ (\w+\ ?\w+)\?{0, 1}$
            if last_word.search(o):
                keyword = concat(normalize(re.sub('(.*)(\,[^\,\r\n]|\;[^\,\r\n])(\w+\ ?\w+)(\ et sim.|,\ et sim.){0,1}(\??)(\ \(\?\))?$', r'\3', o)))
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue

            if linne_cap_unobvious.search(o):
                keyword = concat(normalize(re.sub('(.*\ )([A-Z]\w+\ \w+)(.*)', r'\2', o)))
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue

            if linne_cap_single_unobvious.search(o):
                keyword = concat(normalize(re.sub('(.*\ )([A-Z]\w+)(.*)', r'\2', o)))
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue

            if sorte in o or sorte_apostr in o:
                keyword = concat(normalize(re.sub(r'.*(?<=\bsorte de|\bsorte d\')(?:\sgrand|\sgrande|\spetit|\spetite|\sgros|\sgrosse){0,1}\ {0,1}(\w+)(.*)', r'\1', normalize(o))))
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue

            if espece in o or espece_apostr in o:
                keyword = concat(normalize(re.sub(r'.*(?<=\bespèce de|\bespèce d\')(?:\sgrand|\sgrande|\spetit|\spetite|\sgros|\sgrosse){0,1}\ {0,1}(\w+)(.*)', r'\1', normalize(o))))
                page_py = wiki_wiki.page(keyword)
                if page_py.exists():
                    make_langlinks(s, page_py)
                    continue

            if (re.findall('\w+', o)):
                for word in (re.findall('\w+', o)):
                    if word not in blacklist:
                        page_py = wiki_wiki.page(word)
                        if page_py.exists():
                            make_langlinks(s, page_py)
                        else:
                            graph.add((s, ontolex + 'isConceptOf', Literal('to be mapped')))

            else:
                graph.add((s, ontolex + 'isConceptOf', Literal('to be mapped')))


def make_langlinks(s, page_py):
    langlinks = page_py.langlinks
    if langlinks:
        for k in sorted(langlinks):
            if 'en' in sorted(langlinks):
                if k == 'en':
                    url_en = langlinks[k].fullurl
                    # url = page_py.fullurl # for direct search in engl. Wikipedia
                    url_dbr = str(url_en).replace('https://en.wikipedia.org/wiki/', '')
                    graph.add((s, ontolex + 'isConceptOf', dbr + url_dbr))

            else:
                graph.add((s, ontolex + 'isConceptOf', Literal('missing english equivalent to French wikipedia entry')))
    else:
        graph.add((s, ontolex + 'isConceptOf', Literal('no equivalents to French wikipedia entry')))

def normalize(text):
    """ deletes / that indicates an Old French word within the definition; replaces characters; escapes ' """
    return str(text).replace('/', '').replace('œ', 'oe').replace('æ', 'ae').replace('?', '').replace("'", "\'")


def concat(text):
    """ turns white space into underscore """
    return str(text).replace(' ', '_')


def main():
    kwargs_json = {'ensure_ascii': False, 'indent': 2}
    mapped_entities_from_rdf = map_rdf(graph)

    print(json.dumps(mapped_entities_from_rdf, **kwargs_json, sort_keys=False))
    graph.serialize(destination='mapped_entities_from_rdf.ttl', format='turtle')


if __name__ == '__main__':
    main()
