Rio Turismo 2001

Utilizei três planilhas da seção de turismo do Data.Rio:

Tabela 468 - Diária média, gasto médio e permanência média dos visitantes hospedados em hotéis.
https://www.data.rio/documents/04d5bb74aa254d0bae11206e3c7771aa/about

Tabela 1289 - Número de estabelecimentos de hospedagem por tipo de unidades habitacionais.
https://www.data.rio/documents/0cf08d856cd746729c2f862d0a2047cf/about

Tabela 1290 - Número de estabelecimentos de hospedagem, total e pertencentes à cadeia de hotéis, segundo tipo e porte.
https://www.data.rio/documents/7eb4db425ff34b73aaa3ef4e1eed0f24/about

O projeto foi feito em Python, utilizando Streamlit e pandas, com todo o código em um único arquivo app.py.

Durante o desenvolvimento, utilizei o ChatGPT como apoio para corrigir a leitura das planilhas. Quando carreguei os arquivos, várias colunas apareciam como Unnamed, pois os cabeçalhos estavam em linhas diferentes e havia títulos, células mescladas e notas de rodapé. Enviei os arquivos para a IA e pedi ajuda para identificar os cabeçalhos corretos e organizar os dados utilizando comandos básicos do pandas.

Para executar o projeto no VS Code, coloque o app.py e o requirements.txt na mesma pasta e execute os comandos abaixo no terminal:

pip install -r requirements.txt

streamlit run app.py

Depois, basta abrir a aplicação no navegador e carregar os arquivos XLS nos campos correspondentes.

O projeto ainda está sendo desenvolvido por etapas, conforme as questões propostas pelo professor.
