from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

# pathlib garante que o caminho funciona no Windows, Mac e Linux
# __file__ é o caminho deste próprio arquivo em tempo de execução
db_path = Path(__file__).parent / 'employee_events.db'


# OPTION 1: MIXIN
# Um Mixin é uma classe auxiliar que NÃO é instanciada sozinha.
# Ela é incluída na cadeia de herança de QueryBase para fornecer
# os métodos de execução SQL sem repetição de código (DRY).
class QueryMixin:

    def pandas_query(self, sql, args=None):
        """Executa uma query SQL e retorna o resultado como DataFrame pandas."""
        conn = connect(db_path)
        df = pd.read_sql_query(sql, conn, params=args)
        conn.close()
        return df

    def query(self, sql, args=None):
        """Executa uma query SQL e retorna o resultado como lista de tuplas."""
        conn = connect(db_path)
        cursor = conn.cursor()
        result = cursor.execute(sql, args or []).fetchall()
        conn.close()
        return result


# OPTION 2: DECORATOR (deixado no template original para referência)
# O decorator envolve uma função que retorna uma string SQL,
# executa a query e retorna os resultados automaticamente.
def query(func):
    """
    Decorator que executa a string SQL retornada pela função decorada
    e devolve o resultado como lista de tuplas.
    """
    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    return run_query
