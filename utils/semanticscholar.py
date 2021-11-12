from pathlib import Path
from attrdict import AttrDict
import json
import time
import pickle
import urllib.request
import urllib.parse
from sumeval.metrics.rouge import RougeCalculator
import networkx as nx

from utils.common import Paper
from utils.utils import StrOrPath

class SemanticScholar(object):
    API = {
        'search_by_title': 'https://api.semanticscholar.org/graph/v1/paper/search?{QUERY}',
        'search_by_id': 'https://api.semanticscholar.org/graph/v1/paper/{PAPER_ID}?{PARAMS}',
    }
    
    def __init__(self, threshold=0.95):
        self.__api = AttrDict(self.API)
        self.__rouge = RougeCalculator(stopwords=True, stemming=False, word_limit=-1, length_limit=-1, lang="en")
        self.__threshold = threshold
        self.__graph, self.__papers = None, {}

    @property
    def threshold(self):
        return self.__threshold
    @property
    def G(self):
        return self.__graph
    @property
    def papers(self):
        return self.__papers

    def get_paper_id(self, title:str) -> str:
        params = {
            'query': title,
            'fields': 'title',
            'offset': 0,
            'limit': 100,
        }
        response = urllib.request.urlopen(self.__api.search_by_title.format(QUERY=urllib.parse.urlencode(params)))
        content = json.loads(response.read().decode('utf-8'))

        for item in content['data']:
            score = self.__rouge.rouge_l(summary=title, references=item['title'])
            if score > self.threshold:
                return item['paperId']
        return ''

    def get_paper_detail(self, paper_id:str) -> Paper:
        fields = [
            'paperId', 'url', 'title', 'abstract', 'venue', 'year',
            'referenceCount', 'citationCount', 'influentialCitationCount', 'isOpenAccess', 'fieldsOfStudy',
            'authors', 'citations', 'references', 'embedding'
        ]
        params = f'fields={",".join(fields)}'
        response = urllib.request.urlopen(self.__api.search_by_id.format(PAPER_ID=paper_id, PARAMS=params))
        content = json.loads(response.read().decode('utf-8'))
        return Paper(**content)

    def build_reference_graph(self, paper_id:str, min_influential_citation_count:int=1):
        '''build a reference graph
        
        Args:
            paper_id (str): if of the root paper
            min_influential_citation_count (int): number of citation count. ignore papers with the citation count under the threshold
        '''
        papers = {}
        counter = {'total': 0, 'done': 0}
        start = time.time()
        def process(g:nx.DiGraph, paper:Paper):
            counter['total'] += len(paper.citations)
            for citation in paper.citations:

                if citation.paper_id is None:
                    counter['done'] += 1
                    continue

                # get paper
                is_new = False
                if citation.paper_id in papers:
                    ci_paper = papers[citation.paper_id]
                else:
                    try:
                        ci_paper = self.get_paper_detail(citation.paper_id)
                        is_new = True
                        papers[citation.paper_id] = ci_paper
                        time.sleep(3)
                    except Exception as ex:
                        print(f'Warning: {ex} @{citation.paper_id}')
                        counter['done'] += 1
                        continue

                counter['done'] += 1
                if ci_paper.influential_citation_count >= min_influential_citation_count:
                    g.add_edge(paper.paper_id, citation.paper_id)
                    print(f' -> {counter["done"]:5d}/{counter["total"]:5d} ({counter["done"]/counter["total"]*100.0:5.1f}%) | '
                          f'etime: {(time.time() - start)/60.0:6.2f} min | '
                          f'papers: {len(papers):5d} | '
                          f'{paper.paper_id} -> {citation.paper_id} @icc: {ci_paper.influential_citation_count}')

                    if is_new:
                        process(g, ci_paper)

        root_paper:Paper = self.get_paper_detail(paper_id)
        g = nx.DiGraph()
        process(g, root_paper)

        self.__graph = g
        self.__papers = papers
        return papers, g

    def export(self, out_dir:StrOrPath):
        assert not(self.__graph is None or len(self.__papers) < 1), 'Reference graph is not build yet.'
        out_dir:Path = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # save graph
        nx.write_

        # save paper information
        papers_outfile = out_dir / 'papers.pickle'
        pickle.dump(self.__graph, open(papers_outfile, 'wb'))