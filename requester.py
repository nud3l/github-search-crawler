from os import path, makedirs
from requests.auth import HTTPBasicAuth
import requests
import hashlib

from time import time, sleep
from sortedcontainers import SortedSet

from config import Config


class RequestHandler:
    def __init__(self, term, extension):
        # setup configuration
        self.config = Config()

        # setup GitHub OAuth
        self.auth = HTTPBasicAuth(self.config.github['user'], self.config.github['token'])

        # configure crawler specifics
        self.github_url = 'https://api.github.com/search/code?q='  # use the GitHub search API
        self.query = '{}+extension:{}'.format(term, extension)  # search for contract in files with extension .sol
        self.sort = '&sort='
        self.order = '&order='
        self.size_range = SortedSet()
        self.size_range.update([0, 384001])  # stick to GitHub size restrictions
        self.initial_items = []

    def rate_limit(self, request):
        limit = requests.get('https://api.github.com/rate_limit', auth=self.auth)
        limit_json = limit.json()

        if request is 'search':
            remaining_search = limit_json["resources"]["search"]["remaining"]
            reset_time = limit_json["resources"]["search"]["reset"]

            if remaining_search is 0:
                # wait until we can do search requests again
                sleep_time = reset_time - int(time())
                print "Search limit reached. Waiting {} seconds".format(sleep_time)
                sleep(sleep_time)
        elif request is 'core':
            remaining_download = limit_json["resources"]["core"]["remaining"]
            reset_time = limit_json["resources"]["core"]["reset"]

            if remaining_download is 0:
                # wait until we can do search requests again
                sleep_time = reset_time - int(time())
                print "Core limit is reached. Waiting {} seconds".format(sleep_time)
                sleep(sleep_time)

    def search_github(self, lower, upper, order_state):
        self.rate_limit(request='search')
        if isinstance(lower, int) and isinstance(upper, int) and isinstance(order_state, int):
            base_url = self.github_url + self.query + "+size:>{}+size:<{}+size:{}".format(lower, upper, upper)
            if order_state is 1:
                url = base_url + self.sort + "indexed" + self.order + "desc"
            elif order_state is 2:
                url = base_url + self.sort + "indexed" + self.order + "asc"
            else:
                url = base_url

            print "Get contracts from {}".format(url)
            response = requests.get(url, auth=self.auth)
        else:
            response = requests.get(self.github_url + self.query, auth=self.auth)

        if response.status_code is 200:
            result = response.json()
        else:
            print "No valid GitHub credentials found."
            result = None

        return result

    def get_total_count(self):
        incomplete_results = True
        result = dict()

        # Get total number of files that contain search term
        while incomplete_results:
            print "Get total number of contracts from {}".format(self.github_url + self.query)
            try:
                result = self.search_github(None, None, None)
                incomplete_results = result["incomplete_results"]
            except TypeError:
                print "Could not search GitHub"
                break

        # in case we have less then 1000 results, store this to limit API calls
        self.initial_items = result["items"]
        total_count = result["total_count"]

        return total_count

    def get_items(self, lower, upper, target_count, order_state):
        items = self.initial_items
        this_item_count = len(items)
        incomplete_items = False

        try:
            result = self.search_github(lower, upper, order_state)
            items = result["items"]
            this_item_count = len(items)
            incomplete_items = True if (this_item_count < target_count) else False
        except TypeError:
            print "Could not search GitHub"

        return items, this_item_count, incomplete_items

    def get_download_url_content(self, url):
        self.rate_limit(request='core')

        # GitHub only gives you the download url when you request it for each file
        response = requests.get(url, auth=self.auth)
        if response.status_code is 200:
            result = response.json()
            download_url = result["download_url"]
            # This is the hash for the complete file line by line
            content_full = result["content"]
            # We want just one hash for the whole file for faster comparison of changes
            content = hashlib.md5(content_full).hexdigest()
        else:
            print "No valid GitHub credentials found."
            download_url = None
            content = None

        return download_url, content

    def store_locally(self, url, repository_id, remote_path):
        # get download url
        download_url, content = self.get_download_url_content(url)

        # create folder structure
        current_path = path.dirname(path.abspath(__file__))
        file_path = '{}/code-folder/{}/{}'.format(current_path, repository_id, remote_path)
        local_path = file_path.rpartition("/")[0]

        if not path.exists(local_path):
            makedirs(local_path)

        return file_path, download_url, content

    def download(self, file_path, download_url):
        self.rate_limit(request='core')

        print "Downloading {}".format(file_path)
        response = requests.get(download_url, auth=self.auth)
        with open(file_path, 'wb') as out_file:
            out_file.write(response.content)
        del response
