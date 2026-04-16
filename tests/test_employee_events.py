import pytest
from pathlib import Path

# Path(__file__).parent → diretório tests/
# .parent              → raiz do projeto
# .absolute()          → caminho absoluto
project_root = Path(__file__).parent.parent.absolute()


@pytest.fixture
def db_path():
    """
    Fixture que retorna o caminho para o banco SQLite.

    Uma fixture do pytest é uma função que prepara recursos para os testes.
    O decorator @pytest.fixture a registra e o pytest a injeta automaticamente
    nos testes que declaram o mesmo nome como parâmetro.
    """
    return project_root / "python-package" / "employee_events" / "employee_events.db"


def test_db_exists(db_path):
    """Verifica que o arquivo do banco de dados existe no caminho esperado."""
    assert db_path.is_file()


@pytest.fixture
def db_conn(db_path):
    """Fixture que abre e retorna uma conexão SQLite com o banco."""
    from sqlite3 import connect
    return connect(db_path)


@pytest.fixture
def table_names(db_conn):
    """Fixture que retorna a lista de nomes de todas as tabelas do banco."""
    name_tuples = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    return [x[0] for x in name_tuples]


def test_employee_table_exists(table_names):
    """Verifica que a tabela 'employee' existe no banco."""
    assert 'employee' in table_names


def test_team_table_exists(table_names):
    """Verifica que a tabela 'team' existe no banco."""
    assert 'team' in table_names


def test_employee_events_table_exists(table_names):
    """Verifica que a tabela 'employee_events' existe no banco."""
    assert 'employee_events' in table_names
