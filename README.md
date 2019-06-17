# Twitter Related Search Scraper

To use this from the command line, navigate to the folder of
`twitter_rss.py` and type:

`python twitter_rss.py <search term> <depth> <output variables>`

- `<search term>` : term to start searching twitter for (string)
- `<depth>` : depth to continue the search to (integer)
- `<output variables>` : "gephi" for gephi csv output
                     "output" for result csv output
                     "output results" for result csv output without queries



## Inline documentation:

"""Twitter Related Search Scraper

This script scrapes Twitter for the related searches of a query and continues
with the gathered new queries until the specified depth of search is reached.

The first command line argument is a string that is the start of the search.
Following this arguments can be added to
    * specify the depth of the search (as integer)
    * make the script export a gephi-readable csv -> add "gephi"
    * make the script export a csv of search terms and queries -> add "output"
    * make the script export a csv of only the search terms
        -> add "results" in addition to "output"
These additions can be made in any order. If multiple integers are given, the
script runs on the smallest.

The script requires the packages pandas, csv, sys, requests, bs4, random, time.

This file can also be imported as a module and contains the class(es):
    * related_search_hub
"""

class related_search_hub:
    """
    A class used to represent one scraping instance.

    ...

    Atributes
    ---------
    initial_search : str
        A string with the search term to start the scraping with.
    initial_query : str
        A string containing the formatted query to be added to the twitter url.
    depth_to_go : int
        The depth to which the subsearches are executed. Starts at a given value
        and is reduced while descending.
    level : int
        Interger denoting the level to which the search was already executed.
    standard_wait : float
        Floating point number denoting the wait time between requests to
        twitter. Default value is random between .25 and .75 seconds.
    error_list : list
        List to track the errors while accessing twitter. Starts empty and is
        filled when running the script - reported at the end.
    results_df : pd.DataFrame
        DataFrame that stores the results of the searches as well as future
        search queries. Columns are
        type|level|search|result_1|result_2|...|result_5

    Methods
    -------
    get_related_searches(query)
        Access twitter and gets the related searches connected to the provided
        query string. Returns a tuple of the result and query list.
    get_results(query=False, search=False)
        Uses get_related to access twitter and stores results in results_df.
    go_deeper()
        Automatedly conducts all the searches in the current level, increases
        level, decreases depth_to_go, and writes all results into results_df.
    results_as_csv(only_results=False)
        Exports results_df as csv in current directory. If only_results is True
        omits the search querie rows.
    export_gephi_csv()
        Exports results_df as gephi readable csv. Import to gephi as undirected
        graph with method sum for multiple edge occurrences.
    full_descent(with_output=False, only_results_output=False, with_gephi=False)
        Automatedly conducts all the searches until the specified depth is
        reached. Arguments specify the type of csv output.
            * with_output uses results_as_csc and passes only_results_output on.
            * with_gephi uses export_gephi_csv.
    """
