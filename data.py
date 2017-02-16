from os import path, makedirs
from sqlalchemy.orm import sessionmaker
from time import time

from config import Config
from model import Repository, Owner, Code, metadata


class DataHandler:
    def __init__(self):
        print "Setting up code folder and configuration"
        if not path.exists('code-folder'):
            makedirs('code-folder')
        # import configuration
        self.config = Config()

        # setup the database
        Session = sessionmaker(bind=self.config.engine)
        metadata.create_all(self.config.engine, checkfirst=True)
        self.db = Session()

    def update_owner_table(self, item):
        owner = self.db.query(Owner).filter(Owner.id == item["repository"]["owner"]["id"]).first()
        if not owner:
            new_owner = Owner(
                id=item["repository"]["owner"]["id"],
                login=item["repository"]["owner"]["login"],
                html_url=item["repository"]["owner"]["html_url"],
            )
            self.db.add(new_owner)
            self.db.commit()

    def update_repository_table(self, item):
        repository = self.db.query(Repository).filter(Repository.id == item["repository"]["id"]).first()
        if not repository:
            new_repository = Repository(
                id=item["repository"]["id"],
                name=item["repository"]["name"],
                full_name=item["repository"]["full_name"],
                owner_id=item["repository"]["owner"]["id"],
                url=item["repository"]["url"],
                html_url=item["repository"]["html_url"],
                description=item["repository"]["description"],
                fork=item["repository"]["fork"],
            )
            self.db.add(new_repository)
            self.db.commit()

    def update_code_table(self, item, language, platform, local_path, download_url, content):
        new_items = 0
        updated_items = 0
        code = self.db.query(Code).\
            filter(Code.path == item["path"]).\
            filter(Code.repository_id == item["repository"]["id"]).\
            first()
        unixtime = int(time())
        if not code:
            new_code = Code(
                name=item["name"],
                path=item["path"],
                url=item["url"],
                html_url=item["html_url"],
                download_url=download_url,
                code=local_path,
                content=content,
                repository_id=item["repository"]["id"],
                date_added=unixtime,
                date_modified=unixtime,
                available=True,
                language=language,
                platform=platform,
            )
            self.db.add(new_code)
            self.db.commit()
            new_items = 1
        else:
            # wait for 8 hours to update at least
            if (code.content is not content) and (code.date_modified < (unixtime - (60 * 60 * 8))):
                code.content = content
                code.date_modified = unixtime
                self.db.commit()
                updated_items = 1

        return new_items, updated_items
