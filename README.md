# paper-finder

## Install
```bash
> git clone https://github.com/akitenkrad/paper-finder.git
```

## Example

### bibtex -> csv
```python
>>> from utils.bibtex import parse, to_csv
>>> bibtex_list = parse('<PATH TO BIBTEX.bib>')
>>> fields = ['title', 'year', 'authors', 'journal', 'categories']
>>> to_csv(bibtex_list, fields=fields, outfile='bibtex.csv')
```