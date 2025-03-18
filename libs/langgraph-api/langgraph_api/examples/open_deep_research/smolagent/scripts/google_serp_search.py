from serpapi.serp_api_client import *


class GoogleSerpSearch(SerpApiClient):
    """GoogleSearch enables to search google and parse the result.
    ```python
    from serpapi import GoogleSearch
    query = GoogleSearch({"q": "coffee", "location": "Austin,Texas"})
    data = query.get_json()
    ```

    https://github.com/serpapi/google-search-results-python
    """

    def __init__(self, params_dict):
        super(GoogleSerpSearch, self).__init__(params_dict, GOOGLE_ENGINE)
