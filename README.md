# Title 

Llm are good generating code and also genereting SQL from text. Today we're going to play with it. The idea is use natural languaje to generate SQL querys. For the this experiment I've downloaded a csv with data from IMDB. Something like this example:

```csv
nconst,primaryname,birthyear,deathyear,primaryprofession,knownfortitles
nm0325022,Käthe Gold,1907,1997,"actress,archive_footage","tt0026069,tt0032498,tt0436641,tt0026066"
nm0325025,Lee Gold,1919,1985,writer,"tt0034433,tt0040392,tt0048226,tt0099219"
nm0325028,Louise Gold,1956,,"actress,miscellaneous,soundtrack","tt0074028,tt0104940,tt0083791,tt2281587"
...
```

Now we create a PostgreSQL database with docker. That's the Dockerfile

```dockerfile
FROM postgres:16.3-alpine
COPY actors.csv /docker-entrypoint-initdb.d/actors.csv
COPY init.sql /docker-entrypoint-initdb.d/
```

And we setup the database and import the csv into actors table in the docker engtrypoint

```sql
CREATE TABLE actors (
    nconst TEXT PRIMARY KEY,
    primaryname TEXT,
    birthyear INTEGER,
    deathyear INTEGER,
    primaryprofession TEXT,
    knownfortitles TEXT
);

COPY actors FROM '/docker-entrypoint-initdb.d/actors.csv' CSV HEADER;
```

That's the docker-compose file to set up the PostgreSQL database

```dockerfile
version: '3.6'

services:
  pg:
    build:
      context: .docker/pg
      dockerfile: Dockerfile
    ports:
      - 5432:5432
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_DB: ${POSTGRES_DB}
      PGDATA: /var/lib/postgresql/data/pgdata
```

Now we can start with the python script. We're going to use cick library to build cli scrpt.
The python application interacts with a database to execute SQL queries generated from user input. The process begins with obtaining a MovieChain object through the get_chain function, which takes an argument llm. This MovieChain object is then used to generate an SQL query based on the user's input q through its get_sql method. After that we just execute the SQL query into the PostgreSQL and print the results.

```python
import click
from dbutils import get_conn, Db, get_cursor
from lib.chains.movie import get_chain
from lib.llm.groq import llm
from settings import DSN


@click.command()
@click.option('--q', required=True, help='question to ask')
def run(q):
    chain = get_chain(llm)
    sql = chain.get_sql(q)
    click.echo(f"q: {q}")
    click.echo(sql)
    click.echo('')
    if sql:
        conn = get_conn(DSN, named=True, autocommit=True)
        db = Db(get_cursor(conn=conn))
        data = db.fetch_all(sql)
        for row in data:
            print(row)
```

The MovieChain class interacts with llm (in this example we're using groq).

```python
import logging
from langchain_core.messages import SystemMessage, HumanMessage

from .prompts import PROMPT

logger = logging.getLogger(__name__)


class MovieChain:

    def __init__(self, llm):
        self.llm = llm

        self.prompt = SystemMessage(content=PROMPT)

    def get_sql(self, q: str):
        user_message = HumanMessage(content=q)
        try:
            ai_msg = self.llm.invoke([self.prompt, user_message])
            output_message = ai_msg.content if not isinstance(ai_msg, str) else ai_msg

            return output_message
        except Exception as e:
            logger.error(f"Error during question processing: {e}")
```

The Chain uses two prompts. The system prompt thats creates the propper context to help llm to create the SQL query. We're providint the create table scrip.

```python
PROMPT = """
You are an expert in generating SQL queries based on user questions.
You have access to a database with the following table schema:

CREATE TABLE actors (
    nconst TEXT PRIMARY KEY,
    primaryname TEXT,
    birthyear INTEGER,
    deathyear INTEGER,
    primaryprofession TEXT,
    knownfortitles TEXT
);

Please generate an SQL query to answer the following user question.
Ensure the query is valid, secure, and tailored to the provided schema.
Return only the SQL query without additional explanations.
Don't use quotes around the query in any case.
"""
```

And that's all. With it we can ask quetions about this dataset and llm genetes the SQL for us.
```bash
python cli.py movie --q=List the living actors under 10 years old. 
q: List the living actors under 10 years old.
SELECT * FROM actors WHERE deathyear IS NULL AND birthyear > (EXTRACT(YEAR FROM CURRENT_DATE) - 10);
...
```

```bash
python cli.py movie --q=List the living actors who were born in the same year as Mel Gibson 
q: List the living actors who were born in the same year as Mel Gibson
SELECT * FROM actors WHERE birthyear = (SELECT birthyear FROM actors WHERE primaryname = 'Mel Gibson') AND deathyear IS NULL;
...
```

```bash
cli.py movie --q=List the deceased actors who were born in the same year as Mel Gibson. 
q: List the deceased actors who were born in the same year as Mel Gibson.
SELECT * 
FROM actors 
WHERE deathyear IS NOT NULL 
AND birthyear = (SELECT birthyear 
                 FROM actors 
                 WHERE primaryname = 'Mel Gibson');
...
```

```bash
python cli.py movie --q=What is the name, date of birth, and age of the oldest living actor born in the 70s? 
q: What is the name, date of birth, and age of the oldest living actor born in the 70s?
SELECT primaryname, birthyear, (2023 - birthyear) AS age 
FROM actors 
WHERE birthyear >= 1970 AND birthyear < 1980 AND deathyear IS NULL 
ORDER BY birthyear ASC 
LIMIT 1;

{'primaryname': 'Missy Gold', 'birthyear': 1970, 'age': 53}
```

With this kind of projects where we are executing "random" SQL generated by a llm we need to take care with the user that is connected to the database. We need to restrict the access to avoid posible SQL injection problems depending on the prompt that user provides when he asks to llm.