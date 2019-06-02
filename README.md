# Wikidata's Users Editing Labels

This repository provides scripts to extract information on users editing of labels in Wikidata, split into three user types: anonymous users, bots and registered users. 


All code is written in Python 2.7

## Database

To create the database use the script *create-database-psql.py*. It is necessary to download the Wikidata dump (currently *wikidatawiki-20190302-stub-meta-history.xml.gz*) from https://dumps.wikimedia.org/wikidatawiki/. Further, the list of bots is needed, which is available at https://www.wikidata.org/wiki/Wikidata:List_of_bots. 
We use a PSQL database, the datbase is called *wikibabeldb*, it contains three tables: *anonymous*, *bots* and *registered*, each one for the respective user type. Each table contains *username, comment, sha1, language, format, timestamp, parentid, item_id, model, id*, based on the revision information from Wikidata. 

We limit the revisions written to the database to those that are label edits (marked with *wbsetlabel-set* or *wbsetlabel-add* in the comment). 

Bots are considered all editors, that have a bot flag, as listed in https://www.wikidata.org/wiki/Wikidata:List_of_bots and users that have a *bot* pre- or suffix. 
Anonymous users are all users that have a an IP address instead of a username (which is saved in the username field in the PSQL database), registered users are users that are neither bots nor anonymous.


First, we created a MongoDB database, the datbase is called *wikibabeldb*, it contains three collections: *anonymous*, *bots* and *registered*, each one for the respective user type, the file to populate the database is a script and can be run with `python create-database.py`. However, MongoDB limits the documents it returns in size, therefore it did not work for the analysis part of the code. We still make the code available in case it is helpful in other use cases. 

## Metrics
To reproducce the analysis, the code can be found in the Metrics folder. *run.py* runs the whole pipeline from data analysis to graph creation. *metricspsql.py* contains all classes to analyse the data, *graph.py* contains the classes for the creation of graphs. 
Again, *metrics.py* is written for the MongoDB setup, but due to limitations of MongoDB is not used by us but might be useful for future work. 
