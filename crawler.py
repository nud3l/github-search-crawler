"""
GitHub Solidity contract crawler
GitHub search API restrictions: https://help.github.com/articles/searching-code/
- Only the default branch is considered. In most cases, this will be the master branch.
- Only files smaller than 384 KB are searchable.
- Only repositories with fewer than 500,000 files are searchable.
"""
from sortedcontainers import SortedSet
from time import time, asctime, localtime

from config import Config
from data import DataHandler
from requester import RequestHandler


class Crawler:
    def __init__(self, platform):
        # setup configuration
        self.config = Config()
        term = self.config.types[platform]['term']
        extension = self.config.types[platform]['extension']

        self.language = self.config.types[platform]['language']
        self.platform = self.config.types[platform]['platform']

        # setup request handler
        self.requester = RequestHandler(term, extension)

        # setup data handler
        self.data = DataHandler()

        # configure crawler specifics
        self.size_range = SortedSet()
        self.size_range.update([0, 384001])  # stick to GitHub size restrictions
        self.initial_items = []
        print "Started GitHub crawler at {}".format(asctime(localtime(time())))

    def crawl(self):
        total_count = self.requester.get_total_count()
        target_count = total_count
        print "Crawler found {} items to store and fetch".format(total_count)
        item_count = 0

        current_item = 0
        next_item = 1

        start_time = int(time())

        # sort items differently to get more items
        # order_state 0 = default ordering (best match according to "score")
        # order_state 1 = last indexed
        # order_state 2 = first indexed
        order_state = 1

        # GitHub only provides 1000 items per request
        while item_count < total_count:
            print "Crawler looks in range {} to {} Byte".format(
                self.size_range[current_item],
                (self.size_range[next_item] - 1),
            )

            # We might get everything from just one request
            if (len(self.size_range) is 2) and (total_count < 1000):
                # excluding the lower and upper bound will use the items we got from our initial request
                lower = None
                upper = None
            # in case we need more then one request
            else:
                lower = self.size_range[current_item]
                upper = self.size_range[next_item]
                print "Setting lower and upper bound to {} and {}".format(lower, upper)

            # get items, request item count and incomplete status
            items, this_item_count, incomplete_items = self.requester.get_items(lower, upper, target_count, order_state)

            # update item count
            item_count += this_item_count
            print "Crawler got {} out of {} items".format(this_item_count, target_count)

            # write the items we got in this request to the DB
            new_items = 0
            updated_items = 0
            for item in items:
                self.data.update_owner_table(item)
                self.data.update_repository_table(item)
                local_path, download_url, content = self.requester.store_locally(
                        item["url"],
                        item["repository"]["id"],
                        item["path"]
                )
                new, updated = self.data.update_code_table(
                        item=item,
                        language=self.language,
                        platform=self.platform,
                        local_path=local_path,
                        download_url=download_url,
                        content=content,
                )
                if (new or updated) is 1:
                    self.requester.download(local_path, download_url)
                new_items += new
                updated_items += updated

            # update target count for new items
            target_count -= (new_items + updated_items)

            print "Crawler stored {} new items and updated {} items in the database".format(new_items, updated_items)

            # in case our results are incomplete or we have more than 1000 items we need to narrow down our search field
            if (incomplete_items or (this_item_count > 1000)) and ((next_item + 1) is len(self.size_range)):
                # get items with different ordering
                if order_state is 0:
                    order_state = 1
                elif order_state is 1:
                    order_state = 2
                elif order_state is 2:
                    new_boundaries = []
                    for i in xrange(len(self.size_range) - 1):
                        new_boundaries.append(int((self.size_range[i] + self.size_range[i + 1]) / 2) + 1)
                    self.size_range.update(new_boundaries)  # include the new boundary into our sorted list
                    print "Crawler introduced new boundaries: {}".format(self.size_range)

                    current_item = 0
                    next_item = 1

                    order_state = 1
            # jump to the next search area until we are at the end
            elif (next_item + 1) < len(self.size_range):
                current_item += 1
                next_item += 1

            timeout = True if (start_time < (int(time() - (60 * 60 * 8)))) else False

            if (target_count is 0) or timeout:
                print "Crawler is finished"
                if timeout:
                    print "Timeout after 8 hours"
                break
