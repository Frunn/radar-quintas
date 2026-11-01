import streamlit as st
import pandas as pd
from urllib.parse import quote
from pathlib import Path
from datetime import date

st.set_page_config(page_title="Radar de Quintas", page_icon="🌳", layout="wide")
DATA_FILE = Path("quintas_guardadas.csv")
COLUMNS = ["Data", "Portal", "Título", "Localidade", "Preço (€)", "Terreno (m²)",
           "Área construída (m²)", "Estado", "Estacionamento", "URL", "Notas", "Classificação"]

def load_data():
    if DATA_FILE.exists():
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)

def search_url(query):
    return "https://www.google.com/search?q=" + quote(query)

st.title("🌳 Radar de Quintas")
st.caption("Pesquisa e acompanhamento de quintas, casas rurais e terrenos no Douro.")

with st.sidebar:
    st.header("Critérios de pesquisa")
    areas = st.multiselect(
        "Concelhos / zonas",
        ["Baião", "Amarante", "Marco de Canaveses", "Mesão Frio", "Peso da Régua",
         "Lamego", "Resende", "Cinfães", "Santa Marta de Penaguião", "Vila Real"],
        default=["Baião", "Amarante", "Marco de Canaveses"]
    )
    min_price, max_price = st.slider("Orçamento (€)", 0, 300000, (100000, 150000), step=5000)
    min_land, max_land = st.slider("Área de terreno (m²)", 0, 30000, (3000, 10000), step=500)
    property_types = st.multiselect(
        "Tipologias",
        ["quinta", "casa de campo", "moradia", "terreno", "casa para recuperar", "ruína"],
        default=["quinta", "casa de campo", "moradia", "casa para recuperar"]
    )
    st.caption("Preço e área são usados para avaliar os resultados, não como termos obrigatórios da pesquisa.")
    st.checkbox("Espaço para guardar dois veículos", value=True)
    st.caption("Mercedes CLK e Nissan Terrano II")

tabs = st.tabs(["🔎 Pesquisar", "📌 Imóveis guardados", "ℹ️ Avaliação"])

with tabs[0]:
    st.subheader("Pesquisas mais abrangentes")
    st.write("Escolhe um portal e uma localidade. Cada ligação abre uma pesquisa menos restritiva.")
    portals = [
        ("Idealista", "idealista.pt"),
        ("Imovirtual", "imovirtual.com"),
        ("OLX", "olx.pt"),
        ("Casa Sapo", "casasapo.pt"),
        ("SuperCasa", "supercasa.pt"),
        ("CustoJusto", "custojusto.pt"),
        ("RE/MAX", "remax.pt"),
    ]
    if not areas:
        st.warning("Seleciona pelo menos um concelho na barra lateral.")
    else:
        terms = property_types or ["quinta", "casa de campo", "moradia"]
        for area in areas:
            with st.expander(f"📍 {area}", expanded=(area == areas[0])):
                cols = st.columns(3)
                for i, (portal, domain) in enumerate(portals):
                    # Search only locality + alternatives; no exact price/area terms.
                    type_group = " OR ".join(f'"{term}"' for term in terms)
                    query = f'site:{domain} "{area}" ({type_group})'
                    with cols[i % 3]:
                        st.markdown(f"**{portal}**")
                        st.link_button("Pesquisar", search_url(query), use_container_width=True)
                general_query = f'"{area}" ({ " OR ".join(f"{t}" for t in terms) }) quinta imóvel rural'
                st.link_button("Pesquisa geral no Google", search_url(general_query))
    st.info("Os resultados dependem do que cada portal permite ao Google indexar. Se um portal não devolver resultados, experimenta a pesquisa geral ou pesquisa diretamente no próprio portal.")

with tabs[1]:
    st.subheader("Registar e comparar imóveis")
    records = load_data()
    with st.expander("＋ Adicionar imóvel", expanded=True):
        with st.form("new_property", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                d = st.date_input("Data", value=date.today())
                portal = st.selectbox("Portal", ["Idealista", "Imovirtual", "OLX", "Casa Sapo", "SuperCasa", "CustoJusto", "RE/MAX", "Outro"])
                title = st.text_input("Título do anúncio")
                location = st.text_input("Localidade / freguesia")
            with c2:
                price = st.number_input("Preço (€)", min_value=0, step=1000)
                land = st.number_input("Terreno (m²)", min_value=0, step=100)
                built = st.number_input("Área construída (m²)", min_value=0, step=10)
                condition = st.selectbox("Estado", ["Habitável", "A necessitar de obras", "Ruína / recuperação integral", "Por confirmar"])
            with c3:
                parking = st.selectbox("Estacionamento", ["Garagem", "Anexo / armazém", "Espaço exterior", "Não tem", "Por confirmar"])
                score = st.select_slider("Classificação", ["Baixa", "Média", "Boa", "Excelente"], value="Média")
                url = st.text_input("URL do anúncio")
                notes = st.text_area("Notas", height=90)
            if st.form_submit_button("Guardar imóvel", type="primary"):
                row = {"Data": d.isoformat(), "Portal": portal, "Título": title, "Localidade": location,
                       "Preço (€)": price, "Terreno (m²)": land, "Área construída (m²)": built,
                       "Estado": condition, "Estacionamento": parking, "URL": url,
                       "Notas": notes, "Classificação": score}
                records = pd.concat([records, pd.DataFrame([row])], ignore_index=True)
                records.to_csv(DATA_FILE, index=False)
                st.success("Imóvel guardado.")
                st.rerun()
    records = load_data()
    if not records.empty:
        st.dataframe(records, use_container_width=True, hide_index=True)
        st.download_button("Descarregar CSV", records.to_csv(index=False).encode("utf-8-sig"),
                           "quintas_guardadas.csv", "text/csv")
    else:
        st.caption("Ainda não existem imóveis guardados.")

with tabs[2]:
    st.subheader("Critérios de avaliação")
    st.markdown("""
    - **Orçamento:** 100.000–150.000 € como referência inicial.
    - **Terreno:** preferência por 3.000–10.000 m².
    - **Estado:** aceitar imóveis que necessitem de reabilitação.
    - **Edifícios:** avaliar estrutura, anexos e potencial de recuperação.
    - **Acessos:** confirmar acesso automóvel e espaço para os dois veículos.
    - **Condicionantes:** verificar PDM, REN/RAN, servidões, água, saneamento e licenciamento.
    """)
st.caption("Radar de Quintas · Versão de pesquisa corrigida. A pesquisa é feita através dos motores de pesquisa; não existe recolha automática de anúncios nesta versão.")
