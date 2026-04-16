from .query_base import QueryBase
from .sql_execution import query


class Employee(QueryBase):
    """
    Subclasse de QueryBase para consultas específicas de funcionários.

    Herda event_counts() e notes() de QueryBase.
    Define `name = 'employee'` para que as queries herdadas
    usem a tabela e coluna corretas via f-string.
    """

    name = 'employee'

    @query
    def names(self):
        """
        Retorna lista de (nome_completo, employee_id) de todos os funcionários.
        O decorator @query executa a string SQL retornada e devolve
        uma lista de tuplas automaticamente.
        """
        return """
            SELECT first_name || ' ' || last_name, employee_id
            FROM employee
            ORDER BY first_name
        """

    @query
    def username(self, id):
        """
        Retorna o nome completo do funcionário com o id informado.
        Usado para exibir o cabeçalho do dashboard.
        """
        return f"""
            SELECT first_name || ' ' || last_name
            FROM employee
            WHERE employee_id = {id}
        """

    def model_data(self, id):
        """
        Retorna um DataFrame com os dados agregados de eventos
        necessários para alimentar o modelo de machine learning.

        Retorna 1 linha com colunas: positive_events, negative_events.
        """
        return self.pandas_query(f"""
            SELECT SUM(positive_events) AS positive_events,
                   SUM(negative_events) AS negative_events
            FROM {self.name}
            JOIN employee_events
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
        """)
