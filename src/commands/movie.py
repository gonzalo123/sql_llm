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
