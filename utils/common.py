from typing import Any, List
from collections import namedtuple
import numpy as np

Author = namedtuple('Author', ('author_id', 'name'))
RefPaper = namedtuple('RefPaper', ('paper_id', 'title'))

class Paper(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, f'__{key}', value)
        
    def __get(self, key:str, default:Any):
        return getattr(self, key) if hasattr(self, key) else default

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
        return int(self.__get('__citation_count', default=0))
    @property
    def influential_citation_count(self) -> int:
        return int(self.__get('__influentialCitationCount', default=0))
    @property
    def isOpenAccess(self) -> bool:
        return self.__get('__isOpenAccess', default=False)
    @property
    def fields_of_study(self) -> List[str]:
        return self.__get('__fieldsOfStudy', default=[])
    @property
    def embedding(self) -> np.ndarray:
        embedding = self.__get('__embedding', default={})
        if 'vector' in embedding:
            return np.array(embedding['vector'])
        else:
            return np.array([])
    @property
    def embed_model(self) -> str:
        embedding = self.__get('__embedding', default={})
        if 'model' in embedding:
            return embedding['model']
        else:
            return ''
    @property
    def authors(self) -> List[Author]:
        author_list = self.__get('__authors', default=[])
        return [Author(a['authorId'], a['name']) for a in author_list]
    @property
    def citations(self) -> List[RefPaper]:
        citation_list = self.__get('__citations', default=[])
        return [RefPaper(p['paperId'], p['title']) for p in citation_list]
    @property
    def references(self) -> List[RefPaper]:
        reference_list = self.__get('__references', default=[])
        return [RefPaper(p['paperId'], p['title']) for p in reference_list]

    def __str__(self):
        return f'<Paper id:{self.paper_id} title:{self.title[:15]}... >'
    def __repr__(self):
        return self.__str__()

