from typing import Dict
import sys
from pathlib import Path
import time
import json
import re
from tqdm import tqdm
from glob import glob
from dateutil.parser import parse as date_parse
import networkx as nx

from utils.common import Paper
from utils.semanticscholar import SemanticScholar
from utils.arxiv import ArXiv
from utils.utils import StrOrPath, now, timedelta2HMS

class PaperFinderUtil(object):

    def __init__(self, ss_threshold:float=0.95):
        self.ss = SemanticScholar(threshold=ss_threshold)
        self.axv = ArXiv()
        self.graph:nx.DiGraph = nx.DiGraph()
        self.papers:Dict[str, Path] = {}

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
    def merge_arxiv(self, arxiv_dir:StrOrPath='__cache__/papers', ss_dir:StrOrPath='__cache__/arxiv'):
        arxiv_dir:Path = Path(arxiv_dir)
        ss_dir:Path = Path(ss_dir)
        arxiv_papers = [Path(f) for f in tqdm(glob(str(arxiv_dir / '**' / '*.json'), recursive=True), desc='load arxiv papers', leave=False)]

        with tqdm(arxiv_papers) as it:
            for arxiv_paper_path in it:
                arxiv_paper = json.load(open(arxiv_paper_path))

                try:
                    # 1. get title
                    if 'ss_id' in arxiv_paper and len(arxiv_paper['ss_id']) > 0:
                        paper_id = arxiv_paper['ss_id']
                    else:
                        title = re.sub(r'\$.+\$', '', arxiv_paper['title'], count=100).strip()
                        paper_id = self.ss.get_paper_id(title)

                    it.set_description(paper_id)

                    if paper_id == '':
                        print(f'Warning: cannot find paper id -> {arxiv_paper["title"]}')
                        json.dump(arxiv_paper, open(arxiv_paper_path, 'w', encoding='utf-8'))
                        continue
                    arxiv_paper['ss_id'] = paper_id

                    # 2. get detail
                    paper:Paper = self.get_paper(paper_id)

                    try:
                        updated = date_parse(arxiv_paper['updated'])
                    except Exception as ex:
                        print(f'Warning: {ex} @{paper_id}')
                        updated = ''
                
                    try:
                        published = date_parse(arxiv_paper['published'])
                    except Exception as ex:
                        print(f'Warning: {ex} @{paper_id}')
                        published = ''

                    kwargs = {
                        'doi': arxiv_paper['doi'],
                        'primary_category': arxiv_paper['primary_category'],
                        'categories': arxiv_paper['categories'],
                        'updated': updated,
                        'published': published,
                        'arxiv_hash': arxiv_hash['hash'],
                        'arxiv_id': arxiv_paper['id'],
                        'arxiv_title': arxiv_paper['title'],
                    }
                    paper.add_fields(**kwargs)

                    # 3. save paper
                    self.export_paper(paper, ss_dir)
                    json.dump(arxiv_paper, open(arxiv_paper_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
                    
                except Exception as ex:
                    print(f'Warning: {ex} @{arxiv_paper["title"]}')
                    continue
                    
            
    def build_reference_graph(self,
            paper_id:str,
            min_influential_citation_count:int=1,
            max_depth:int=3,
            cache_dir:StrOrPath='__cache__/papers',
            export_interval:int=1000):
        '''build a reference graph
        
        Args:
            paper_id (str): if of the root paper
            min_influential_citation_count (int): number of citation count. ignore papers with the citation count under the threshold
            max_depth (int): max depth
            cache_dir (StrOrPath): path to cache directory
            export_interval (int): export cache with the specified interval
        '''
        sys.setrecursionlimit(10000)
        stats = {'total': 0, 'done': 0, 'paper_queue': [], 'new_papers': [], 'finished_papers': [], 'cache_dir': Path(cache_dir)}
        graph_cache = stats['cache_dir'] / f'{paper_id}.graphml'
        start = time.time()

        root_paper = self.get_paper(paper_id)
        stats['paper_queue'].insert(0, (root_paper, 0))
        stats['total'] += len(root_paper.citations)
        while 0 < len(stats['paper_queue']):

            paper, depth = stats['paper_queue'].pop()

            if max_depth < depth:
                return

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
                try:
                    ci_paper:Paper = self.get_paper(ci_ref_paper.paper_id)
                    new_paper_path = self.export_paper(ci_paper, cache_dir)
                    self.papers[ci_paper.paper_id] = new_paper_path
                    stats['new_papers'].append(ci_paper)

                except Exception as ex:
                    print(f'Warning: {ex} @{ci_ref_paper.paper_id}')
                    stats['done'] += 1
                    continue

                # 3. add the new paper into the list
                stats['done'] += 1
                if ci_paper.influential_citation_count >= min_influential_citation_count:
                    self.__add_edge(self.graph, paper, ci_paper)
                    self.__show_progress__(stats['total'], stats['done'], start, depth=depth, paper=paper, ci_paper=ci_paper)

                    if ci_paper.paper_id not in stats['finished_papers']:
                        stats['finished_papers'].append(ci_paper.paper_id)
                        stats['paper_queue'].insert(0, (ci_paper, depth + 1))
                        stats['total'] += len(ci_paper.citations)

        # post process
        self.export_graph(stats['cache_dir'] / f'{paper_id}.graphml')
        self.__show_progress__(stats['total'], stats['done'], start, zip_path=stats['cache_dir'] / f'{paper_id}.graphml')
        print('Done.')

    def __add_edge(self, graph:nx.DiGraph, src:Paper, dst:Paper):
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
            graph.nodes[paper.paper_id]['primary_category'] = paper.primary_category

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
        if paper_id in self.papers:
            paper_path = self.papers[paper_id]
            paper = Paper.from_dict(json.load(open(paper_path)))
        else:
            paper = self.ss.get_paper_detail(paper_id)
        return paper

    @staticmethod
    def from_cache(cache_path:StrOrPath, threshold:float=0.95, no_cache:bool=False):
        cache_path:Path = Path(cache_path)
        
        pf_util = PaperFinderUtil()

        print('Reading files from cache...')
        cache_papers = [Path(f) for f in tqdm(glob(str(cache_path / '**' / '*.json'), recursive=True), leave=False)]
        for cache_paper in tqdm(cache_papers, desc='Loading...', leave=False):
            pf_util.papers[cache_paper.stem] = cache_paper

        print(f'Loaded papers: {len(pf_util.papers)}')
        return pf_util
