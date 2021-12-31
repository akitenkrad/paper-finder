from typing import Dict, Optional
from pathlib import Path
from attrdict import AttrDict
import json
import time
from urllib.error import URLError, HTTPError
import urllib.request
import urllib.parse
import socket
from sumeval.metrics.rouge import RougeCalculator
import networkx as nx

from utils.common import Paper

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

    @property
    def threshold(self) -> float:
        return self.__threshold

    def __retry_and_wait(self, msg:str, ex:Exception, retry:int) -> int:
        retry += 1
        if 5 < retry: raise ex
        if retry == 1: msg = '\n' + msg

        print(msg)

        if ex.errno == -3:
            time.sleep(300.0)
        else:
            time.sleep(5.0)
        return retry

    def get_paper_id(self, title:str) -> str:

        retry = 0
        while retry < 5:
            try:
                params = {
                    'query': title,
                    'fields': 'title',
                    'offset': 0,
                    'limit': 100,
                }
                response = urllib.request.urlopen(self.__api.search_by_title.format(QUERY=urllib.parse.urlencode(params)), timeout=5.0)
                content = json.loads(response.read().decode('utf-8'))
                time.sleep(3.0)
                break

            except HTTPError as ex:
                retry = self.__retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)
            except URLError as ex:
                retry = self.__retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)
            except socket.timeout as ex:
                retry = self.__retry_and_wait(f'API Timeout -> Retry: {retry}', ex, retry)
            except Exception as ex:
                retry = self.__retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)
            
            if 5 <= retry:
                print(f'No paper-id found @ {title}')
                return ''

        for item in content['data']:
            score = self.__rouge.rouge_l(summary=title.lower(), references=item['title'].lower())
            if score > self.threshold:
                return item['paperId'].strip()
        return ''

    def get_paper_detail(self, paper_id:str) -> Optional[Paper]:
 
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
                time.sleep(3.0)
                break

            except HTTPError as ex:
                retry = self.__retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)
            except URLError as ex:
                retry = self.__retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)
            except socket.timeout as ex:
                retry = self.__retry_and_wait(f'API Timeout -> Retry: {retry}', ex, retry)
            except Exception as ex:
                retry = self.__retry_and_wait(f'{str(ex)} -> Retry: {retry}', ex, retry)
            
            if 5 <= retry:
                raise Exception(f'No paper found @ {paper_id}')

        content = json.loads(response.read().decode('utf-8'))
        return Paper(**content)
