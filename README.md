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