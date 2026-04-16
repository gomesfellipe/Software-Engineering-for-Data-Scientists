from .query_base import QueryBase
from .sql_execution import query


class Team(QueryBase):
    """
    Subclasse de QueryBase para consultas específicas de times.

    Herda event_counts() e notes() de QueryBase.
    Define `name = 'team'` para que as queries herdadas
    usem a tabela e coluna corretas via f-string.
    """

    name = 'team'

    @query
    def names(self):
        """
        Retorna lista de (team_name, team_id) de todos os times.
        """
        return """
            SELECT team_name, team_id
            FROM team
            ORDER BY team_name
        """

    @query
    def username(self, id):
        """
        Retorna o nome do time com o id informado.
        Usado para exibir o cabeçalho do dashboard.
        """
        return f"""
            SELECT team_name
            FROM team
            WHERE team_id = {id}
        """

    def model_data(self, id):
        """
        Retorna um DataFrame com dados de eventos por funcionário do time.

        Diferente do Employee (que retorna 1 linha agregada), Team retorna
        N linhas — uma por funcionário — para que o modelo calcule a
        probabilidade de recrutamento de cada membro e depois tire a média.
        """
        return self.pandas_query(f"""
            SELECT positive_events, negative_events FROM (
                SELECT employee_id,
                       SUM(positive_events) AS positive_events,
                       SUM(negative_events) AS negative_events
                FROM {self.name}
                JOIN employee_events
                    USING({self.name}_id)
                WHERE {self.name}.{self.name}_id = {id}
                GROUP BY employee_id
            )
        """)
