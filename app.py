import streamlit as st
import pandas as pd
from urllib.parse import quote
from pathlib import Path
from datetime import date

st.set_page_config(page_title="Radar de Quintas", page_icon="🌳", layout="wide")

DATA_FILE = Path("quintas_guardadas.csv")
COLUMNS = [
    "Data", "Portal", "Título", "Localidade", "Preço (€)", "Terreno (m²)",
    "Área construída (m²)", "Estado", "Estacionamento", "URL", "Notas", "Classificação"
]

def load_data():
    if DATA_FILE.exists():
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)

def google_search_url(query: str) -> str:
    return "https://www.google.com/search?q=" + quote(query)

st.title("🌳 Radar de Quintas")
st.caption("Acompanhar oportunidades de quintas, casas rurais e terrenos no Douro e envolvente.")

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
        "Tipologia",
        ["Quinta", "Casa de campo", "Moradia", "Terreno com construção", "Casa para recuperar"],
        default=["Quinta", "Casa de campo", "Moradia", "Casa para recuperar"]
    )
    include_renovation = st.checkbox("Incluir imóveis para recuperar", value=True)
    st.markdown("---")
    st.caption("Requisitos adicionais")
    garage = st.checkbox("Espaço para guardar dois veículos", value=True)
    st.caption("Mercedes CLK e Nissan Terrano II")
    additional_notes = st.text_area(
        "Outras preferências",
        "Aceito obras de reabilitação. Preferência por propriedade com terreno e edifícios existentes."
    )

tab_search, tab_saved, tab_method = st.tabs(["🔎 Pesquisar", "📌 Imóveis guardados", "ℹ️ Como avaliar"])

with tab_search:
    st.subheader("Pesquisas nos portais")
    if not areas:
        st.warning("Seleciona pelo menos um concelho na barra lateral.")
    else:
        area_query = " OR ".join(f'"{a}"' for a in areas)
        types = property_types or ["quinta"]
        type_query = " OR ".join(f'"{t}"' for t in types)
        state_terms = ' recuperar obras restauro' if include_renovation else ''
        size_terms = f' "{min_land}" "{max_land}"'
        price_terms = f' "{min_price}" "{max_price}"'
        common = f'({area_query}) ({type_query}){state_terms} quinta propriedade rural{price_terms}{size_terms}'
        portals = [
            ("Idealista", "idealista.pt"),
            ("Imovirtual", "imovirtual.com"),
            ("OLX", "olx.pt"),
            ("Casa Sapo", "casasapo.pt"),
            ("SuperCasa", "supercasa.pt"),
            ("CustoJusto", "custojusto.pt"),
            ("RE/MAX", "remax.pt"),
            ("Pesquisa geral", None),
        ]
        cols = st.columns(4)
        for idx, (label, domain) in enumerate(portals):
            q = f"site:{domain} {common}" if domain else common
            with cols[idx % 4]:
                st.markdown(f"**{label}**")
                st.link_button("Abrir pesquisa", google_search_url(q), use_container_width=True)

        st.caption(
            f"Parâmetros selecionados: {', '.join(areas)} · {min_price:,}–{max_price:,} € · "
            f"{min_land:,}–{max_land:,} m²".replace(",", " ")
        )

    st.info(
        "Esta versão prepara pesquisas direcionadas e permite registar os resultados manualmente. "
        "Ainda não recolhe anúncios automaticamente: os portais podem exigir sessão, CAPTCHA ou "
        "restringir a recolha automatizada."
    )

with tab_saved:
    st.subheader("Registar uma oportunidade")
    records = load_data()
    with st.expander("＋ Adicionar imóvel", expanded=True):
        with st.form("new_property", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                listing_date = st.date_input("Data de consulta", value=date.today())
                portal = st.selectbox("Portal", ["Idealista", "Imovirtual", "OLX", "Casa Sapo", "SuperCasa", "CustoJusto", "RE/MAX", "Outro"])
                title = st.text_input("Título do anúncio")
                location = st.text_input("Localidade / freguesia")
            with c2:
                price = st.number_input("Preço (€)", min_value=0, step=1000)
                land = st.number_input("Área do terreno (m²)", min_value=0, step=100)
                built = st.number_input("Área construída (m²)", min_value=0, step=10)
                condition = st.selectbox("Estado", ["Habitável", "A necessitar de obras", "Ruína / recuperação integral", "Por confirmar"])
            with c3:
                parking = st.selectbox("Estacionamento", ["Garagem", "Anexo / armazém", "Espaço exterior", "Não tem", "Por confirmar"])
                score = st.select_slider("Classificação", ["Baixa", "Média", "Boa", "Excelente"], value="Média")
                url = st.text_input("URL do anúncio")
                comments = st.text_area("Notas", height=90)
            save = st.form_submit_button("Guardar imóvel", type="primary")
            if save:
                item = {
                    "Data": listing_date.isoformat(), "Portal": portal, "Título": title,
                    "Localidade": location, "Preço (€)": price, "Terreno (m²)": land,
                    "Área construída (m²)": built, "Estado": condition,
                    "Estacionamento": parking, "URL": url, "Notas": comments,
                    "Classificação": score
                }
                records = pd.concat([records, pd.DataFrame([item])], ignore_index=True)
                records.to_csv(DATA_FILE, index=False)
                st.success("Imóvel guardado.")
                st.rerun()

    records = load_data()
    if not records.empty:
        st.subheader(f"{len(records)} imóvel(is) registado(s)")
        c1, c2 = st.columns(2)
        with c1:
            price_limit = st.number_input("Preço máximo a mostrar (€)", min_value=0, value=int(max_price), step=5000)
        with c2:
            area_floor = st.number_input("Área mínima a mostrar (m²)", min_value=0, value=int(min_land), step=500)
        shown = records.copy()
        shown["Preço (€)"] = pd.to_numeric(shown["Preço (€)"], errors="coerce")
        shown["Terreno (m²)"] = pd.to_numeric(shown["Terreno (m²)"], errors="coerce")
        shown = shown[
            (shown["Preço (€)"].fillna(0) <= price_limit) &
            (shown["Terreno (m²)"].fillna(0) >= area_floor)
        ]
        st.dataframe(shown, use_container_width=True, hide_index=True)
        st.download_button(
            "Descarregar lista em CSV",
            records.to_csv(index=False).encode("utf-8-sig"),
            file_name="quintas_guardadas.csv",
            mime="text/csv"
        )
        st.caption("Nota: em alojamento cloud, o CSV local pode não sobreviver a reinícios ou reconstruções da aplicação. Para uso continuado, a próxima evolução deverá ligar uma base de dados persistente.")
    else:
        st.caption("Ainda não existem imóveis guardados.")

with tab_method:
    st.subheader("Critérios para comparar oportunidades")
    st.markdown("""
    **Localização e acessos**
    - Distância a Baião, Amarante e principais vias.
    - Acesso automóvel, inclinação do terreno e exposição solar.

    **Edifícios e terreno**
    - Estado estrutural, anexos, ruínas e potencial de reabilitação.
    - Área útil de terreno, água, saneamento e eletricidade.

    **Viabilidade**
    - PDM e classificação do solo.
    - Condicionantes REN/RAN, servidões e licenciamento.
    - Custos prováveis de reabilitação e manutenção.

    **Necessidade funcional**
    - Espaço de estacionamento ou armazém para dois veículos.
    """)

st.divider()
st.caption("Radar de Quintas · Protótipo inicial")
