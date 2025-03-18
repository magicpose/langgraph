#!/user/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional

import aiohttp
from smolagents import Tool


class GoogleSerperSearchTool(Tool):
    name = "web_search"
    description = """Performs a google web search for your query then returns a string of the top search results."""
    inputs = {
        "query": {"type": "string", "description": "The search query to perform."},
        "filter_year": {
            "type": "integer",
            "description": "Optionally restrict results to a certain year",
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self):
        super().__init__(self)
        import os

        self.serpapi_key = os.getenv("SERPAPI_API_KEY")

    def forward(self, query: str, filter_year: Optional[int] = None) -> list:
        import requests

        if self.serpapi_key is None:
            raise ValueError("Missing SerpAPI key. Make sure you have 'SERPAPI_API_KEY' in your env variables.")

        headers = {
            'X-API-KEY': self.serpapi_key or '',
            'Content-Type': 'application/json',
        }
        params = {
            'q': query,
            'gl': 'cn',
            'hl': 'zh-CN'
        }

        if filter_year is not None:
            params["tbs"] = f"cdr:1,cd_min:01/01/{filter_year},cd_max:12/31/{filter_year}"

        response = requests.post('https://proxy-serper.e-tudou.com/search',
                      headers=headers,
                      params=params)

        web_snippets = []

        web_snippets.extend(response.json()['organic'])

        # convert search results to ToolReturn format
        # if status_code == -1:
        #     tool_return.errmsg = response
        #     tool_return.state = ActionStatusCode.HTTP_ERROR
        # elif status_code == 200:
        #     parsed_res = self._parse_results(response)
        #     tool_return.result = [dict(type='text', content=str(parsed_res))]
        #     tool_return.state = ActionStatusCode.SUCCESS
        # else:
        #     tool_return.errmsg = str(status_code)
        #     tool_return.state = ActionStatusCode.API_ERROR
        # return tool_return
        #
        # if "organic_results" not in results.keys():
        #     if filter_year is not None:
        #         raise Exception(
        #             f"No results found for query: '{query}' with filtering on year={filter_year}. Use a less restrictive query or do not filter on year."
        #         )
        #     else:
        #         raise Exception(f"No results found for query: '{query}'. Use a less restrictive query.")
        # if len(results["organic_results"]) == 0:
        #     year_filter_message = f" with filter year={filter_year}" if filter_year is not None else ""
        #     return f"No results found for '{query}'{year_filter_message}. Try with a more general query, or remove the year filter."

        # if "organic_results" in results:
        #     for idx, page in enumerate(results["organic_results"]):
        #         date_published = ""
        #         if "date" in page:
        #             date_published = "\nDate published: " + page["date"]
        #
        #         source = ""
        #         if "source" in page:
        #             source = "\nSource: " + page["source"]
        #
        #         snippet = ""
        #         if "snippet" in page:
        #             snippet = "\n" + page["snippet"]
        #
        #         redacted_version = f"{idx}. [{page['title']}]({page['link']}){date_published}{source}\n{snippet}"
        #
        #         redacted_version = redacted_version.replace("Your browser can't play this video.", "")
        #         web_snippets.append(redacted_version)

        return web_snippets
        # return "## Search Results\n" + "\n\n".join(web_snippets)