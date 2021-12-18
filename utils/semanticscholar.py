from typing import Dict, List
import sys
from pathlib import Path
from attrdict import AttrDict
import json
import time
import pickle
from tqdm import tqdm
from glob import glob
from urllib.error import URLError, HTTPError
import urllib.request
import urllib.parse
import socket
from sumeval.metrics.rouge import RougeCalculator
import networkx as nx

from utils.common import Paper
from utils.utils import StrOrPath, now, timedelta2HMS

class SemanticScholar(object):
    API:Dict[str, str] = {
        'search_by_title': 'https://api.semanticscholar.org/graph/v1/paper/search?{QUERY}',
        'search_by_id': 'https://api.semanticscholar.org/graph/v1/paper/{PAPER_ID}?{PARAMS}',
    }
    CACHE_PATH:Path = Path('__cache__/papers.pickle')
    
    def __init__(self, threshold:float=0.95):
        self.__api = AttrDict(self.API)
        self.__rouge = RougeCalculator(stopwords=True, stemming=False, word_limit=-1, length_limit=-1, lang="en")
        self.__threshold = threshold
        self.graph:nx.DiGraph = nx.DiGraph()
        self.papers:Dict[str, Path] = {}

    @property
    def threshold(self) -> float:
        return self.__threshold

    def dict2paper(self, paper_data:dict):
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
        return Paper(**kwargs)

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

        def retry_and_wait(msg:str, ex:Exception, retry:int) -> int:
            retry += 1
            if 5 < retry: raise ex
            if retry == 1: msg = '\n' + msg

            print(msg)

            if ex.errno == -3:
                time.sleep(300.0)
            else:
                time.sleep(5.0)
            return retry
 
        retry = 0
        while retry < 5:
            try:
                fields = [
                    'paperId', 'url', 'title', 'abstract', 'venue', 'year',
                    'referenceCount', 'citationCount', 'influentialCitationCount', 'isOpenAccess', 'fieldsOfStudy',
                    'authors', 'citations', 'references', 'embedding'
                ]
                params = f'fields={",".join(fields)}'
                response = urllib.request.urlopen(self.__api.search_by_id.format(PAPER_ID=paper_id, PARAMS=params), timeout=5.0)
                break
            except HTTPError as ex:
                retry = retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)
            except URLError as ex:
                retry = retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)
            except socket.timeout as ex:
                retry = retry_and_wait(f'API Timeout -> Retry: {retry}', ex, retry)
            except Exception as ex:
                retry = retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)

        content = json.loads(response.read().decode('utf-8'))
        return Paper(**content)

    def __show_progress__(self, total:int, done:int, start:float, leave:bool=True,
                          export_papers:bool=False, graph_path:StrOrPath='',
                          depth:int=1, paper:Paper=None, ci_paper:Paper=None):
        res = (f' -> {done:5d}/{total:5d} ({done / (total + 1e-10) * 100.0:5.2f}%) | '
               f'etime: {timedelta2HMS(int(time.time() - start))} @{now().strftime("%H:%M:%S")}')
        
        if export_papers: 
            res += f' | exported -> {len(self.papers):5d} papers'
        if graph_path != '':
            res += f' | exported -> {str(Path(graph_path).resolve().absolute())}'
        if paper is not None and ci_paper is not None:
            res += f' | papers: {len(self.papers):5d}'
            res += f' | {paper.paper_id[:5]} -> {ci_paper.paper_id[:5]} @icc: {ci_paper.influential_citation_count:4d}'
            res += f' | {"=" * (depth // 100)}{"+" * ((depth % 100) // 10)}{"-" * (depth % 10)}★'
        
        if leave == False:
            res = f'\r{res} | processing {done} papers...\r'

        if leave:
            print(res)
        else:
            print(res, end='')

    def build_reference_graph(self, paper_id:str, min_influential_citation_count:int=1, cache_dir:StrOrPath='__cache__/papers', export_interval:int=1000):
        '''build a reference graph
        
        Args:
            paper_id (str): if of the root paper
            min_influential_citation_count (int): number of citation count. ignore papers with the citation count under the threshold
            cache (StrOrPath): path to cache directory
            export_interval (int): export cache with the specified interval
        '''
        sys.setrecursionlimit(10000)
        stats = {'total': 0, 'done': 0, 'paper_queue': [], 'new_papers': [], 'finished_papers': [], 'cache_dir': Path(cache_dir)}
        graph_cache = stats['cache_dir'] / f'{paper_id}.graphml'
        start = time.time()

        root_paper = self.get_paper_detail(paper_id)
        stats['paper_queue'].insert(0, (root_paper, 0))
        stats['total'] += len(root_paper.citations)
        while 0 < len(stats['paper_queue']):

            paper, depth = stats['paper_queue'].pop()

            for ci_ref_paper in paper.citations:

                if ci_ref_paper.paper_id is None:
                    stats['done'] += 1
                    continue

                # 1. show progress
                self.__show_progress__(stats['total'], stats['done'], start, leave=False)

                if len(self.papers) > 0 and len(stats['new_papers']) >= export_interval and len(self.papers) % export_interval == 0:
                    self.export_graph(graph_cache)
                    self.__show_progress__(stats['total'], stats['done'], start, graph_path=graph_cache)
                    stats['new_papers'] = []

                # 2. get paper detail
                if ci_ref_paper.paper_id in self.papers:
                    ci_paper:Paper = self.get_paper(ci_ref_paper.paper_id)
                else:
                    try:
                        ci_paper:Paper = self.get_paper_detail(ci_ref_paper.paper_id)
                        new_paper_path = self.export_paper(ci_paper, cache_dir)
                        self.papers[ci_paper.paper_id] = new_paper_path
                        stats['new_papers'].append(ci_paper)
                        time.sleep(3.0)

                    except Exception as ex:
                        print(f'Warning: {ex} @{ci_ref_paper.paper_id}')
                        stats['done'] += 1
                        continue

                # 3. add the new paper into the list
                stats['done'] += 1
                if ci_paper.influential_citation_count >= min_influential_citation_count:
                    self.add_edge(self.graph, paper, ci_paper)
                    self.__show_progress__(stats['total'], stats['done'], start, depth=depth, paper=paper, ci_paper=ci_paper)

                    if ci_paper.paper_id not in stats['finished_papers']:
                        stats['finished_papers'].append(ci_paper.paper_id)
                        stats['paper_queue'].insert(0, (ci_paper, depth + 1))
                        stats['total'] += len(ci_paper.citations)

        # post process
        self.export_graph(stats['cache_dir'] / f'{paper_id}.graphml')
        self.__show_progress__(stats['total'], stats['done'], start, zip_path=stats['cache_dir'] / f'{paper_id}.graphml')
        print('Done.')

    def add_edge(self, graph:nx.DiGraph, src:Paper, dst:Paper):
        graph.add_edge(src.paper_id, dst.paper_id)
        
        for paper in [src, dst]:
            if paper.paper_id is None:
                continue
            graph.nodes[paper.paper_id]['name'] = paper.paper_id
            graph.nodes[paper.paper_id]['paper_id'] = paper.paper_id
            graph.nodes[paper.paper_id]['title'] = paper.title
            graph.nodes[paper.paper_id]['year'] = paper.year
            graph.nodes[paper.paper_id]['venue'] = paper.venue
            graph.nodes[paper.paper_id]['reference_count'] = paper.reference_count
            graph.nodes[paper.paper_id]['citation_count'] = paper.citation_count
            graph.nodes[paper.paper_id]['influential_citation_count'] = paper.influential_citation_count
            graph.nodes[paper.paper_id]['first_author_name'] = paper.authors[0].name if len(paper.authors) > 0 else ''
            graph.nodes[paper.paper_id]['first_author_id'] = paper.authors[0].author_id if len(paper.authors) > 0 else ''
            graph.nodes[paper.paper_id]['first_fields_of_study'] = paper.fields_of_study[0] if len(paper.fields_of_study) > 0 else ''

    def export_paper(self, paper:Paper, out_dir:StrOrPath='__cache__/papers') -> Path:
        out_dir:Path = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        d1, d2, d3 = paper.paper_id[:3]
        outfile:Path = out_dir / d1 / d2 / d3 / f'{paper.paper_id}.json'
        outfile.parent.mkdir(parents=True, exist_ok=True)

        data = paper.to_dict()
        json.dump(data, open(outfile, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        return outfile

    def export_graph(self, outfile:StrOrPath='papers.graphml'):
        outfile:Path = Path(outfile)
        outfile.parent.mkdir(parents=True, exist_ok=True)

        nx.write_graphml_lxml(self.graph, str(outfile.resolve().absolute()), encoding='utf-8', prettyprint=True, named_key_ids=True)

    def get_paper(self, paper_id:str) -> Paper:
        paper_path = self.papers[paper_id]
        paper = self.dict2paper(json.load(open(paper_path)))
        return paper

    @staticmethod
    def from_cache(cache_path:StrOrPath, threshold:float=0.95, no_cache:bool=False):
        cache_path:Path = Path(cache_path)
        
        ss = SemanticScholar(threshold=threshold)

        print('Reading files from cache...')
        cache_papers = [Path(f) for f in tqdm(glob(str(cache_path / '**' / '*.json'), recursive=True), leave=False)]
        for cache_paper in tqdm(cache_papers, desc='Loading...', leave=False):
            ss.papers[cache_paper.stem] = cache_paper

        print(f'Loaded papers: {len(ss.papers)}')
        return ss
