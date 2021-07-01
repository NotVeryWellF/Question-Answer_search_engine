# Question-Answer_search_engine

## Description

Event-based Question-Answer Search Engine, that works on the set of news articles, ranks them using temporal data from the articles and query, and tries to answer the question + estimate time scope of the query, based on the retrieved articles 

## Set-up the environment

! Really hard task, because there are a lot of dependencies

> python 3.6 [!ONLY]

> SUTime can require downloading the library as a folder and import by path and installing java dependencies (everything in the official page)

> Model for the bidaf-keras can be downloaded from the official page of the project bidaf-keras

> Dataset is in the repo, but if you want to try yours, you need to have format as in the preprocessed.json

> Installation can take some time, patience is required

## Start app

> `python3.6 app.py`

Wait till app is started (Can take some time, because of the bidaf model and sutime loading)

In browser:
> `localhost:5000/search`
