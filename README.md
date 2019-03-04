# Wikidata's Users Editing Labels

All code is written in Python 2.7

## Database

We use a MongoDB database, the datbase is called *wikibabeldb*, it contains three collections: *anonymous*, *bots* and *registered*, each one for the respective user type.
Bots are considered all editors, that have a bot flag, as listed in https://www.wikidata.org/wiki/Wikidata:List_of_bots and users that have a *bot* pre- or suffix. 
The file to populate the database is a script and can be run with `python create-database.py`.

## Metrics
To run the metrics (...)