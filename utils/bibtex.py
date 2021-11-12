import re
from typing import List
from pathlib import Path
from glob import glob
import pandas as pd

from utils.utils import StrOrPath

class Bibtex(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, f'__{key}', value)

    @property
    def abstract(self) -> str:
        '''abstract of the paper'''
        return getattr(self, '__abstract') if hasattr(self, '__abstract') else ''
    @property
    def address(self) -> str:
        '''address of the publisher'''
        return getattr(self, '__address') if hasattr(self, '__address') else ''
    @property
    def annote(self) -> str:
        '''annotation'''
        return getattr(self, '__annote') if hasattr(self, '__annote') else ''
    @property
    def authors(self) -> List[str]:
        '''list of authors'''
        if hasattr(self, '__author'):
            author_data = getattr(self, '__author')
            return [author.strip() for author in author_data.split(' and ')]
        else:
            return []
    @property
    def booktitle(self) -> str:
        '''title of the book if the paper is a part of the book'''
        return getattr(self, '__booktitle') if hasattr(self, '__booktitle') else ''
    @property
    def categories(self) -> List[str]:
        '''categories of the paper'''
        if hasattr(self, '__category'):
            category_data = getattr(self, '__category')
            return [category.strip() for category in category_data.split(',')]
        else:
            return []
    @property
    def crossref(self) -> str:
        '''cross reference key'''
        return getattr(self, '__crossref') if hasattr(self, '__crossref') else ''
    @property
    def chapter(self) -> str:
        '''name of the chapter'''
        return getattr(self, '__chapter') if hasattr(self, '__chapter') else ''
    @property
    def doi(self) -> str:
        '''digital object identifier'''
        return getattr(self, '__doi') if hasattr(self, '__doi') else ''
    @property
    def edition(self) -> str:
        '''edition of the book'''
        return getattr(self, '__edition') if hasattr(self, '__edition') else ''
    @property
    def editors(self) -> List[str]:
        '''name of the editor'''
        if hasattr(self, '__editor'):
            editor_data = getattr(self, '__editor')
            return [editor.strip() for editor in editor_data.split(' and ')]
        else:
            return []
    @property
    def eprint(self) -> str:
        '''preprint or technical report'''
        return getattr(self, '__eprint') if hasattr(self, '__eprint') else ''
    @property
    def howpublished(self) -> str:
        '''how the paper was published'''
        return getattr(self, '__howpublished') if hasattr(self, '__howpublished') else ''
    @property
    def isbn(self) -> str:
        '''isbn'''
        return getattr(self, '__isbn') if hasattr(self, '__isbn') else ''
    @property
    def issn(self) -> str:
        '''issn'''
        return getattr(self, '__issn') if hasattr(self, '__issn') else ''
    @property
    def institution(self) -> str:
        '''institution'''
        return getattr(self, '__institution') if hasattr(self, '__institution') else ''
    @property
    def journal(self) -> str:
        '''name of the journal'''
        return getattr(self, '__journal') if hasattr(self, '__journal') else ''
    @property
    def key(self) -> str:
        '''the key used when sorting'''
        return getattr(self, '__key') if hasattr(self, '__key') else ''
    @property
    def keywords(self) -> List[str]:
        '''keywords'''
        if hasattr(self, '__keywords'):
            keywords_data = getattr(self, '__keywords')
            return [keyword.strip() for keyword in keywords_data.split(',')]
        else:
            return []
    @property
    def month(self) -> str:
        '''month of publication'''
        return getattr(self, '__month') if hasattr(self, '__month') else ''
    @property
    def note(self) -> str:
        '''note'''
        return getattr(self, '__note') if hasattr(self, '__note') else ''
    @property
    def number(self) -> str:
        '''number of the journal'''
        return getattr(self, '__number') if hasattr(self, '__number') else ''
    @property
    def organization(self) -> str:
        '''organization of the conference'''
        return getattr(self, '__organization') if hasattr(self, '__organization') else ''
    @property
    def pages(self) -> str:
        '''pages of the paper'''
        return getattr(self, '__pages') if hasattr(self, '__pages') else ''
    @property
    def publisher(self) -> str:
        '''name of the publisher'''
        return getattr(self, '__publisher') if hasattr(self, '__publisher') else ''
    @property
    def school(self) -> str:
        '''name of the school if the paper is a dissertation'''
        return getattr(self, '__school') if hasattr(self, '__school') else ''
    @property
    def series(self) -> str:
        '''name of the series'''
        return getattr(self, '__series') if hasattr(self, '__series') else ''
    @property
    def title(self) -> str:
        '''title of the paper'''
        return getattr(self, '__title') if hasattr(self, '__title') else ''
    @property
    def type(self) -> str:
        '''type of the paper'''
        return getattr(self, '__type') if hasattr(self, '__type') else ''
    @property
    def url(self) -> str:
        '''url of the paper'''
        if hasattr(self, '__url'):
            return getattr(self, '__url')
        elif hasattr(self, '__doi'):
            return f'https://doi.org/{getattr(self, "__doi")}'
        else:
            return ''
    @property
    def volume(self) -> str:
        '''volume of the journal'''
        return getattr(self, '__volume') if hasattr(self, '__volume') else ''
    @property
    def year(self) -> int:
        return int(getattr(self, '__year')) if hasattr(self, '__year') else -1
    @property
    def tags(self) -> List[str]:
        '''list of authors'''
        if hasattr(self, '__mendeley_tags'):
            tag_data = getattr(self, '__mendeley_tags')
            return [tag.strip() for tag in tag_data.split(',')]
        else:
            return []

    def __str__(self):
        return f'<Bibtex "{" ".join(self.title.split()[:5])}..." >'
    def __repr__(self):
        return self.__str__()

    def to_dict(self, fields:List[str]):
        res = {}
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if isinstance(value, list):
                    value = ', '.join(value)
                res[field] = value
            else:
                raise KeyError(f'unknown field: {field}')
        return res

def parse(bibtex_path:StrOrPath) -> List[Bibtex]:
    '''parse bibtex files'''

    ptn_bib = re.compile(r'@[a-zA-Z]*?{(?P<BODY>[\s\S]*?)\n}\n')
    ptn_row = re.compile(r'(?P<KEY>[^=,\s{}"]+)\s*=\s*[{"]*(?P<VALUE>[^}"]+)["}]?,?')

    bibtex_path:Path = Path(bibtex_path)
    if bibtex_path.is_dir():
        bibtex_files = [Path(f) for f in glob(str(bibtex_path / '*.bib'))]
    else:
        bibtex_files = [bibtex_path]

    bibtex_list = []
    for bibtex_file in bibtex_files:
        bibtext = open(bibtex_file).read()
        bib_all = ptn_bib.findall(bibtext)
        for bib in bib_all:
            bibbody = [b.strip() for b in bib.split('\n')]
            bibargs = {}
            for row in bibbody:
                m = ptn_row.match(row)
                if m is not None:
                    key = m.group('KEY').replace('-', '_')
                    value = m.group('VALUE')
                    bibargs[key] = value
            bibtex_list.append(Bibtex(**bibargs))

    return bibtex_list

def to_csv(bibtex_list:List[Bibtex], fields:List[str], outfile:StrOrPath='bibtex.csv'):
    '''export bibtex info into excel'''
    outfile:Path = Path(outfile)
    df = []
    for bibtex in bibtex_list:
        df.append(bibtex.to_dict(fields))
    df = pd.DataFrame(df)

    outfile.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(outfile), header=True, index=False)
    print(f'exported -> {str(outfile.resolve().absolute())}')
