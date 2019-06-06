import pandas as pd
import csv
import sys
import requests
from bs4 import BeautifulSoup
import random
from time import sleep

class related_search_hub:
    def __init__(self, start_search, depth_to_go=1, wait_time=random.uniform(.25,.75)):
        self.initial_search = start_search
        self.standard_wait = wait_time
        self.initial_query = '/hashtag/' + start_search[1:] if start_search[0] == '#' else '/search?q=' + start_search
        self.depth_to_go = depth_to_go
        self.level = 1
        self.error_list = []

    def get_results(self, query=False, search=False):
        query = query if query else self.initial_query
        search = search if search else self.initial_search
        print("Scraping https://twitter.com" + query + ".")
        results, new_queries = self.get_related_searches(query)
        if results:
            print(f"""Level {self.level} search for {search} yielded the related searches {results}.""")
            result_dict = dict(zip(
                ['type', 'level', 'search', 'result_1', 'result_2', 'result_3', 'result_4', 'result_5'],
                [('result', 'query'), self.level, (search, query)] + list(zip(results, new_queries)))
                              )
            if self.level == 1:
                self.results_df = pd.DataFrame(result_dict)
            else:
                self.results_df = pd.concat([self.results_df, pd.DataFrame(result_dict)], ignore_index=True, sort=False)
        else:
            print(f"""Level {self.level} search for {search} yielded an error.""")

    def go_deeper(self):
        result_matrix = self.results_df.loc[(self.results_df.level==self.level) & (self.results_df.type=='result'),'result_1':]
        query_matrix = self.results_df.loc[(self.results_df.level==self.level) & (self.results_df.type=='query'),'result_1':]
        self.level += 1
        self.depth_to_go -= 1
        rows = result_matrix.shape[0]
        earlier_searches_1 = self.results_df.loc[self.results_df.type=='result', 'search'].values
        earlier_searches_2 = []
        print('----- going deeper -----')
        for i in range(rows):
            R = result_matrix.iloc[i,:].dropna()
            Q = query_matrix.iloc[i,:].dropna()
            columns = R.shape[0]
            for j in range(columns):
                if (R[j] in earlier_searches_1) or (R[j] in earlier_searches_2):
                    pass
                else:
                    self.get_results(query=Q[j], search=R[j])
                    earlier_searches_2.append(R[j])
                    sleep(self.standard_wait)
        print(f'----- finished level {self.level} -----')

    def get_related_searches(self, query, waittime=random.uniform(.25,.75)):
        r = requests.get('http://www.twitter.com' + query)
        similar_results_bucket = BeautifulSoup(r.text, 'html.parser').find_all('ul', class_="AdaptiveRelatedSearches-items")
        if (similar_results_bucket and (similar_results_bucket[0].find_all('a', class_='js-nav'))):
            results = similar_results_bucket[0].find_all('a', class_='js-nav')
            names = [x.decode_contents().strip().replace('<strong>','').replace('</strong>','') for x in results]
            links = [x.attrs['href'][:-9] for x in results]
            return (names,links)
        else:
            print(f'----- error loading http://www.twitter.com{query} -----')
            self.error_list.append(query)
            return([], [])


    def results_as_csv(self, only_results=False):
        search_string = self.initial_search.replace(" ", "_")
        if not only_results:
            print('----- saving full csv -----')
            self.results_df.to_csv(f'results_{search_string}_depth{self.level}.csv', index=False)
        else:
            print('----- saving results only csv -----')
            self.results_df.loc[self.results_df.type=='result', 'level':].to_csv(f'results_only_{search_string}_depth{self.level}.csv', index=False)

    def export_gephi_csv(self):
        search_string = self.initial_search.replace(" ", "_")
        self.results_df.loc[self.results_df.type=='result','search':].to_csv(
            f'gephi_{search_string}_depth{self.level}.csv',
            index=False,
            header=False,
            sep=";",
            quoting=csv.QUOTE_ALL
            )

    def full_descent(self, with_output=False, only_results_output=False, with_gephi=False):
        self.get_results()
        self.depth_to_go -= 1
        while self.depth_to_go > 0:
            self.go_deeper()
        if self.error_list:
            print('----- there were loading errors -----')
            for x in self.error_list:
                  print(f'----- error while loading https://www.twitter.com/{x}  ----- ')
        else: pass
        if with_output:
            self.results_as_csv(only_results=only_results_output)
        if with_gephi:
            self.export_gephi_csv()
        else: pass
        print('----- alle done -----')


if __name__ == '__main__':
    search_item = str(sys.argv[1]).replace(' ', '%20')
    if len(sys.argv) >= 3:
        configuration = sys.argv[2:]
        make_gephi = True if 'gephi' in configuration else False
        make_output = True if 'output' in configuration else False
        results_only = True if (('results' in configuration) and make_output) else False
        depth = min([int(x) for x in configuration if x.isdigit()])
        X = related_search_hub(search_item, depth_to_go=depth)
        X.full_descent(with_output=make_output, only_results_output=results_only, with_gephi=make_gephi)
    else:
        X = related_search_hub(search_item)
        X.full_descent()
