import streamlit as st
import httpx
from datetime import datetime, timedelta
from pytz import timezone  # Import pytz for time zone handling
import pandas as pd


def main():
  st.title("Justificativa de Faltas")
  # Make API request to get data

  # Create a text input field for searching
  search_term = st.text_input('Busque pelo nome do estudante', value="digite aqui")

  # Filter DataFrame based on search term
  if search_term:
    response = httpx.get(
      'https://freq-willapp.herokuapp.com/allstudents/2023%401124856')
    data = response.json()

    # Create DataFrame from data
    df = pd.DataFrame(data)

    df = df[df['estudante'].str.contains(search_term, case=False)]

    # Create DataFrame with clickable rows
    if not df.empty:
      df = df[['matrícula', 'estudante', 'turma']]
      st.write(df, unsafe_allow_html=True)
      if df.shape[0] < 6:
        dict_nome_matricula = {
          str(index) + ' - ' + row['estudante']: row['matrícula']
          for index, row in df.iterrows()
        }

        # Cria duas colunas com o mesmo tamanho
        col1, col2 = st.columns(2)

        # Adiciona os campos em cada coluna
        with col1:
          option = st.selectbox('Selecione o estudante correto:',
                                tuple(dict_nome_matricula.keys()))
          if option:
            student_id = dict_nome_matricula.get(option)
        with col2:
          secret_key = st.text_input("Chave secreta", type="password")
        usar_data_final = st.checkbox(
          "Deseja definir uma data final específica?")
        col3, col4 = st.columns(2)
        with col3:
          data_inicial = st.date_input(
            "Data Inicial",
            value=datetime.now(tz=timezone('America/Sao_Paulo')))
        with col4:
          if usar_data_final:
            data_final = st.date_input(
              "Data Final",
              value=datetime.now(tz=timezone('America/Sao_Paulo')) +
              timedelta(days=1))
            dias_licenca = (data_final - data_inicial).days + 1
          else:
            dias_licenca = st.number_input("Quantidade de dias justificados",
                                           min_value=1)
            data_final = data_inicial + timedelta(days=dias_licenca - 1)

        tem_certificado = st.checkbox("O estudante tem um atestado médico?")
        ocorrencia_medica = st.text_area("Detalhes da justificativa",
                                         max_chars=200)

        st.subheader(':blue[Conferência]')
        col_nome, col_rm, col_turma = st.columns(3)
        selected_row = df.loc[int(option.split(" - ")[0]), :]
        nome = selected_row['estudante']
        matrícula = selected_row['matrícula']
        turma = selected_row['turma']
        with col_nome:
          st.write(f"Nome: **{nome}**")
        with col_rm:
          st.write(f"matrícula: **{matrícula}**")
        with col_turma:
          st.write(f"turma: **{turma}**")
        colx1, colx2, colx3, colx4 = st.columns(4)
        with colx1:
          st.write(f"Data Inicial: **{data_inicial.strftime('%d/%m/%Y')}**")
        with colx2:
          st.write(f"Data Final: **{data_final.strftime('%d/%m/%Y')}**")
        with colx3:
          st.write(f"Dias de justificativa: **{dias_licenca}**")
        with colx4:
          if tem_certificado:
            st.write("**COM** atestado médico.")
          else:
            st.write("**SEM** atestado médico.")
        # if ocorrencia_medica:
        st.write(f"Detalhes da justificativa: {ocorrencia_medica}")

        # Add a "Enviar" button to submit the form
        if st.button("Enviar"):
          payload = {
            "matrícula": matrícula,
            "data_init": data_inicial.strftime('%d/%m/%Y'),
            "data_end": data_final.strftime('%d/%m/%Y'),
            "num_dias_justificados": dias_licenca,
            "tem_atestado": tem_certificado,
            "justificativa": ocorrencia_medica,
          }
          print(payload)
          try:
            # Use httpx library to make a POST request with the payload data
            response = httpx.post(
              f"https://freq-willapp.herokuapp.com/jus/{secret_key}",
              json=payload)
            if response.status_code == 200:
              st.success("Sua justificativa foi enviada com sucesso!")
              st.subheader('Resposta do Servidor:')
              st.write(response.json())
            else:
              st.error(
                "Houve um erro ao enviar sua justificativa. Tente novamente mais tarde."
              )
              st.subheader('Resposta do Servidor:')
              st.write(response.content)
          except:
            st.error(
              "Houve um erro ao enviar sua justificativa. Tente novamente mais tarde."
            )


if __name__ == "__main__":
  main()
