from typing import Dict, List
from pathlib import Path
from datetime import datetime
from attrdict import AttrDict
from enum import Enum
import hashlib
import json
from tqdm import tqdm
import arxiv

from utils.utils import StrOrPath
from utils.arxiv_utils import ArXivCategory


class ArXiv(object):
    QUERY:Dict[str, str] = {
        'search_cat_submitted_date': 'cat:{CATEGORY} AND submittedDate:[{START} TO {END}]'
    }

    def __init__(self):
        self.__query = AttrDict(ArXiv.QUERY)

    def save_cat_submitted_date(self, cat:ArXivCategory, start:datetime, end:datetime, save_dir:StrOrPath='') -> List[dict]:
        res = arxiv.Search(query=self.__query.search_cat_submitted_date.format(
            CATEGORY=cat.value.name,
            START=start.strftime('%Y%m%d%H%M%S'),
            END=end.strftime('%Y%m%d%H%M%S')))

        with tqdm() as pbar:
            for paper in res.results():
                paper_hash = hashlib.md5((paper.title + paper.get_short_id()).encode('utf-8')).hexdigest()
                data = {
                    'id': paper.entry_id,
                    'hash': paper_hash,
                    'title': paper.title,
                    'authors': [{'name': author.name} for author in paper.authors],
                    'summary': paper.summary,
                    'doi': paper.doi if paper.doi is not None else '',
                    'primary_category': paper.primary_category,
                    'categories': paper.categories,
                    'url': paper.links[0].href if len(paper.links) > 0 else '',
                    'pdf_url': paper.pdf_url if paper.pdf_url is not None else '',
                    'updated': paper.updated.strftime('%Y-%m-%d %H:%M:%S') if paper.updated is not None else '',
                    'published': paper.published.strftime('%Y-%m-%d %H:%M:%S') if paper.published is not None else '',
                    'ss_id': '',
                }
                
                paper_path = Path(save_dir) / paper_hash[0] / paper_hash[1] / paper_hash[2] / f'{paper_hash}.json'
                pbar.set_description(f'{str(paper_path.resolve().absolute())}')
                pbar.update(1)

                paper_path.parent.mkdir(parents=True, exist_ok=True)
                json.dump(data, open(paper_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
