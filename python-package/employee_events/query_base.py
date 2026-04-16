from .sql_execution import QueryMixin


class QueryBase(QueryMixin):
    """
    Classe base para todas as queries do banco employee_events.

    Herda de QueryMixin para ganhar os métodos pandas_query() e query()
    sem precisar reimplementar a lógica de conexão ao banco.

    Subclasses definem o atributo `name` ('employee' ou 'team')
    e sobrescrevem `names()` com a query específica do seu tipo.
    """

    # Atributo de classe — identifica o tipo de entidade.
    # Subclasses sobrescrevem com 'employee' ou 'team'.
    # Usado com f-strings para construir queries dinamicamente.
    name = ''

    def names(self):
        """Retorna lista de (nome, id) de todas as entidades. Subclasses sobrescrevem."""
        return []

    def event_counts(self, id):
        """
        Retorna um DataFrame com contagens de eventos positivos e negativos
        agrupados por data para a entidade de id fornecido.

        Usa f-string para construir a cláusula FROM/JOIN/WHERE dinamicamente
        com base no atributo `name` da subclasse (employee ou team).
        """
        return self.pandas_query(f"""
            SELECT event_date,
                   SUM(positive_events) AS positive_events,
                   SUM(negative_events) AS negative_events
            FROM {self.name}
            JOIN employee_events
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
            GROUP BY event_date
            ORDER BY event_date
        """)

    def notes(self, id):
        """
        Retorna um DataFrame com as notas (note_date, note) associadas
        à entidade de id fornecido.
        """
        return self.pandas_query(f"""
            SELECT note_date, note
            FROM notes
            JOIN {self.name}
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
            ORDER BY note_date
        """)
