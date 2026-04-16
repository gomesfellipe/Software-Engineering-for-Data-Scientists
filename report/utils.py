import pickle
from pathlib import Path

# Path(__file__).parent → diretório report/
# .parent              → diretório raiz do projeto
# .resolve()           → caminho absoluto (sem ../ relativos)
project_root = Path(__file__).parent.parent.resolve()

# Aponta para assets/model.pkl a partir da raiz do projeto
model_path = project_root / "assets" / "model.pkl"


def load_model():
    """Carrega e retorna o modelo de machine learning serializado em pickle."""
    with model_path.open('rb') as file:
        model = pickle.load(file)
    return model
