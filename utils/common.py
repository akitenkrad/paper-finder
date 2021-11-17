from typing import Any, List
from collections import namedtuple
from datetime import datetime, timezone, timedelta
import numpy as np
from utils.utils import StrOrPath

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

    @property
    def paper_id(self) -> str:
        return self.__get('__paperId', default='')
    @property
    def url(self) -> str:
        return self.__get('__url', default='')
    @property
    def title(self) -> str:
        return self.__get('__title', default='')
    @property
    def abstract(self) -> str:
        return self.__get('__abstract', default='')
    @property
    def venue(self) -> str:
        return self.__get('__venue', default='')
    @property
    def year(self) -> int:
        return int(self.__get('__year', default=-1))
    @property
    def reference_count(self) -> int:
        return int(self.__get('__referenceCount', default=0))
    @property
    def citation_count(self) -> int:
        return int(self.__get('__citationCount', default=0))
    @property
    def influential_citation_count(self) -> int:
        return int(self.__get('__influentialCitationCount', default=0))
    @property
    def is_open_access(self) -> bool:
        return self.__get('__isOpenAccess', default=False)
    @property
    def fields_of_study(self) -> List[str]:
        return self.__get('__fieldsOfStudy', default=[])
    @property
    def embedding(self) -> np.ndarray:
        embedding = self.__get('__embedding', default={})
        if embedding is not None and 'vector' in embedding:
            return np.array(embedding['vector'])
        else:
            return np.array([])
    @property
    def embed_model(self) -> str:
        embedding = self.__get('__embedding', default={})
        if embedding is not None and 'model' in embedding:
            return embedding['model']
        else:
            return ''
    @property
    def authors(self) -> List[Author]:
        author_list = self.__get('__authors', default=[])
        return [Author(self.__filter_none(a['authorId']), self.__filter_none(a['name'])) for a in author_list]
    @property
    def citations(self) -> List[RefPaper]:
        citation_list = self.__get('__citations', default=[])
        return [RefPaper(p['paperId'], p['title']) for p in citation_list]
    @property
    def references(self) -> List[RefPaper]:
        reference_list = self.__get('__references', default=[])
        return [RefPaper(p['paperId'], p['title']) for p in reference_list]
    @property
    def at(self) -> datetime:
        ts = self.__get('__at', default=0)
        jst = timezone(timedelta(hours=9))
        return datetime.fromtimestamp(ts, tz=jst)

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
            'at': self.__get('__at', default=0),
        }
 