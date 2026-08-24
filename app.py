import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

from plotly.subplots import make_subplots


arq1 = "HIST_PAINEL_COVIDBR_2025_Parte1_05set2025.csv"
arq2 = "HIST_PAINEL_COVIDBR_2025_Parte2_05set2025.csv"

dados1 = pd.read_csv(
    arq1,
    sep=";",
    encoding="latin1"
)

dados2 = pd.read_csv(
    arq2,
    sep=";",
    encoding="latin1"
)

dados = pd.concat(
    [dados1, dados2],
    ignore_index=True
)


st.title("Análise dos Dados da COVID-19 no Brasil")

st.subheader("Questão 1 - Importância da Visualização de Dados")

st.write(
    "A visualização de dados é importante em uma pandemia porque "
    "permite transformar uma grande quantidade de informações em "
    "gráficos e mapas que podem ser entendidos mais facilmente. "
    "Com isso, fica mais simples perceber mudanças na quantidade "
    "de casos, óbitos e a evolução da doença ao longo do tempo."
)

st.write(
    "Para os gestores de saúde, essas informações ajudam a "
    "acompanhar a situação de cada região e a planejar recursos "
    "e medidas de prevenção. Para a população, os gráficos "
    "facilitam o acompanhamento da pandemia e ajudam a entender "
    "como a situação estava mudando."
)


st.subheader("Questão 2 - Gráfico de Barras com Streamlit")

dados_sp = dados[
    (dados["estado"] == "SP") &
    (dados["municipio"].isna())
].copy()

dados_sp["semanaEpi"] = pd.to_numeric(
    dados_sp["semanaEpi"],
    errors="coerce"
)

dados_sp["casosNovos"] = pd.to_numeric(
    dados_sp["casosNovos"],
    errors="coerce"
)

casos_sp = dados_sp.groupby(
    "semanaEpi"
)["casosNovos"].sum().reset_index()

casos_sp = casos_sp.sort_values(
    "semanaEpi"
)

st.bar_chart(
    casos_sp.set_index("semanaEpi")[
        "casosNovos"
    ]
)

st.write(
    "O estado escolhido foi São Paulo porque ele possui uma "
    "população muito grande e registrou uma quantidade elevada "
    "de casos durante a pandemia. No gráfico é possível perceber "
    "que os casos não se mantiveram constantes. Em algumas semanas "
    "houve picos maiores, enquanto em outras a quantidade de "
    "novos casos foi menor."
)


st.subheader("Questão 3 - Gráfico de Linha com Streamlit")

dados_est = dados[
    (dados["estado"].notna()) &
    (dados["codmun"].isna())
].copy()

dados_est["semanaEpi"] = pd.to_numeric(
    dados_est["semanaEpi"],
    errors="coerce"
)

dados_est["obitosAcumulado"] = pd.to_numeric(
    dados_est["obitosAcumulado"],
    errors="coerce"
)

dados_obt = dados_est.groupby(
    [
        "semanaEpi",
        "estado"
    ]
)["obitosAcumulado"].max().reset_index()

obt_br = dados_obt.groupby(
    "semanaEpi"
)["obitosAcumulado"].sum().reset_index()

obt_br = obt_br.sort_values(
    "semanaEpi"
)

st.line_chart(
    obt_br.set_index("semanaEpi")[
        "obitosAcumulado"
    ]
)

st.write(
    "A linha mostra a evolução do número acumulado de óbitos "
    "por COVID-19 no Brasil. Como esse valor vai sendo somado "
    "com o passar das semanas, a tendência é de crescimento. "
    "Quando a linha sobe mais rapidamente, significa que houve "
    "um aumento maior dos óbitos naquele período. Já os trechos "
    "mais próximos de uma linha reta indicam um crescimento menor."
)


st.subheader("Questão 4 - Gráficos de Área com Streamlit")

dados_est = dados[
    (dados["estado"].isin([
        "SP",
        "MG",
        "RJ"
    ])) &
    (dados["municipio"].isna())
].copy()

dados_est["semanaEpi"] = pd.to_numeric(
    dados_est["semanaEpi"],
    errors="coerce"
)

dados_est["casosAcumulado"] = pd.to_numeric(
    dados_est["casosAcumulado"],
    errors="coerce"
)

casos_est = dados_est.groupby(
    [
        "semanaEpi",
        "estado"
    ]
)["casosAcumulado"].max().reset_index()

sp = casos_est[
    casos_est["estado"] == "SP"
].set_index("semanaEpi")

mg = casos_est[
    casos_est["estado"] == "MG"
].set_index("semanaEpi")

rj = casos_est[
    casos_est["estado"] == "RJ"
].set_index("semanaEpi")

st.write("São Paulo (SP)")

st.area_chart(
    sp["casosAcumulado"]
)

st.write("Minas Gerais (MG)")

st.area_chart(
    mg["casosAcumulado"]
)

st.write("Rio de Janeiro (RJ)")

st.area_chart(
    rj["casosAcumulado"]
)

st.write(
    "Foram escolhidos São Paulo, Minas Gerais e Rio de Janeiro "
    "porque os três estados fazem parte da mesma região e tiveram "
    "uma grande participação nos casos do país. São Paulo apresenta "
    "um número acumulado maior, o que pode ser explicado em parte "
    "pelo tamanho da sua população. Minas Gerais e Rio de Janeiro "
    "também apresentam crescimento ao longo do período, mas em "
    "níveis diferentes."
)


st.subheader("Questão 5 - Mapa com Streamlit")

dados_est = dados[
    (dados["estado"].notna()) &
    (dados["municipio"].isna())
].copy()

dados_est["data"] = pd.to_datetime(
    dados_est["data"],
    errors="coerce"
)

dados_est["casosAcumulado"] = pd.to_numeric(
    dados_est["casosAcumulado"],
    errors="coerce"
)

ult_data = dados_est["data"].max()

dados_ult = dados_est[
    dados_est["data"] == ult_data
].copy()

top5 = dados_ult.sort_values(
    "casosAcumulado",
    ascending=False
).head(5).copy()

coord = {
    "SP": [-23.55052, -46.63331],
    "MG": [-19.91668, -43.93449],
    "PR": [-25.42840, -49.27330],
    "RJ": [-22.90685, -43.17290],
    "RS": [-30.03465, -51.21766]
}

top5["latitude"] = top5["estado"].map(
    lambda x: coord[x][0]
)

top5["longitude"] = top5["estado"].map(
    lambda x: coord[x][1]
)

maior = top5["casosAcumulado"].max()

top5["tamanho"] = (
    1000 +
    (
        top5["casosAcumulado"] / maior
    ) * 49000
)

mapa = top5[
    [
        "estado",
        "latitude",
        "longitude",
        "casosAcumulado",
        "tamanho"
    ]
].copy()

st.map(
    mapa,
    latitude="latitude",
    longitude="longitude",
    size="tamanho",
    zoom=4
)

st.dataframe(
    mapa[
        [
            "estado",
            "casosAcumulado"
        ]
    ],
    use_container_width=True
)

st.write(
    "O mapa apresenta os cinco estados que tinham os maiores "
    "valores de casos acumulados na data mais recente disponível. "
    "As posições dos pontos representam as capitais dos estados. "
    "Além da localização, o tamanho do ponto ajuda a comparar "
    "a quantidade de casos de cada estado."
)


st.subheader("Questão 6 - Gráfico de Barras com Matplotlib")

dados_est = dados[
    (dados["estado"].notna()) &
    (dados["codmun"].isna())
].copy()

dados_est["semanaEpi"] = pd.to_numeric(
    dados_est["semanaEpi"],
    errors="coerce"
)

dados_est["casosNovos"] = pd.to_numeric(
    dados_est["casosNovos"],
    errors="coerce"
)

dados_est["obitosNovos"] = pd.to_numeric(
    dados_est["obitosNovos"],
    errors="coerce"
)

dados_est = dados_est.dropna(
    subset=[
        "estado",
        "semanaEpi"
    ]
)

ult_sem = int(
    dados_est["semanaEpi"].max()
)

dados_ult = dados_est[
    dados_est["semanaEpi"] == ult_sem
].copy()

dados_ult = dados_ult.groupby(
    "estado"
)[
    [
        "casosNovos",
        "obitosNovos"
    ]
].sum()

dados_ult = dados_ult.sort_values(
    "casosNovos",
    ascending=False
)

fig, ax = plt.subplots(
    figsize=(14, 7)
)

pos = range(
    len(dados_ult)
)

largura = 0.4

ax.bar(
    [x - largura / 2 for x in pos],
    dados_ult["casosNovos"],
    width=largura,
    label="Casos Novos"
)

ax.bar(
    [x + largura / 2 for x in pos],
    dados_ult["obitosNovos"],
    width=largura,
    label="Óbitos Novos"
)

ax.set_title(
    "Casos Novos e Óbitos Novos por Estado"
)

ax.set_xlabel(
    "Estado"
)

ax.set_ylabel(
    "Quantidade"
)

ax.set_xticks(
    list(pos)
)

ax.set_xticklabels(
    dados_ult.index,
    rotation=45
)

ax.legend()

plt.tight_layout()

st.pyplot(
    fig
)

st.write(
    "Aqui foi feita uma comparação entre casos novos e óbitos "
    "novos na semana epidemiológica mais recente. Os estados "
    "não apresentam os mesmos valores, principalmente porque "
    "existem diferenças no número de casos entre eles. Também "
    "é importante lembrar que um óbito pode acontecer depois "
    "do registro do caso, então os valores não precisam crescer "
    "exatamente ao mesmo tempo."
)

st.write(
    "Semana analisada:",
    ult_sem
)


st.subheader("Questão 7 - Boxplot com Seaborn")

reg = [
    "Norte",
    "Nordeste",
    "Sudeste"
]

dados_reg = dados[
    (dados["regiao"].isin(reg)) &
    (dados["estado"].notna()) &
    (dados["municipio"].isna())
].copy()

dados_reg["semanaEpi"] = pd.to_numeric(
    dados_reg["semanaEpi"],
    errors="coerce"
)

dados_reg["casosNovos"] = pd.to_numeric(
    dados_reg["casosNovos"],
    errors="coerce"
)

dados_box = dados_reg.groupby(
    [
        "regiao",
        "semanaEpi"
    ]
)["casosNovos"].sum().reset_index()

fig, ax = plt.subplots(
    figsize=(10, 6)
)

sns.boxplot(
    data=dados_box,
    x="regiao",
    y="casosNovos",
    ax=ax
)

ax.set_title(
    "Distribuição dos Casos Novos por Região"
)

ax.set_xlabel(
    "Região"
)

ax.set_ylabel(
    "Casos Novos"
)

st.pyplot(
    fig
)

st.write(
    "O boxplot mostra como os casos novos ficaram distribuídos "
    "nas regiões Norte, Nordeste e Sudeste. O Sudeste apresenta "
    "valores maiores em números absolutos. Também dá para perceber "
    "a variação entre as semanas e alguns valores mais afastados "
    "do comportamento central."
)


st.subheader("Questão 8 - Gráfico de Área com Altair")

dados_sud = dados[
    (dados["regiao"] == "Sudeste") &
    (dados["estado"].notna()) &
    (dados["municipio"].isna())
].copy()

dados_sud["semanaEpi"] = pd.to_numeric(
    dados_sud["semanaEpi"],
    errors="coerce"
)

dados_sud["casosNovos"] = pd.to_numeric(
    dados_sud["casosNovos"],
    errors="coerce"
)

casos_sud = dados_sud.groupby(
    "semanaEpi"
)["casosNovos"].sum().reset_index()

casos_sud = casos_sud.sort_values(
    "semanaEpi"
)

graf = alt.Chart(
    casos_sud
).mark_area().encode(
    x=alt.X(
        "semanaEpi:Q",
        title="Semana Epidemiológica"
    ),
    y=alt.Y(
        "casosNovos:Q",
        title="Casos Novos"
    ),
    tooltip=[
        "semanaEpi",
        "casosNovos"
    ]
).properties(
    title="Casos Novos de COVID-19 - Região Sudeste"
)

st.altair_chart(
    graf,
    use_container_width=True
)

st.write(
    "A região escolhida foi o Sudeste por apresentar uma "
    "quantidade alta de casos e permitir observar bem as "
    "mudanças ao longo do tempo. O gráfico mostra vários "
    "momentos de aumento e redução. Os pontos mais altos "
    "representam as semanas com maior número de casos novos."
)


st.subheader("Questão 9 - Heatmap com Altair")

dados_sp = dados[
    (dados["estado"] == "SP") &
    (dados["municipio"].isna())
].copy()

dados_sp["semanaEpi"] = pd.to_numeric(
    dados_sp["semanaEpi"],
    errors="coerce"
)

dados_sp["casosNovos"] = pd.to_numeric(
    dados_sp["casosNovos"],
    errors="coerce"
)

dados_sp["obitosNovos"] = pd.to_numeric(
    dados_sp["obitosNovos"],
    errors="coerce"
)

dados_sp = dados_sp.groupby(
    "semanaEpi"
)[
    [
        "casosNovos",
        "obitosNovos"
    ]
].sum().reset_index()

corr = dados_sp[
    [
        "casosNovos",
        "obitosNovos"
    ]
].corr()

dados_heat = corr.reset_index().melt(
    id_vars="index"
)

dados_heat.columns = [
    "var1",
    "var2",
    "corr"
]

graf = alt.Chart(
    dados_heat
).mark_rect().encode(
    x=alt.X(
        "var1:N",
        title="Variável"
    ),
    y=alt.Y(
        "var2:N",
        title="Variável"
    ),
    color=alt.Color(
        "corr:Q",
        title="Correlação"
    ),
    tooltip=[
        "var1",
        "var2",
        "corr"
    ]
).properties(
    title="Correlação entre Casos Novos e Óbitos Novos - SP"
)

st.altair_chart(
    graf,
    use_container_width=True
)

st.write(
    "Neste caso, o heatmap compara apenas casos novos e óbitos "
    "novos em São Paulo. A correlação ajuda a verificar se as "
    "duas variáveis costumam variar na mesma direção. Um valor "
    "positivo mostra uma tendência de aumento conjunto, mas isso "
    "não quer dizer que uma variável seja a causa direta da outra."
)


st.subheader("Questão 10 - Gráfico de Pizza com Plotly")

dados_est = dados[
    (dados["estado"].notna()) &
    (dados["codmun"].isna())
].copy()

dados_est["data"] = pd.to_datetime(
    dados_est["data"],
    errors="coerce"
)

dados_est["casosAcumulado"] = pd.to_numeric(
    dados_est["casosAcumulado"],
    errors="coerce"
)

ult_data = dados_est["data"].max()

dados_ult = dados_est[
    dados_est["data"] == ult_data
].copy()

dados_reg = dados_ult.groupby(
    "regiao"
)["casosAcumulado"].sum().reset_index()

graf = px.pie(
    dados_reg,
    names="regiao",
    values="casosAcumulado",
    title="Distribuição dos Casos Acumulados por Região"
)

graf.update_traces(
    textinfo="percent+label"
)

st.plotly_chart(
    graf,
    use_container_width=True
)

st.write(
    "O gráfico mostra como os casos acumulados estão divididos "
    "entre as cinco regiões brasileiras. A região que possui "
    "mais casos fica com a maior parcela da pizza. A população "
    "e a quantidade de casos registrados em cada região ajudam "
    "a explicar essas diferenças."
)


st.subheader("Questão 11 - Subplots com Plotly")

reg = [
    "Sudeste",
    "Nordeste"
]

dados_reg = dados[
    (dados["regiao"].isin(reg)) &
    (dados["estado"].notna()) &
    (dados["municipio"].isna())
].copy()

dados_reg["semanaEpi"] = pd.to_numeric(
    dados_reg["semanaEpi"],
    errors="coerce"
)

dados_reg["casosNovos"] = pd.to_numeric(
    dados_reg["casosNovos"],
    errors="coerce"
)

dados_reg["obitosNovos"] = pd.to_numeric(
    dados_reg["obitosNovos"],
    errors="coerce"
)

dados_reg = dados_reg.groupby(
    [
        "regiao",
        "semanaEpi"
    ]
)[
    [
        "casosNovos",
        "obitosNovos"
    ]
].sum().reset_index()

fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=[
        "Sudeste",
        "Nordeste"
    ]
)

dados_sud = dados_reg[
    dados_reg["regiao"] == "Sudeste"
]

dados_nord = dados_reg[
    dados_reg["regiao"] == "Nordeste"
]

fig.add_trace(
    go.Bar(
        x=dados_sud["semanaEpi"],
        y=dados_sud["casosNovos"],
        name="Casos Novos - Sudeste"
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Bar(
        x=dados_sud["semanaEpi"],
        y=dados_sud["obitosNovos"],
        name="Óbitos Novos - Sudeste"
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Bar(
        x=dados_nord["semanaEpi"],
        y=dados_nord["casosNovos"],
        name="Casos Novos - Nordeste"
    ),
    row=1,
    col=2
)

fig.add_trace(
    go.Bar(
        x=dados_nord["semanaEpi"],
        y=dados_nord["obitosNovos"],
        name="Óbitos Novos - Nordeste"
    ),
    row=1,
    col=2
)

fig.update_layout(
    title="Casos Novos e Óbitos Novos por Semana",
    barmode="group"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.write(
    "Os subplots ajudam a visualizar as duas regiões ao mesmo "
    "tempo. O Sudeste apresenta valores absolutos maiores em "
    "boa parte do período, enquanto o Nordeste também apresenta "
    "seus próprios períodos de crescimento. Assim, fica mais "
    "fácil perceber que a evolução dos casos e óbitos não foi "
    "igual nas duas regiões."
)


st.subheader("Questão 12 - Mapa Interativo com PyDeck")

dados_mg = dados[
    (dados["estado"] == "MG") &
    (dados["municipio"].notna())
].copy()

dados_mg["municipio"] = dados_mg["municipio"].apply(
    lambda x: (
        str(x).encode("latin1").decode("utf-8")
        if "Ã" in str(x)
        else str(x)
    )
)

dados_mg["data"] = pd.to_datetime(
    dados_mg["data"],
    errors="coerce"
)

dados_mg["casosAcumulado"] = pd.to_numeric(
    dados_mg["casosAcumulado"],
    errors="coerce"
)

dados_mg["populacaoTCU2019"] = pd.to_numeric(
    dados_mg["populacaoTCU2019"],
    errors="coerce"
)

mun = [
    "Belo Horizonte",
    "Uberlândia",
    "Contagem",
    "Juiz de Fora",
    "Betim"
]

dados_mg = dados_mg[
    dados_mg["municipio"].isin(mun)
].copy()

dados_mg = dados_mg.sort_values(
    "data"
)

dados_mg = dados_mg.groupby(
    "municipio"
).tail(1)

coord = {
    "Belo Horizonte": [-19.9208, -43.9378],
    "Uberlândia": [-18.9186, -48.2772],
    "Contagem": [-19.9317, -44.0536],
    "Juiz de Fora": [-21.7642, -43.3503],
    "Betim": [-19.9678, -44.1983]
}

dados_mg["latitude"] = dados_mg["municipio"].map(
    lambda x: coord[x][0]
)

dados_mg["longitude"] = dados_mg["municipio"].map(
    lambda x: coord[x][1]
)

dados_mg["casos_100mil"] = (
    dados_mg["casosAcumulado"] /
    dados_mg["populacaoTCU2019"]
) * 100000

dados_mg["raio"] = (
    dados_mg["casos_100mil"].clip(lower=1) ** 0.5
) * 120

camada = pdk.Layer(
    "ScatterplotLayer",
    data=dados_mg,
    get_position=[
        "longitude",
        "latitude"
    ],
    get_radius="raio",
    get_fill_color=[
        200,
        30,
        30,
        160
    ],
    pickable=True
)

visao = pdk.ViewState(
    latitude=-19.5,
    longitude=-44.5,
    zoom=6
)

mapa = pdk.Deck(
    layers=[
        camada
    ],
    initial_view_state=visao,
    tooltip={
        "text":
        "{municipio}\n"
        "Casos acumulados: {casosAcumulado}\n"
        "Casos por 100 mil: {casos_100mil}"
    }
)

st.pydeck_chart(
    mapa
)

st.write(
    "Foram escolhidos cinco municípios de Minas Gerais para "
    "comparar os casos acumulados. Como os municípios possuem "
    "populações diferentes, foi usada também a quantidade de "
    "casos por 100 mil habitantes."
)

st.write(
    "Esse ajuste ajuda na comparação, porque um município grande "
    "pode ter mais casos simplesmente por possuir mais habitantes. "
    "Com os casos por 100 mil, conseguimos observar melhor a "
    "situação em relação ao tamanho de cada município."
)

st.write(
    "A concentração de pessoas pode facilitar a transmissão "
    "de uma doença contagiosa, já que aumenta a possibilidade "
    "de contato entre indivíduos."
)