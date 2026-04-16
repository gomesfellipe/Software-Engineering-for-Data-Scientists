from pathlib import Path
from fasthtml.common import *
import matplotlib.pyplot as plt

# Importa as classes de query do pacote instalado employee_events
from employee_events import Employee, Team, QueryBase

# Importa a função que carrega o modelo de ML
from utils import load_model

# Componentes base (pré-construídos pelo time)
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
)

# Componentes compostos (pré-construídos pelo time)
from combined_components import FormGroup, CombinedComponent


# ─── CSS do relatório ──────────────────────────────────────────────────────────
# Carrega o CSS da pasta assets/ a partir da raiz do projeto
_css_path = Path(__file__).parent.parent / 'assets' / 'report.css'
_css = _css_path.read_text() if _css_path.exists() else ""


# ─── Subclasse 1: ReportDropdown ──────────────────────────────────────────────
# Herda Dropdown para criar um dropdown que se auto-popula com os nomes
# do modelo (employees ou teams) vindos do banco de dados.
class ReportDropdown(Dropdown):

    def build_component(self, entity_id, model):
        # Define o label do dropdown como o nome do tipo de entidade
        self.label = model.name.title()
        # Delega a construção do HTML para a classe pai
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        # Chama model.names() para buscar os (nome, id) do banco
        return model.names()


# ─── Subclasse 2: Header ──────────────────────────────────────────────────────
# Exibe o título da página como H1, indicando o tipo de dashboard.
class Header(BaseComponent):

    def build_component(self, entity_id, model):
        # model.name é 'employee' ou 'team'
        # .title() capitaliza → 'Employee' ou 'Team'
        return H1(f"{model.name.title()} Performance")


# ─── Subclasse 3: LineChart ───────────────────────────────────────────────────
# Gráfico de linha com contagem ACUMULADA de eventos positivos e negativos
# ao longo do tempo. Herda MatplotlibViz que converte a figura para HTML.
class LineChart(MatplotlibViz):

    def visualization(self, entity_id, model):
        # Busca os dados de eventos do banco
        df = model.event_counts(entity_id)

        # Preenche valores nulos com 0 (boa prática: nunca deixar NaN para o gráfico)
        df = df.fillna(0)

        # Define event_date como índice para o plot temporal
        df = df.set_index('event_date')

        # Ordena pelo índice (data) para garantir a sequência cronológica
        df = df.sort_index()

        # Transforma em contagem acumulada — mostra tendência ao longo do tempo
        df = df.cumsum()

        # Nomeia as colunas de forma legível
        df.columns = ['Positive', 'Negative']

        # Cria a figura e eixo matplotlib
        fig, ax = plt.subplots()
        df.plot(ax=ax)

        # Aplica estilos de eixo compatíveis com fundo escuro/claro
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

        ax.set_title('Cumulative Event Counts')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Count')


# ─── Subclasse 4: BarChart ────────────────────────────────────────────────────
# Barra horizontal mostrando o risco previsto de recrutamento [0, 1].
# Usa o modelo de ML carregado como atributo de classe.
class BarChart(MatplotlibViz):

    # Atributo de classe: o modelo é carregado UMA vez quando a classe é definida
    # (não a cada requisição). Princípio: operações caras fora do hot path.
    predictor = load_model()

    def visualization(self, entity_id, model):
        # Obtém os dados de features para o modelo (positive/negative events)
        data = model.model_data(entity_id).fillna(0)

        # predict_proba retorna [[prob_classe_0, prob_classe_1], ...]
        prediction = self.predictor.predict_proba(data)

        # Pega apenas a coluna 1 (probabilidade de ser recrutado)
        # Shape: (n_samples, 1)
        prediction = prediction[:, 1:]

        # Para time: média da probabilidade de todos os membros
        # Para employee: probabilidade do único registro
        if model.name == 'team':
            pred = prediction.mean()
        else:
            pred = prediction[0, 0]

        fig, ax = plt.subplots()

        # Código fornecido pelo template — não alterar
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)

        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')


# ─── Subclasse 5: Visualizations ─────────────────────────────────────────────
# CombinedComponent que agrupa LineChart e BarChart lado a lado (css grid).
class Visualizations(CombinedComponent):

    children = [LineChart(), BarChart()]

    # Mantém o layout em grid do PicoCSS (FastHTML usa PicoCSS por padrão)
    outer_div_type = Div(cls='grid')


# ─── Subclasse 6: NotesTable ──────────────────────────────────────────────────
# Tabela de notas do funcionário/time. Herda DataTable que monta o HTML da tabela.
class NotesTable(DataTable):

    def component_data(self, entity_id, model):
        # Delega a busca de dados para o método notes() do modelo
        return model.notes(entity_id)


# ─── DashboardFilters ─────────────────────────────────────────────────────────
# Formulário com radio (Employee/Team) e dropdown de seleção.
# Usa HTMX para atualizar o dropdown dinamicamente sem recarregar a página.
class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(
            id="selector",
            name="user-selection"
        )
    ]


# ─── Report ───────────────────────────────────────────────────────────────────
# Página completa: cabeçalho + filtros + visualizações + tabela de notas.
class Report(CombinedComponent):

    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable()
    ]


# ─── Inicialização do App FastHTML ────────────────────────────────────────────
# FastHTML é um framework Python que gera HTML diretamente — sem templates Jinja.
# Style() injeta o CSS inline no cabeçalho da página.
app = FastHTML(hdrs=(Style(_css),))

# Instancia o Report uma vez (reutilizado em todas as rotas)
report = Report()


# ─── Rotas ────────────────────────────────────────────────────────────────────

@app.get('/')
def index():
    """Página inicial: exibe o dashboard para o employee de id 1."""
    return report(1, Employee())


@app.get('/employee/{employee_id}')
def employee_page(employee_id: str):
    """Dashboard de um funcionário específico pelo seu ID."""
    return report(employee_id, Employee())


@app.get('/team/{team_id}')
def team_page(team_id: str):
    """Dashboard de um time específico pelo seu ID."""
    return report(team_id, Team())


# ─── Rotas auxiliares (fornecidas pelo template — não alterar) ────────────────

@app.get('/update_dropdown{r}')
def update_dropdown(r):
    """Atualiza o dropdown via HTMX quando o radio Employee/Team é alterado."""
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    """Processa o formulário e redireciona para a rota correta."""
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()
