from typing import Dict
from pathlib import Path
from attrdict import AttrDict
import json
import time
import zipfile
from tqdm import tqdm
import urllib.request
import urllib.parse
from sumeval.metrics.rouge import RougeCalculator
import networkx as nx

from utils.common import Paper
from utils.utils import StrOrPath, now, timedelta2HMS

class SemanticScholar(object):
    API = {
        'search_by_title': 'https://api.semanticscholar.org/graph/v1/paper/search?{QUERY}',
        'search_by_id': 'https://api.semanticscholar.org/graph/v1/paper/{PAPER_ID}?{PARAMS}',
    }
    
    def __init__(self, threshold=0.95):
        self.__api = AttrDict(self.API)
        self.__rouge = RougeCalculator(stopwords=True, stemming=False, word_limit=-1, length_limit=-1, lang="en")
        self.__threshold = threshold
        self.__graph:nx.DiGraph = nx.DiGraph()
        self.__papers:Dict[str, Paper] = {}

    @property
    def threshold(self) -> float:
        return self.__threshold
    @property
    def graph(self) -> nx.DiGraph:
        return self.__graph
    @property
    def papers(self) -> Dict[str, Paper]:
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

    def build_reference_graph(self, paper_id:str, min_influential_citation_count:int=1, cache:StrOrPath='__cache__/papers.zip', export_interval:int=1000):
        '''build a reference graph
        
        Args:
            paper_id (str): if of the root paper
            min_influential_citation_count (int): number of citation count. ignore papers with the citation count under the threshold
            cache (StrOrPath): path to cache. the cache file is assumed to be ".zip" format. 
            export_interval (int): export cache with the specified interval
        '''
        counter = {'total': 0, 'done': 0, 'new_papers':0, 'cache': Path(cache)}
        start = time.time()
        def process(ss:SemanticScholar, paper:Paper):
            counter['total'] += len(paper.citations)
            for citation in paper.citations:
                
                if len(ss.papers) > 0 and counter['new_papers'] == export_interval:
                    ss.export(counter['cache'])
                    counter['new_papers'] = 0

                if citation.paper_id is None:
                    counter['done'] += 1
                    continue

                # get paper
                is_new = False
                if citation.paper_id in ss.papers:
                    ci_paper = ss.__papers[citation.paper_id]
                else:
                    try:
                        ci_paper = self.get_paper_detail(citation.paper_id)
                        is_new = True
                        ss.__papers[citation.paper_id] = ci_paper
                        counter['new_papers'] += 1
                        time.sleep(3)

                    except Exception as ex:
                        print(f'Warning: {ex} @{citation.paper_id}')
                        counter['done'] += 1
                        continue

                counter['done'] += 1
                if ci_paper.influential_citation_count >= min_influential_citation_count:
                    ss.graph.add_edge(paper.paper_id, citation.paper_id)
                    print(f' -> {counter["done"]:5d}/{counter["total"]:5d} ({counter["done"]/counter["total"]*100.0:5.1f}%) | '
                          f'etime: {timedelta2HMS(int(time.time() - start))} @{now().strftime("%Y.%m.%d-%H:%M:%S")} | '
                          f'papers: {len(ss.papers):5d} | '
                          f'{paper.paper_id[:8]} -> {citation.paper_id[:8]} @icc: {ci_paper.influential_citation_count}')

                    if is_new:
                        process(ss, ci_paper)

        root_paper:Paper = self.get_paper_detail(paper_id)
        process(self, root_paper)

    def export(self, out_file:StrOrPath='papers.zip'):
        assert len(self.__papers) > 0, 'Reference graph is not build yet.'
        out_file:Path = Path(out_file)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(str(out_file), 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for paper_id, paper in tqdm(self.__papers.items(), total=len(self.papers), desc='exporting...', leave=False):
                if paper is None:
                    continue
                data = paper.to_dict()
                zf.writestr(f'{paper_id}.json', json.dumps(data, ensure_ascii=False, indent=2))
        print(f'exported -> {str(out_file.resolve().absolute())}')

    @staticmethod
    def from_cache(cache_path:StrOrPath, threshold=0.95):
        cache_path:Path = Path(cache_path)

        papers = {}
        with zipfile.ZipFile(str(cache_path), 'r') as zf:
            for file_info in tqdm(zf.filelist, total=len(zf.filelist), desc='loading...'):
                paper_id = Path(file_info.filename).stem
                paper_data = json.loads(zf.read(file_info))
                kwargs = {
                    'paperId': paper_data['paper_id'],
                    'url': paper_data['url'],
                    'title': paper_data['title'],
                    'abstract': paper_data['abstract'],
                    'venue': paper_data['venue'],
                    'year': paper_data['year'],
                    'referenceCount': paper_data['reference_count'],
                    'citationCount': paper_data['citation_count'],
                    'influentialCitationCount': paper_data['influential_citation_count'],
                    'isOpenAccess': paper_data['is_open_access'],
                    'fieldsOfStudy': paper_data['fields_of_study'],
                    'embedding': {'vector': paper_data['embedding'], 'model': paper_data['embed_model']},
                    'authors': [{'authorId': a['author_id'], 'name': a['name']} for a in paper_data['authors']],
                    'citations': [{'paperId': r['paper_id'], 'title': r['title']} for r in paper_data['citations']],
                    'references': [{'paperId': r['paper_id'], 'title': r['title']} for r in paper_data['references']],
                    'at': paper_data['at'],
                }
                papers[paper_id] = Paper(**kwargs)

        ss = SemanticScholar(threshold=threshold)
        ss.__papers = papers
        return ss
