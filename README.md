# Crawling Ethereum smart contracts from GitHub
This crawler is intended to crawl specific files from GitHub. It uses the GitHub search API [search code functionality](https://developer.github.com/v3/search/#search-code) to search for specific keywords in code files and certain extensions. When it finds these files, they are stored locally on the file system and indexed in a SQL database. The crawler is based on Python and is written in Python 2. In case you want to use it with Python 3, you will need to update the ```print``` statements. Also, this project is intended as a "quick and dirty" crawler, so it is not properly tested and there is currently no logging. Please feel free to extend/alter the program the program to your specifications.

## Setup python
Copy the repository files to a local directory. It is a good practice to have a virtualenv setup. From your local folder you can install the python requirements in your virtualenv.

```
pip install -r requirements.txt
```

## Setup PostgreSQL
I like and use PostgreSQL, but you can also use another SQL like DB with minimal adjustments. If you also want to use PostgreSQL install it on your machine.

```
sudo apt-get install postgresql postgresql-contrib
```

If you like a GUI then install it.

```
sudo apt-get install pgadmin3
```

Then set up the server according to this tutorial: [https://help.ubuntu.com/community/PostgreSQL](https://help.ubuntu.com/community/PostgreSQL)

The crawler expects a PostgreSQL user and a database to store the contracts. You could for example create the following users and databases. Make sure your user has the rights to create and alter tables in the DB.

```
user: github-crawler
password: your-password-here
db: smartcontracts
```

## Setup the crawler
In the root folder of the crawler create a ```config.yml``` file. To crawl all GitHub repositories you will need to create a token on GitHub. Follow the steps described here: [https://help.github.com/articles/creating-an-access-token-for-command-line-use/](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
Fill in the details to setup the crawler as described below. You can of course change the configuration, if you e.g. have a remote SQL server or want to search for different queries/extensions.

```
sql:
    host: localhost
    user: github-crawler
    password: your-password-here
    db: smartcontracts
    port: 5432
github:
    token:  your-github-token
    user: your-github-user
types:
    ethereum:
        extension: sol
        term: contract
        language: solidity
        platform: ethereum
```

In types, the search is configured. If you like to extend it, just add your new types and then instantiate the objects in the main method. Please note that GitHub limits your API requests!

```
types:
    ethereum:
        extension: sol
        term: contract
        language: solidity
        platform: ethereum
    hyperledger-java:
        extension: java
        term: ChaincodeBase
        language: Java
        platform: hyperledger-fabric
    hyperledger-go:
        extension: go
        term: chaincode
        language: go
        platform: hyperledger-fabric
```

## Run the crawler

```
python __main__.py >> /tmp/github-crawler.log 2>&1
```

You could also run it as a cronjob in the background. Just edit your cronfile.

```
crontab -e
```

Add this line to crawl it at noon every day.

```
00 12 * * * /usr/bin/python2.7 /home/github-crawler/crawler/__main__.py >> /tmp/github-crawler.log 2>&1
```

## Userful links
[https://developer.github.com/v3/rate_limit/](https://developer.github.com/v3/rate_limit/)

[help.github.com/articles/searching-code/](help.github.com/articles/searching-code/)

## ToDo
- include logging
- include unit tests
- package to deb
