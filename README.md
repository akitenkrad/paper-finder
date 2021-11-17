# paper-finder

utils for searching information about technical papers

## Install
```bash
> git clone https://github.com/akitenkrad/paper-finder.git
```

## Examples

### bibtex -> csv
```python
>>> from utils.bibtex import parse, to_csv
>>> bibtex_list = parse('<PATH TO BIBTEX.bib>')
>>> fields = ['title', 'year', 'authors', 'journal', 'tags']
>>> to_csv(bibtex_list, fields=fields, outfile='bibtex.csv')
```

### build a reference graph

#### download cache file

https://drive.google.com/file/d/1pYDy3wwRWSLMOIon5XwpCcxwrOXA5yzC/view?usp=sharing

#### run
```python
>>> from utils.semantichsholar import SemanticSholar
>>> ss = SemanticSholar.from_cache('<PATH TO CACHE>')
>>> paper_id = ss.get_paper_id('<TITLE OF ROOT PAPER>')
>>> ss.build_reference_graph(paper_id=paper_id,
                             min_influential_citation_count=1,
                             cache='<PATH TO CACHE>.zip',
                             export_interval=100)
```
