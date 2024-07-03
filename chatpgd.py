import os
from datetime import datetime
import pygsheets
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv, find_dotenv
import json
import base64
import pytz

# load_dotenv(find_dotenv())
encoded_key = os.getenv("TESTE")
encoded_key = str(encoded_key)
service_key= json.loads(base64.b64decode(encoded_key).decode('ASCII'))
perguntaEnc = os.getenv("PERGUNTA")
perguntaEnc = str(perguntaEnc)
pergunta = base64.b64decode(perguntaEnc).decode('UTF-8')
with open('temp.json', 'w') as file:
    json.dump(service_key, file)

st.set_page_config(page_title="ELO-PGD")
timezone = pytz.timezone('America/Sao_Paulo')  # Exemplo: São Paulo, Brasil

st.markdown("""
<style>
header{visibility: hidden;}
.viewerBadge_link__qRIco{visibility: hidden; width: 0px; height: 0px;}
#MainMenu {visibility: hidden;} 
footer {visibility: hidden;}
.viewerBadge_link__qRIco{visibility: hidden}
.st-emotion-cache-ztfqz8 ef3psqc5{visibility: hidden;}
.st-emotion-cache-ztfqz8 ef3psqc5{visibility: hidden;}
.st-emotion-cache-15ecox0 ezrtsby0{visibility: hidden;}
.st-emotion-cache-q16mip e3g6aar1{visibility: hidden;}
.viewerBadge_container__r5tak styles_viewerBadge__CvC9N{visibility: hidden;}
.st-emotion-cache-h4xjwg ezrtsby2{visibility: hidden;}
.st-emotion-cache-ch5dnh ef3psqc5{visibility: hidden;}
span{visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<img style="float: left;" width=150px src="https://www.ufpe.br/documents/4462600/0/PGD+LOGO.png/2783cf94-3db6-4270-9f2b-ba32901120e8?t=1715183714641" /><h1>Chat-PGD</h1>', unsafe_allow_html=True)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

credential_file = "temp.json"
sheet_title = "testePGD"
worksheet_title = "Página1"
gc = pygsheets.authorize(service_account_file=credential_file)
temp = gc.open(sheet_title)
sheet = temp.worksheet_by_title(worksheet_title)
hora = datetime.now(timezone).strftime("%d/%m/%Y %H:%M:%S")

if "contador" not in st.session_state:
    st.session_state.contador = 0

if "diff" not in st.session_state:
    cont = int(sheet.cell("E1").value) + 1
    st.session_state.diff = f"Chat nº {str(cont).zfill(4)} iniciado as {hora}" 
    sheet.update_value(f'E1', cont)


def save_message(sheet, speaker, message):
    all_records = sheet.get_all_records()
    last_row = len(all_records) + 2  # Próxima linha vazia
    sheet.update_value(f'A{last_row}', speaker)
    sheet.update_value(f'B{last_row}', message)
    texto = st.session_state.diff +" " + " mensagem nº " + str(st.session_state.contador)
    sheet.update_value(f'C{last_row}', texto)
    st.session_state.contador += 1 

inicio = 0
if inicio == 0:
    inicio = 1
# st.title("Chat-PGD")
if "messages" not in st.session_state:
    st.session_state.messages = []
    save_message(sheet, "NovoChat", "NovoChat")

pergunta += st.session_state.diff + "\n" + "--Início do Chat--\n"
for message in st.session_state.messages:
    if message["role"] == "user":
        pergunta += f"\npergunta:\n{message['content']}"
    else:
        pergunta += f"\nresposta:\n{message['content']}"
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua dúvida sobre o PGD..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(sheet, "Usuário", prompt)
    pergunta += f"\npergunta:\n{prompt}"
    result = llm.invoke(pergunta)
    response = result.content
    pergunta += f"\nresposta:\n{response}"
    if response:
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message(sheet, "Sistema", response)

