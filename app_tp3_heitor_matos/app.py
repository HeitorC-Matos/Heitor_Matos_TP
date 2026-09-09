import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import date, datetime
from numbers import Number


st.set_page_config(
    page_title="Rio Turismo | 2001",
    page_icon="🌴",
    layout="wide"
)

if "dados_carregados" not in st.session_state:
    st.session_state["dados_carregados"] = {}

if "preferencias" not in st.session_state:
    st.session_state["preferencias"] = {}

if "versoes_upload" not in st.session_state:
    st.session_state["versoes_upload"] = {"468": 0, "1289": 0, "1290": 0}

if "base_preferida" not in st.session_state:
    st.session_state["base_preferida"] = None

if "cores" not in st.session_state:
    st.session_state["cores"] = {
        "painel": "#111111",
        "fonte": "#F5F5F5"
    }


def guardar_cor(campo, chave):
    st.session_state["cores"][campo] = st.session_state[chave]


def guardar_preferencia(codigo, campo, chave):
    st.session_state["preferencias"][codigo][campo] = st.session_state[chave]


def guardar_coluna_filtro(codigo, chave):
    st.session_state["preferencias"][codigo]["coluna"] = st.session_state[chave]
    st.session_state["preferencias"][codigo]["valor"] = "Todos"
    st.session_state.pop("valor_" + codigo, None)


def guardar_base():
    st.session_state["base_preferida"] = st.session_state["base_selecionada"]


def limpar_filtros(codigo):
    st.session_state["preferencias"][codigo] = {}
    for campo in ["completos", "coluna", "valor", "colunas", "busca"]:
        st.session_state.pop(campo + "_" + codigo, None)


def remover_arquivo(codigo):
    st.session_state["dados_carregados"].pop(codigo, None)
    st.session_state["versoes_upload"][codigo] += 1


if "cor_painel" not in st.session_state:
    st.session_state["cor_painel"] = st.session_state["cores"]["painel"]

if "cor_fonte" not in st.session_state:
    st.session_state["cor_fonte"] = st.session_state["cores"]["fonte"]

with st.sidebar.expander("🎨 Personalizar cores"):
    cor_painel = st.color_picker(
        "Cor de fundo do painel lateral",
        key="cor_painel",
        on_change=guardar_cor,
        args=("painel", "cor_painel")
    )
    cor_fonte = st.color_picker(
        "Cor dos textos",
        key="cor_fonte",
        on_change=guardar_cor,
        args=("fonte", "cor_fonte")
    )

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #000000;
        color: {cor_fonte};
    }}
    [data-testid="stHeader"] {{
        background-color: #000000;
    }}
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {{
        background-color: {cor_painel};
    }}
    .stApp h1, .stApp h2, .stApp h3,
    .stApp h4, .stApp h5, .stApp h6,
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stCaptionContainer"] p,
    .stApp label {{
        color: {cor_fonte} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌴 Rio Turismo | 2001")
st.write("Dashboard sobre o turismo e a hospedagem no Rio de Janeiro em 2001.")
st.divider()



# Início da manipulação dos dados
def preparar_tabela_468(dados):
    
    
    if dados.shape[0] < 81 or dados.shape[1] < 4:
        raise ValueError("A Tabela 468 nao possui a estrutura esperada.")

    titulo = str(dados.iloc[2, 0])
    if "Tabela 468" not in titulo:
        raise ValueError(
            "Este arquivo nao parece ser a Tabela 468. "
            "Confira se ele foi enviado no campo correto."
        )

    
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    if dados.iloc[69:81, 0].astype(str).str.strip().tolist() != meses:
        raise ValueError(
            "Os meses de 2001 nao estao nas linhas esperadas. "
            "Confira se esta e a planilha original da Tabela 468."
        )

    if str(dados.iloc[67, 0]).strip() != "Média 2001":
        raise ValueError("Nao foi encontrada a media anual de 2001.")

    
    mensal = dados.iloc[69:81, 0:4].copy()

    
    media_anual = dados.iloc[67:68, 0:4].copy()

    colunas = [
        "Período",
        "Diária média (R$)",
        "Gasto médio diário (R$)",
        "Permanência média (dias)"
    ]

    
    for tabela in [mensal, media_anual]:
        tabela.columns = colunas
        tabela["Período"] = tabela["Período"].astype(str).str.strip()

        for coluna in colunas[1:]:
            
            
            tabela[coluna] = pd.to_numeric(tabela[coluna], errors="coerce")

    return mensal.reset_index(drop=True), media_anual.reset_index(drop=True)


def preparar_tabela_1290(dados):
    
    
    titulo = str(dados.iloc[2, 0]) if len(dados) > 2 else ""

    if "Tabela 1290" not in titulo:
        raise ValueError(
            "Este arquivo nao parece ser a Tabela 1290. "
            "Confira se ele foi enviado no campo correto."
        )

    
    
    dados = dados.iloc[9:37, 0:4].copy()

    
    dados.columns = [
        "Tipo e porte do estabelecimento",
        "Total de estabelecimentos",
        "Estabelecimentos em cadeias de hoteis",
        "Percentual em cadeias (%)"
    ]

    
    dados["Tipo e porte do estabelecimento"] = (
        dados["Tipo e porte do estabelecimento"].str.strip()
    )

    
    
    for coluna in dados.columns[1:]:
        dados[coluna] = dados[coluna].replace("-", "0")
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    return dados.reset_index(drop=True)


def preparar_tabela_1289(dados):
    
    if dados.shape[0] < 13 or dados.shape[1] < 10:
        raise ValueError("A Tabela 1289 nao possui a estrutura esperada.")

    titulo = str(dados.iloc[2, 0])
    if "Tabela 1289" not in titulo:
        raise ValueError(
            "Este arquivo nao parece ser a Tabela 1289. "
            "Confira se ele foi enviado no campo correto."
        )

    
    dados = dados.iloc[8:13, 0:10].copy()

    
    dados.columns = [
        "Tipo de estabelecimento",
        "Total de estabelecimentos",
        "Total de unidades habitacionais",
        "Suítes",
        "Apartamentos",
        "Quartos",
        "Chalés",
        "Acomodações (capacidade de hóspedes)",
        "Média de unidades habitacionais por estabelecimento",
        "Média de acomodações por unidade habitacional"
    ]

    dados["Tipo de estabelecimento"] = (
        dados["Tipo de estabelecimento"].astype(str).str.strip()
    )

    
    
    for coluna in dados.columns[1:]:
        dados[coluna] = dados[coluna].replace("-", "0")
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    return dados.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def ler_arquivo(conteudo, nome_arquivo, linha_cabecalho=1, tabela_1290=False, tabela_468=False, tabela_1289=False):
    arquivo = BytesIO(conteudo)
    nome = nome_arquivo.lower()

    
    
    if tabela_1290 or tabela_468 or tabela_1289:
        cabecalho = None
    else:
        cabecalho = linha_cabecalho - 1

    if nome.endswith(".xls"):
        dados = pd.read_excel(arquivo, engine="xlrd", header=cabecalho)
    elif nome.endswith(".xlsx"):
        dados = pd.read_excel(arquivo, engine="openpyxl", header=cabecalho)
    elif nome.endswith(".csv"):
        
        
        if tabela_1290 or tabela_468 or tabela_1289:
            
            
            import csv
            arquivo.seek(0)
            amostra = arquivo.read(8192).decode("utf-8-sig", errors="replace")
            linhas = amostra.splitlines()
            try:
                separador = csv.Sniffer().sniff(
                    linhas[9], delimiters=",;\t"
                ).delimiter
            except (csv.Error, IndexError):
                separador = ";"
            arquivo.seek(0)
        else:
            separador = None

        try:
            dados = pd.read_csv(
                arquivo, sep=separador, engine="python",
                encoding="utf-8-sig", header=None if (tabela_1290 or tabela_468 or tabela_1289) else 0,
                skiprows=0 if (tabela_1290 or tabela_468 or tabela_1289) else linha_cabecalho - 1
            )
        except UnicodeDecodeError:
            arquivo.seek(0)
            dados = pd.read_csv(
                arquivo, sep=separador, engine="python",
                encoding="latin-1", header=None if (tabela_1290 or tabela_468 or tabela_1289) else 0,
                skiprows=0 if (tabela_1290 or tabela_468 or tabela_1289) else linha_cabecalho - 1
            )
    else:
        raise ValueError("Formato nao aceito. Envie XLS, XLSX ou CSV.")

    if tabela_1290:
        return preparar_tabela_1290(dados)

    if tabela_468:
        return preparar_tabela_468(dados)

    if tabela_1289:
        return preparar_tabela_1289(dados)

    
    dados = dados.dropna(how="all")
    dados = dados.dropna(axis=1, how="all")
    dados.columns = [str(coluna).strip() for coluna in dados.columns]
    return dados.reset_index(drop=True)


def gerar_csv(dados):
    dados_exportar = dados.copy()

    for coluna in dados_exportar.columns:
        for indice, valor in dados_exportar[coluna].items():
            if isinstance(valor, str) and valor.lstrip().startswith(("=", "+", "-", "@")):
                dados_exportar.at[indice, coluna] = "'" + valor

    return dados_exportar.to_csv(index=False, sep=";").encode("utf-8-sig")


def gerar_xls(dados):
    import xlwt

    if len(dados) > 65535 or len(dados.columns) > 256:
        raise ValueError("O formato XLS aceita ate 65.535 registros e 256 colunas.")

    arquivo_excel = BytesIO()
    livro = xlwt.Workbook(encoding="utf-8")
    planilha = livro.add_sheet("Dados filtrados")
    estilo_cabecalho = xlwt.easyxf("font: bold on")
    estilo_data = xlwt.easyxf(num_format_str="DD/MM/YYYY")

    for coluna, nome in enumerate(dados.columns):
        planilha.write(0, coluna, str(nome), estilo_cabecalho)

    for linha, valores in enumerate(dados.itertuples(index=False, name=None), start=1):
        for coluna, valor in enumerate(valores):
            if pd.isna(valor):
                continue

            if isinstance(valor, (datetime, date)):
                planilha.write(linha, coluna, valor, estilo_data)
            elif isinstance(valor, (Number, bool)):
                if hasattr(valor, "item"):
                    valor = valor.item()
                planilha.write(linha, coluna, valor)
            else:
                planilha.write(linha, coluna, str(valor))

    livro.save(arquivo_excel)
    return arquivo_excel.getvalue()


# Fim da manipulação dos dados

# Questão 12 - Métricas básicas

def formatar_numero(valor, casas=2):
    if pd.isna(valor):
        return "—"
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def mostrar_metricas(dados, codigo):
    st.subheader("📌 Métricas básicas")
    st.caption("Resumo dos registros que passaram pelos filtros e pela busca.")

    if dados.empty:
        st.metric("Registros", 0)
        st.info("Não há dados para calcular médias e somas.")
        return

    # A linha Rio de Janeiro é o total das outras categorias.
    dados_calculo = dados.copy()
    if codigo == "1289":
        dados_calculo = dados_calculo[
            dados_calculo["Tipo de estabelecimento"] != "Rio de Janeiro"
        ]
        st.caption("O total geral foi excluído dos cálculos para não contar duas vezes.")

    colunas_numericas = dados_calculo.select_dtypes(include="number").columns.tolist()
    if not colunas_numericas:
        st.metric("Registros", len(dados))
        st.info("Não há colunas numéricas para calcular as métricas.")
        return

    # O usuário pode escolher o indicador que deseja analisar.
    coluna = st.selectbox(
        "Escolha o indicador das métricas",
        colunas_numericas,
        key="indicador_metrica_" + codigo
    )

    valores = pd.to_numeric(dados_calculo[coluna], errors="coerce")
    valores = valores.replace([float("inf"), float("-inf")], float("nan"))
    valores_validos = valores.dropna()
    media = valores_validos.mean() if not valores_validos.empty else float("nan")

    # Médias e percentuais não são quantidades que podem ser somadas.
    if codigo == "468":
        pode_somar = False
    elif codigo == "1289":
        pode_somar = coluna in [
            "Total de estabelecimentos", "Total de unidades habitacionais",
            "Suítes", "Apartamentos", "Quartos", "Chalés",
            "Acomodações (capacidade de hóspedes)"
        ]
    else:
        pode_somar = coluna in [
            "Total de estabelecimentos", "Estabelecimentos em cadeias de hoteis"
        ]

    total = None
    rotulo_total = "Soma do indicador"

    if pode_somar and codigo == "1289":
        # As quatro categorias são somadas, sem incluir o total geral.
        total = valores_validos.sum() if not valores_validos.empty else float("nan")
    elif pode_somar and codigo == "1290":
        # Esta tabela mistura tipos, portes e subtotais.
        # Consultamos uma linha de cada vez para não duplicar quantidades.
        indice = st.selectbox(
            "Escolha o tipo ou porte para consultar o total",
            dados_calculo.index.tolist(),
            format_func=lambda i: str(dados_calculo.loc[i, dados_calculo.columns[0]]),
            key="linha_metrica_" + codigo
        )
        total = valores.loc[indice]
        rotulo_total = "Total do tipo ou porte"
        st.caption("O total corresponde à linha escolhida, sem somar tipos e subtotais.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Registros exibidos", len(dados))
    with c2:
        st.metric("Média do indicador", formatar_numero(media))
    with c3:
        if total is not None:
            st.metric(rotulo_total, formatar_numero(total, 0))
        else:
            st.metric("Valores disponíveis", len(valores_validos))

    if codigo == "468":
        st.caption("A média é a média simples dos meses selecionados, não a média "
                   "anual publicada. Somar médias mensais não representa um total anual.")
    elif codigo == "1290":
        st.caption("A média é simples e considera as linhas exibidas. Como esta "
                   "tabela contém tipos, portes e subtotais, ela não representa "
                   "uma média ponderada do município.")
    else:
        st.caption("A média é simples e considera as categorias selecionadas.")

    if not pode_somar:
        st.caption("Este indicador é uma média ou percentual e não deve ser somado.")


# Questão 10 - Gráficos simples

def mostrar_graficos(dados, codigo):
    st.subheader("📊 Gráficos simples")
    st.caption("Os gráficos acompanham os filtros e a busca da tabela.")

    if dados.empty:
        st.info("Não há dados para mostrar nos gráficos.")
        return

    # A primeira coluna identifica os meses ou os tipos de estabelecimento.
    categoria = dados.columns[0]
    colunas_numericas = dados.select_dtypes(include="number").columns.tolist()

    if not colunas_numericas:
        st.info("Não há colunas numéricas para criar gráficos.")
        return

    tipo = st.selectbox(
        "Escolha o tipo de gráfico",
        ["Barras", "Linhas", "Pizza"],
        key="tipo_grafico_" + codigo
    )

    if tipo == "Barras" or tipo == "Linhas":
        coluna = st.selectbox(
            "Escolha o indicador",
            colunas_numericas,
            key="indicador_grafico_" + codigo
        )

        # A Tabela 1289 já possui uma linha com o total geral.
        # Ela não deve ser mostrada junto das categorias.
        dados_grafico = dados.copy()
        if codigo == "1289":
            dados_grafico = dados_grafico[
                dados_grafico["Tipo de estabelecimento"] != "Rio de Janeiro"
            ]
            st.caption("O total geral do Rio de Janeiro foi retirado do gráfico.")

        tabela = dados_grafico[[categoria, coluna]].dropna()

        if tabela.empty:
            st.info("Não há valores disponíveis para este indicador.")
        elif tipo == "Barras":
            st.bar_chart(tabela.set_index(categoria))
        else:
            st.line_chart(tabela.set_index(categoria))

    else:
        # Cada base possui uma forma de distribuição que faz sentido.
        if codigo == "468":
            # Médias não devem ser somadas para formar uma pizza.
            coluna = st.selectbox(
                "Escolha o indicador",
                colunas_numericas,
                key="indicador_pizza_" + codigo
            )
            valores = [
                int(dados[coluna].notna().sum()),
                int(dados[coluna].isna().sum())
            ]
            etiquetas = ["Meses com valor", "Meses sem valor"]
            titulo = "Disponibilidade dos dados: " + coluna
            st.caption("A pizza mostra a quantidade de meses com e sem informação, "
                       "sem somar médias.")

        elif codigo == "1289":
            # Usamos apenas quantidades, nunca as colunas de médias.
            colunas_pizza = [
                "Total de estabelecimentos",
                "Total de unidades habitacionais",
                "Suítes", "Apartamentos", "Quartos", "Chalés",
                "Acomodações (capacidade de hóspedes)"
            ]
            coluna = st.selectbox(
                "Escolha o indicador",
                colunas_pizza,
                key="indicador_pizza_" + codigo
            )
            tabela = dados[
                dados["Tipo de estabelecimento"] != "Rio de Janeiro"
            ][[categoria, coluna]].dropna()
            tabela = tabela[tabela[coluna] > 0]
            valores = tabela[coluna].tolist()
            etiquetas = tabela[categoria].tolist()
            titulo = coluna + " por tipo de estabelecimento"
            st.caption("O total geral foi retirado para não contar os "
                       "estabelecimentos duas vezes.")

        else:
            # Na Tabela 1290, comparamos cadeias e não cadeias
            # dentro de um único tipo ou porte, sem somar subtotais.
            indice = st.selectbox(
                "Escolha o tipo ou porte",
                dados.index.tolist(),
                format_func=lambda i: str(dados.loc[i, categoria]),
                key="linha_pizza_" + codigo
            )
            linha = dados.loc[indice]
            total = linha["Total de estabelecimentos"]
            cadeias = linha["Estabelecimentos em cadeias de hoteis"]

            if (pd.notna(total) and pd.notna(cadeias)
                    and total > 0 and 0 <= cadeias <= total):
                valores = [cadeias, total - cadeias]
                etiquetas = ["Em cadeias", "Fora de cadeias"]
            else:
                valores = []
                etiquetas = []

            titulo = "Estabelecimentos em cadeias: " + str(linha[categoria])
            st.caption("A pizza compara apenas o tipo ou porte escolhido, "
                       "sem somar totais e subtotais.")

        # Retira as fatias com valor zero.
        partes = [(etiqueta, valor) for etiqueta, valor in zip(etiquetas, valores)
                  if valor > 0]

        if partes:
            etiquetas, valores = zip(*partes)
            fig, ax = plt.subplots()
            ax.pie(valores, labels=etiquetas, autopct="%1.1f%%")
            ax.set_title(titulo)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("Não há valores positivos disponíveis para esta pizza.")



# Questão 11 - Gráficos avançados

def mostrar_graficos_avancados(dados, codigo):
    st.subheader("📈 Gráficos avançados")
    st.caption("Os gráficos usam os registros que passaram pelos filtros e pela busca.")

    if dados.empty:
        st.info("Não há dados para mostrar nos gráficos.")
        return

    # Na Tabela 1289, o total geral não é uma categoria adicional.
    dados_grafico = dados.copy()
    if codigo == "1289":
        dados_grafico = dados_grafico[
            dados_grafico["Tipo de estabelecimento"] != "Rio de Janeiro"
        ]
        st.caption("O total geral do Rio de Janeiro foi retirado dos gráficos.")

    colunas_numericas = dados_grafico.select_dtypes(include="number").columns.tolist()

    if not colunas_numericas:
        st.info("Não há colunas numéricas para criar gráficos.")
        return

    tipo = st.selectbox(
        "Escolha o gráfico avançado",
        ["Histograma", "Dispersão (scatter plot)"],
        key="tipo_avancado_" + codigo
    )

    if tipo == "Histograma":
        coluna = st.selectbox(
            "Escolha o indicador do histograma",
            colunas_numericas,
            key="histograma_coluna_" + codigo
        )

        # O histograma conta quantos registros aparecem em cada faixa.
        valores = pd.to_numeric(dados_grafico[coluna], errors="coerce")
        valores = valores.replace([float("inf"), float("-inf")], float("nan")).dropna()

        if valores.empty:
            st.info("Não há valores numéricos disponíveis para este indicador.")
        else:
            faixas = st.slider(
                "Número de faixas",
                min_value=1, max_value=15, value=5,
                key="histograma_faixas_" + codigo
            )
            fig, ax = plt.subplots()
            ax.hist(valores, bins=faixas, edgecolor="black")
            ax.set_title("Distribuição de " + coluna)
            ax.set_xlabel(coluna)
            ax.set_ylabel("Quantidade de registros")
            st.pyplot(fig)
            plt.close(fig)
            st.caption("Cada barra mostra quantos registros possuem valores naquela faixa. "
                       "O gráfico não soma os valores do indicador.")

    else:
        if len(colunas_numericas) < 2:
            st.info("São necessárias pelo menos duas colunas numéricas para a dispersão.")
            return

        coluna_x = st.selectbox(
            "Escolha o indicador do eixo X",
            colunas_numericas,
            key="dispersao_x_" + codigo
        )
        opcoes_y = [coluna for coluna in colunas_numericas if coluna != coluna_x]
        # Na Tabela 468, a permanência é uma boa comparação inicial
        # com a diária média, pois o gasto médio está ausente em 2001.
        coluna_padrao = "Permanência média (dias)"
        if codigo == "468" and coluna_padrao in opcoes_y:
            indice_padrao = opcoes_y.index(coluna_padrao)
        else:
            indice_padrao = 0

        coluna_y = st.selectbox(
            "Escolha o indicador do eixo Y",
            opcoes_y,
            index=indice_padrao,
            key="dispersao_y_" + codigo
        )

        # Mantém apenas as linhas com os dois valores disponíveis.
        tabela = dados_grafico[[coluna_x, coluna_y]].copy()
        for coluna in [coluna_x, coluna_y]:
            tabela[coluna] = pd.to_numeric(tabela[coluna], errors="coerce")
        tabela = tabela.replace([float("inf"), float("-inf")], float("nan")).dropna()

        if tabela.empty:
            st.info("Não há registros com valores disponíveis nos dois indicadores.")
        else:
            fig, ax = plt.subplots()
            ax.scatter(tabela[coluna_x], tabela[coluna_y])
            ax.set_title("Relação entre os indicadores")
            ax.set_xlabel(coluna_x)
            ax.set_ylabel(coluna_y)
            st.pyplot(fig)
            plt.close(fig)
            st.caption("Cada ponto representa uma linha da tabela. "
                       "O gráfico ajuda a observar possíveis relações entre os indicadores.")

            if codigo == "1290":
                st.caption("A Tabela 1290 contém totais e subtotais. "
                           "Cada ponto representa uma categoria, não um estabelecimento individual.")


def mostrar_previa(arquivo, codigo, nome_base, tabela_1290=False, tabela_468=False, tabela_1289=False):
    anterior = st.session_state["dados_carregados"].get(codigo)

    if arquivo is None and anterior is None:
        return None

    if tabela_468:
        st.caption(
            "Tabela 468: cabeçalhos corrigidos e somente os 12 meses "
            "de 2001. A média anual será mostrada separadamente."
        )
        linha_cabecalho = 1
    elif tabela_1289:
        st.caption(
            "Tabela 1289: cabeçalhos corrigidos e cinco registros de 2001, "
            "incluindo o total geral."
        )
        linha_cabecalho = 1
    elif tabela_1290:
        st.caption(
            "Tabela 1290: cabeçalhos corrigidos, linhas 10 a 37 "
            "e quatro colunas de dados."
        )
        linha_cabecalho = 1
    else:
        with st.expander("Ajustar leitura da planilha"):
            linha_cabecalho = st.number_input(
                "Linha que contém os nomes das colunas no Excel",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                key="cabecalho_" + codigo
            )

    if arquivo is not None:
        conteudo = arquivo.getvalue()
        precisa_ler = (
            anterior is None
            or anterior["conteudo"] != conteudo
            or anterior["nome"] != arquivo.name
            or anterior["cabecalho"] != linha_cabecalho
        )

        if precisa_ler:
            barra = st.progress(0, text="Preparando o carregamento...")
            try:
                with st.spinner("Processando a planilha..."):
                    barra.progress(25, text="Lendo o arquivo...")
                    resultado = ler_arquivo(
                        conteudo, arquivo.name, linha_cabecalho,
                        tabela_1290, tabela_468, tabela_1289
                    )
                    barra.progress(70, text="Organizando os dados...")

                    if tabela_468:
                        dados, media_anual = resultado
                    else:
                        dados = resultado
                        media_anual = None

                    st.session_state["dados_carregados"][codigo] = {
                        "nome": arquivo.name,
                        "conteudo": conteudo,
                        "cabecalho": linha_cabecalho,
                        "dados": dados,
                        "media_anual": media_anual
                    }
                    barra.progress(90, text="Exibindo os dados...")
                    st.success(f"Arquivo de {nome_base} carregado com sucesso!")
                    barra.progress(100, text="Carregamento concluído!")
            except Exception as erro:
                st.error(f"Não foi possível ler o arquivo: {erro}")
            finally:
                barra.empty()

    salvo = st.session_state["dados_carregados"].get(codigo)
    if salvo is None:
        return None

    dados = salvo["dados"]
    st.caption("Arquivo na sessão: " + salvo["nome"])
    st.write(f"Registros: {dados.shape[0]} | Colunas: {dados.shape[1]}")
    st.dataframe(dados.head(5), width="stretch", hide_index=True)

    if tabela_1289:
        st.caption(
            "A linha Rio de Janeiro representa o total geral e não deve "
            "ser somada novamente às quatro categorias. Acomodações "
            "representam a capacidade de hóspedes. O traço (-) representa zero."
        )

    if tabela_468 and salvo["media_anual"] is not None:
        st.write("Média anual de 2001 publicada na planilha:")
        st.dataframe(salvo["media_anual"], width="stretch", hide_index=True)
        st.caption(
            "O gasto médio diário está sem valores numéricos em 2001. "
            "Ele foi mantido como ausente, e não como gasto zero. "
            "Os dados se referem somente aos hotéis associados à ABIH/RJ."
        )

    st.button(
        "Remover este arquivo da sessão",
        key="remover_" + codigo,
        on_click=remover_arquivo,
        args=(codigo,)
    )
    return dados


st.header("📂 Carregamento dos dados")
st.write("Envie os arquivos oficiais do Data.Rio nos campos correspondentes.")
st.caption("Formatos aceitos: XLS, XLSX e CSV. Cada base será carregada separadamente.")
st.caption("Os arquivos carregados e as preferências são mantidos durante esta sessão.")

with st.container(border=True):
    st.subheader("1. Diária, gasto e permanência dos visitantes")
    st.write("Diária média, gasto médio e permanência média por dia do visitante hospedado em hotéis do Rio de Janeiro, 1997-2002.")
    st.markdown("[Abrir dataset no Data.Rio](https://www.data.rio/documents/04d5bb74aa254d0bae11206e3c7771aa/about)")
    arquivo_visitantes = st.file_uploader(
        "Selecione a planilha de diária, gasto e permanência",
        type=["xls", "xlsx", "csv"],
        key="upload_468_" + str(st.session_state["versoes_upload"]["468"])
    )
    df_visitantes = mostrar_previa(arquivo_visitantes, "468", "visitantes", tabela_468=True)

with st.container(border=True):
    st.subheader("2. Estabelecimentos e unidades habitacionais")
    st.write("Número de estabelecimentos de hospedagem por tipo de unidades habitacionais, segundo o tipo de estabelecimento, em 2001.")
    st.markdown("[Abrir dataset no Data.Rio](https://www.data.rio/documents/0cf08d856cd746729c2f862d0a2047cf/about)")
    arquivo_unidades = st.file_uploader(
        "Selecione a planilha de estabelecimentos e unidades habitacionais",
        type=["xls", "xlsx", "csv"],
        key="upload_1289_" + str(st.session_state["versoes_upload"]["1289"])
    )
    df_unidades = mostrar_previa(
        arquivo_unidades, "1289", "unidades habitacionais", tabela_1289=True
    )

with st.container(border=True):
    st.subheader("3. Estabelecimentos por tipo e porte")
    st.write("Número de estabelecimentos de hospedagem, total e pertencentes a cadeias de hotéis, segundo tipo e porte, em 2001.")
    st.markdown("[Abrir dataset no Data.Rio](https://www.data.rio/documents/7eb4db425ff34b73aaa3ef4e1eed0f24/about)")
    arquivo_estabelecimentos = st.file_uploader(
        "Selecione a planilha de estabelecimentos por tipo e porte",
        type=["xls", "xlsx", "csv"],
        key="upload_1290_" + str(st.session_state["versoes_upload"]["1290"])
    )
    df_estabelecimentos = mostrar_previa(
        arquivo_estabelecimentos, "1290", "estabelecimentos", tabela_1290=True
    )

st.divider()
st.header("🔎 Consulta dos dados")

bases = {}
codigos = {}

if df_visitantes is not None:
    bases["Diária, gasto e permanência"] = df_visitantes
    codigos["Diária, gasto e permanência"] = "468"

if df_unidades is not None:
    bases["Unidades habitacionais"] = df_unidades
    codigos["Unidades habitacionais"] = "1289"

if df_estabelecimentos is not None:
    bases["Estabelecimentos por tipo e porte"] = df_estabelecimentos
    codigos["Estabelecimentos por tipo e porte"] = "1290"

if not bases:
    st.info("Envie pelo menos uma planilha para iniciar a análise.")
else:
    st.sidebar.header("Filtros")
    opcoes_bases = list(bases.keys())

    if st.session_state["base_preferida"] not in opcoes_bases:
        st.session_state["base_preferida"] = opcoes_bases[0]

    if (
        "base_selecionada" not in st.session_state
        or st.session_state["base_selecionada"] not in opcoes_bases
    ):
        st.session_state["base_selecionada"] = st.session_state["base_preferida"]

    nome_base = st.sidebar.radio(
        "Escolha a base de dados",
        opcoes_bases,
        key="base_selecionada",
        on_change=guardar_base
    )
    codigo = codigos[nome_base]
    preferencias = st.session_state["preferencias"].setdefault(codigo, {})
    dados = bases[nome_base].copy()

    if codigo == "468":
        st.sidebar.caption("Recorte: janeiro a dezembro de 2001.")

    chave = "completos_" + codigo
    if chave not in st.session_state:
        st.session_state[chave] = preferencias.get("completos", False)

    somente_completos = st.sidebar.checkbox(
        "Mostrar apenas linhas completas",
        key=chave,
        on_change=guardar_preferencia,
        args=(codigo, "completos", chave)
    )

    if somente_completos:
        dados = dados.dropna()
        if codigo == "468":
            st.sidebar.caption(
                "O gasto médio não possui valores em 2001. "
                "Por isso, exigir todas as colunas completas pode deixar a tabela vazia."
            )

    st.sidebar.subheader("Filtrar registros")
    opcoes_colunas = ["Nenhuma"] + dados.columns.tolist()
    chave = "coluna_" + codigo

    if chave not in st.session_state:
        st.session_state[chave] = preferencias.get("coluna", "Nenhuma")
    if st.session_state[chave] not in opcoes_colunas:
        st.session_state[chave] = "Nenhuma"

    coluna_filtro = st.sidebar.selectbox(
        "Escolha uma coluna para filtrar",
        opcoes_colunas,
        key=chave,
        on_change=guardar_coluna_filtro,
        args=(codigo, chave)
    )

    if coluna_filtro != "Nenhuma":
        valores = dados[coluna_filtro].dropna().unique().tolist()
        valores = sorted(valores, key=str)
        opcoes_valores = ["Todos"] + valores
        chave = "valor_" + codigo

        if chave not in st.session_state:
            st.session_state[chave] = preferencias.get("valor", "Todos")
        if st.session_state[chave] not in opcoes_valores:
            st.session_state[chave] = "Todos"

        valor_filtro = st.sidebar.selectbox(
            "Escolha o valor",
            opcoes_valores,
            key=chave,
            format_func=str,
            on_change=guardar_preferencia,
            args=(codigo, "valor", chave)
        )

        if valor_filtro != "Todos":
            dados = dados[dados[coluna_filtro] == valor_filtro]

    st.sidebar.button(
        "Limpar filtros desta base",
        key="limpar_" + codigo,
        on_click=limpar_filtros,
        args=(codigo,)
    )

    st.subheader(nome_base)
    opcoes = dados.columns.tolist()
    chave = "colunas_" + codigo

    if chave not in st.session_state:
        escolhas = preferencias.get("colunas", opcoes)
        escolhas_validas = [coluna for coluna in escolhas if coluna in opcoes]
        if escolhas and not escolhas_validas:
            escolhas_validas = opcoes.copy()
        st.session_state[chave] = escolhas_validas
    else:
        st.session_state[chave] = [
            coluna for coluna in st.session_state[chave] if coluna in opcoes
        ]

    colunas_escolhidas = st.multiselect(
        "Selecione as colunas que deseja visualizar",
        opcoes,
        key=chave,
        on_change=guardar_preferencia,
        args=(codigo, "colunas", chave)
    )

    if not colunas_escolhidas:
        st.warning("Selecione pelo menos uma coluna para visualizar os dados.")
    else:
        dados_filtrados = dados[colunas_escolhidas].copy()
        chave = "busca_" + codigo

        if chave not in st.session_state:
            st.session_state[chave] = preferencias.get("busca", "")

        busca = st.text_input(
            "Buscar na tabela",
            placeholder="Digite um nome, categoria, número ou outro valor",
            key=chave,
            on_change=guardar_preferencia,
            args=(codigo, "busca", chave)
        )

        if busca.strip():
            linhas_encontradas = pd.Series(False, index=dados_filtrados.index)

            for coluna in dados_filtrados.columns:
                encontrou = dados_filtrados[coluna].astype(str).str.contains(
                    busca.strip(), case=False, regex=False, na=False
                )
                linhas_encontradas = linhas_encontradas | encontrou

            dados_filtrados = dados_filtrados[linhas_encontradas]

        mostrar_metricas(dados.loc[dados_filtrados.index].copy(), codigo)
        st.caption(
            "Clique no cabeçalho para ordenar. Use a barra de ferramentas "
            "da tabela para pesquisar, copiar ou ajustar as colunas."
        )

        if dados_filtrados.empty:
            st.info("Nenhum registro corresponde aos filtros selecionados.")
        else:
            st.dataframe(
                dados_filtrados,
                width="stretch",
                hide_index=True,
                height=400
            )

            mostrar_graficos(dados.loc[dados_filtrados.index].copy(), codigo)
            mostrar_graficos_avancados(dados.loc[dados_filtrados.index].copy(), codigo)

            st.subheader("📥 Download dos dados filtrados")
            st.caption("Os arquivos incluem apenas as linhas e colunas exibidas acima.")

            coluna_csv, coluna_xls = st.columns(2)

            with coluna_csv:
                st.download_button(
                    "Baixar CSV",
                    data=gerar_csv(dados_filtrados),
                    file_name="rio_turismo_2001.csv",
                    mime="text/csv",
                    key="download_csv",
                    use_container_width=True
                )

            with coluna_xls:
                try:
                    arquivo_xls = gerar_xls(dados_filtrados)
                    st.download_button(
                        "Baixar XLS",
                        data=arquivo_xls,
                        file_name="rio_turismo_2001.xls",
                        mime="application/vnd.ms-excel",
                        key="download_xls",
                        use_container_width=True
                    )
                except ModuleNotFoundError as erro:
                    if erro.name == "xlwt":
                        st.info(
                            "Para baixar XLS, instale xlwt no terminal: "
                            "python -m pip install xlwt. "
                            "O carregamento e a exportação CSV continuam disponíveis."
                        )
                    else:
                        st.error(f"Não foi possível preparar o XLS: {erro}")
                except Exception as erro:
                    st.error(f"Não foi possível preparar o XLS: {erro}")

st.caption("Fonte: Data.Rio | Recorte do projeto: 2001")
