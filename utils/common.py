from typing import Any, List
from collections import namedtuple
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse as date_parse
import numpy as np

Author = namedtuple('Author', ('author_id', 'name'))
RefPaper = namedtuple('RefPaper', ('paper_id', 'title'))

class Paper(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, f'__{key}', value)
        
        if not hasattr(self, '__at'):
            self.__at = datetime.now().timestamp()
        
    def __get(self, key:str, default:Any) -> Any:
        value = getattr(self, key) if hasattr(self, key) else default
        if value is None:
            return default
        else:
            return value
    def __filter_none(self, value:Any, default:Any=''):
        if value is None:
            return default
        else:
            return value

    def add_fields(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, f'__{key}', value)

    @property
    def paper_id(self) -> str:
        '''paper id from SemanticScholar'''
        return self.__get('__paperId', default='')
    @property
    def url(self) -> str:
        '''url from SemanticScholar'''
        return self.__get('__url', default='')
    @property
    def title(self) -> str:
        '''title from SemanticScholar'''
        return self.__get('__title', default='')
    @property
    def abstract(self) -> str:
        '''abstract from SemanticScholar'''
        return self.__get('__abstract', default='')
    @property
    def venue(self) -> str:
        '''venue from SemanticScholar'''
        return self.__get('__venue', default='')
    @property
    def year(self) -> int:
        '''year from SemanticScholar'''
        return int(self.__get('__year', default=-1))
    @property
    def reference_count(self) -> int:
        '''reference count from SemanticScholar'''
        return int(self.__get('__referenceCount', default=0))
    @property
    def citation_count(self) -> int:
        '''citation count from SemanticScholar'''
        return int(self.__get('__citationCount', default=0))
    @property
    def influential_citation_count(self) -> int:
        '''influential citation count from SemanticScholar'''
        return int(self.__get('__influentialCitationCount', default=0))
    @property
    def is_open_access(self) -> bool:
        '''is open access from SemanticScholar'''
        return self.__get('__isOpenAccess', default=False)
    @property
    def fields_of_study(self) -> List[str]:
        '''fields of study from SemanticScholar'''
        return self.__get('__fieldsOfStudy', default=[])
    @property
    def embedding(self) -> np.ndarray:
        '''embedding from SemanticScholar'''
        embedding = self.__get('__embedding', default={})
        if embedding is not None and 'vector' in embedding:
            return np.array(embedding['vector'])
        else:
            return np.array([])
    @property
    def embed_model(self) -> str:
        '''embed model from SemanticScholar'''
        embedding = self.__get('__embedding', default={})
        if embedding is not None and 'model' in embedding:
            return embedding['model']
        else:
            return ''
    @property
    def authors(self) -> List[Author]:
        '''authors from SemanticScholar'''
        author_list = self.__get('__authors', default=[])
        return [Author(self.__filter_none(a['authorId']), self.__filter_none(a['name'])) for a in author_list]
    @property
    def citations(self) -> List[RefPaper]:
        '''citations from SemanticScholar'''
        citation_list = self.__get('__citations', default=[])
        return [RefPaper(p['paperId'], p['title']) for p in citation_list]
    @property
    def references(self) -> List[RefPaper]:
        '''references from SemanticScholar'''
        reference_list = self.__get('__references', default=[])
        return [RefPaper(p['paperId'], p['title']) for p in reference_list]
    @property
    def doi(self) -> str:
        '''doi from arxiv'''
        return self.__get('__doi', default='')
    @property
    def primary_category(self) -> str:
        '''primary_category from arxiv'''
        return self.__get('__primary_category', default='')
    @property
    def categories(self) -> List[str]:
        '''categories from arxiv'''
        return self.__get('__categories', default=[])
    @property
    def updated(self) -> datetime:
        '''updated from arxiv'''
        value = self.__get('__updated', default=None)
        if not value:
            return None
        else:
            return value
    @property
    def published(self) -> datetime:
        '''published from arxiv'''
        value = self.__get('__published', default=None)
        if not value:
            return None
        else:
            return value
    @property
    def at(self) -> datetime:
        '''timestamp'''
        ts = self.__get('__at', default=0)
        jst = timezone(timedelta(hours=9))
        return datetime.fromtimestamp(ts, tz=jst)

    @property
    def has_arxiv_info(self) -> bool:
        return 0 < len(self.primary_category) or \
               0 < len(self.categories) or \
               isinstance(self.updated) or \
               isinstance(self.published)

    def __str__(self):
        return f'<Paper id:{self.paper_id} title:{self.title[:15]}... @{self.at.strftime("%Y.%m.%d-%H:%M:%S")}>'
    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            'abstract': self.abstract,
            'authors': [{'author_id': a.author_id, 'name': a.name} for a in self.authors],
            'citation_count': self.citation_count,
            'citations': [{'paper_id': r.paper_id, 'title': r.title} for r in self.citations if r.paper_id is not None],
            'embed_model': self.embed_model,
            'embedding': self.embedding.tolist(),
            'fields_of_study': self.fields_of_study,
            'influential_citation_count': self.influential_citation_count,
            'is_open_access': self.is_open_access,
            'paper_id': self.paper_id,
            'reference_count': self.reference_count,
            'references': [{'paper_id': r.paper_id, 'title': r.title} for r in self.references if r.paper_id is not None],
            'title': self.title,
            'url': self.url,
            'venue': self.venue,
            'year': self.year,
            'doi': self.doi,
            'primary_category': self.primary_category,
            'categories': [{'category': cat} for cat in self.categories],
            'updated': self.updated.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.updated, datetime) else '',
            'published': self.published.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.published, datetime) else '',
            'at': self.__get('__at', default=0),
        }
 
    @staticmethod
    def from_dict(paper_data:dict):
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
            'doi': paper_data['doi'] if 'doi' in paper_data else '',
            'primary_category': paper_data['primary_category'] if 'primary_category' in paper_data else '',
            'categories': [cat['category'] for cat in paper_data['categories']] if 'categories' in paper_data else [],
            'updated': date_parse(paper_data['updated']) if 'updated' in paper_data and paper_data['updated'] != '' else None,
            'published': date_parse(paper_data['published']) if 'published' in paper_data and paper_data['published'] != '' else None,
            'at': paper_data['at'],
        }
        return Paper(**kwargs)

