import io
import os
import streamlit as st
from fpdf import FPDF
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="EasyScript",
    page_icon="🎬",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Libre Baskerville', serif;
    background-color: #FFFEDC;
    color: #333;
}

/* Streamlit app containers */
.stApp, .stApp > header, section.main, .block-container,
[data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"], [data-testid="stMainBlockContainer"],
[data-testid="stMain"], .main .block-container {
    background-color: #FFFEDC !important;
}

/* Cabeçalho */
.main-title {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #E1587D, #EF819E);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.subtitle {
    color: #888;
    font-size: 1rem;
    margin-top: 0.2rem;
    margin-bottom: 2rem;
}

/* Seções */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #E1587D;
    border-left: 3px solid #E1587D;
    padding-left: 0.6rem;
    margin: 1.6rem 0 0.8rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Inputs e textareas */
input, textarea {
    background-color: #EF819E !important;
    color: #FFFFFF !important;
    border: 1px solid #E1587D !important;
    border-radius: 8px !important;
}
input::placeholder, textarea::placeholder {
    color: rgba(255,255,255,0.6) !important;
}

/* Comboboxes / selectboxes (BaseWeb) */
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div,
[data-baseweb="base-input"],
[data-baseweb="input"],
div[class*="InputContainer"],
div[class*="valueContainer"],
div[class*="controlContainer"] {
    background-color: #EF819E !important;
    color: #FFFFFF !important;
    border: 1px solid #E1587D !important;
    border-radius: 8px !important;
}

/* Texto selecionado no combobox */
[data-baseweb="select"] span,
[data-baseweb="select"] div[aria-selected] {
    color: #FFFFFF !important;
}

/* Ícone de seta */
[data-baseweb="select"] svg {
    fill: #FFFFFF !important;
}

/* Lista dropdown */
[data-baseweb="popover"], [data-baseweb="menu"],
ul[data-baseweb="menu"] {
    background-color: #EF819E !important;
    border: 1px solid #E1587D !important;
}
[role="option"] {
    background-color: #EF819E !important;
    color: #FFFFFF !important;
}
[role="option"]:hover, [aria-selected="true"] {
    background-color: #E1587D !important;
}

/* Botão principal */
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #E1587D, #EF819E);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.6rem 2rem;
    transition: opacity 0.2s;
}
div.stButton > button[kind="primary"]:hover { opacity: 0.85; }

/* Botões secundários */
div.stButton > button[kind="secondary"] {
    background-color: #EF819E;
    color: #FFFFFF;
    border: 1px solid #E1587D;
    border-radius: 8px;
}

/* Barra de progresso */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #E1587D, #EF819E) !important;
}

/* Área do roteiro */
.roteiro-box {
    background-color: #EF819E;
    border: 1px solid #E1587D;
    border-radius: 10px;
    padding: 1.4rem;
    max-height: 520px;
    overflow-y: auto;
    font-size: 0.92rem;
    line-height: 1.7;
    white-space: pre-wrap;
    color: #FFFFFF;
}

div[data-testid="stHorizontalBlock"] { gap: 0.6rem; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def gerar_pdf(texto: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.set_auto_page_break(auto=True, margin=15)
    for linha in texto.split("\n"):
        pdf.multi_cell(0, 7, txt=linha)
    return bytes(pdf.output())


def calcular_progresso(tema: str, descricao: str) -> int:
    preenchidos = sum([bool(tema.strip()), bool(descricao.strip())])
    return int((preenchidos / 2) * 100)


def montar_prompt(
    tema, descricao, idioma, genero, plataforma, duracao,
    publico, tom, hook_tipo, cta, narrador, referencias, evitar, observacoes
) -> str:
    partes = [
        f"Você é um roteirista especialista em vídeos curtos para redes sociais.",
        f"Crie um roteiro completo para o seguinte vídeo:\n",
        f"**TEMA:** {tema}",
        f"**DESCRIÇÃO/CONTEXTO:** {descricao}",
        f"**IDIOMA:** {idioma}",
        f"**GÊNERO:** {genero}",
        f"**PLATAFORMA:** {plataforma}",
        f"**DURAÇÃO ALVO:** {duracao}",
        f"**PÚBLICO-ALVO:** {publico}",
        f"**TOM DE NARRAÇÃO:** {tom}",
        f"**TIPO DE HOOK:** {hook_tipo}",
        f"**CALL TO ACTION FINAL:** {cta}",
    ]
    if narrador.strip():
        partes.append(f"**NARRADOR/PERSONAGEM:** {narrador}")
    if referencias.strip():
        partes.append(f"**REFERÊNCIAS/EXEMPLOS:** {referencias}")
    if evitar.strip():
        partes.append(f"**PALAVRAS/TEMAS A EVITAR:** {evitar}")
    if observacoes.strip():
        partes.append(f"**OBSERVAÇÕES EXTRAS:** {observacoes}")

    partes.append("""
---
**FORMATO DE SAÍDA OBRIGATÓRIO:**

Estruture o roteiro em cenas numeradas com:
- Marcação de tempo (ex: [0:00–0:05])
- Rótulo da cena (HOOK, DESENVOLVIMENTO, FECHAMENTO, CTA)
- Instruções visuais entre colchetes (ex: [close no rosto, iluminação suave])
- Fala do narrador em texto corrido
- Ao final: "**Duração total estimada:** X segundos/minutos"

Seja criativo, direto e adequado à plataforma especificada.
""")
    return "\n".join(partes)


def gerar_roteiro(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("Chave de API não encontrada. Configure a variável GROQ_API_KEY no arquivo .env")
        return ""
    client = Groq(api_key=api_key)
    for model in ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception:
            continue
    st.error("Não foi possível gerar o roteiro. Verifique sua chave Groq e tente novamente.")
    return ""


# ── Estado da sessão ──────────────────────────────────────────────────────────

if "roteiro" not in st.session_state:
    st.session_state.roteiro = ""
if "gerando" not in st.session_state:
    st.session_state.gerando = False

# ── Interface ─────────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">EasyScript</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Gerador de roteiros para Instagram Reels, TikTok e YouTube Shorts</p>',
    unsafe_allow_html=True,
)

col_form, col_resultado = st.columns([1.1, 1], gap="large")

with col_form:
    # ① Informações essenciais
    st.markdown('<p class="section-title">① Informações essenciais</p>', unsafe_allow_html=True)

    tema = st.text_input("Tema do vídeo *", placeholder="Ex: Como acordar cedo sem sofrimento")
    descricao = st.text_area(
        "Descrição do vídeo *",
        height=110,
        placeholder=(
            "Descreva o que você quer comunicar, o contexto do vídeo, "
            "referências que você tem em mente, mensagem principal e qualquer detalhe relevante."
        ),
    )

    c1, c2 = st.columns(2)
    with c1:
        idioma = st.selectbox("Idioma", ["Português brasileiro", "Inglês", "Espanhol", "Francês"])
    with c2:
        plataforma = st.selectbox(
            "Plataforma",
            ["Instagram Reels", "TikTok", "YouTube Shorts", "Todos"],
        )

    genero = st.selectbox(
        "Gênero do vídeo",
        ["Educativo", "Comédia", "Informativo", "Motivacional", "Storytelling",
         "Tutorial", "Opinião", "Entretenimento", "Drama", "Lifestyle"],
    )

    duracao = st.radio(
        "Duração alvo",
        ["30 segundos", "60 segundos", "90 segundos", "3 minutos"],
        horizontal=True,
    )

    # ② Público & Tom
    st.markdown('<p class="section-title">② Público & Tom</p>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        publico = st.selectbox(
            "Público-alvo",
            ["Jovens (13–24)", "Adultos jovens (25–34)", "Adultos (35+)", "Público geral",
             "Profissionais", "Estudantes", "Mães/Pais", "Empreendedores"],
        )
    with c4:
        tom = st.selectbox(
            "Tom da narração",
            ["Descontraído", "Sério", "Inspirador", "Provocador", "Íntimo", "Energético", "Reflexivo"],
        )

    # ③ Estrutura & Estilo
    st.markdown('<p class="section-title">③ Estrutura & Estilo</p>', unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        hook_tipo = st.selectbox(
            "Tipo de hook",
            ["Pergunta instigante", "Fato surpreendente", "Afirmação polêmica",
             "História pessoal", "Desafio ao espectador", "Estatística impactante"],
        )
    with c6:
        cta = st.selectbox(
            "Call to action final",
            ["Salvar", "Seguir", "Comentar", "Marcar amigo", "Compartilhar",
             "Visitar link na bio", "Nenhum"],
        )

    narrador = st.text_input("Narrador/Personagem", placeholder="Ex: Especialista em produtividade, jovem de 22 anos")
    referencias = st.text_input("Referências/Exemplos", placeholder="Ex: Estilo do canal X, vídeo Y")
    evitar = st.text_input("Palavras/Temas a evitar", placeholder="Ex: palavrões, política, concorrente Z")
    observacoes = st.text_area("Observações extras", height=70, placeholder="Qualquer outra instrução específica...")

    # Barra de progresso
    progresso = calcular_progresso(tema, descricao)
    st.markdown(f"**Preenchimento dos campos obrigatórios:** {progresso}%")
    st.progress(progresso / 100)

    # Botão gerar
    pode_gerar = bool(tema.strip()) and bool(descricao.strip())
    if st.button("🎬 Gerar Roteiro", type="primary", disabled=not pode_gerar, use_container_width=True):
        with col_resultado:
            with st.spinner("Gerando roteiro..."):
                prompt = montar_prompt(
                    tema, descricao, idioma, genero, plataforma, duracao,
                    publico, tom, hook_tipo, cta, narrador, referencias, evitar, observacoes
                )
                st.session_state.roteiro = gerar_roteiro(prompt)

# ── Resultado ─────────────────────────────────────────────────────────────────

with col_resultado:
    if st.session_state.roteiro:
        st.markdown('<p class="section-title">Roteiro gerado</p>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="roteiro-box">{st.session_state.roteiro}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("")
        c_copy, c_pdf, c_novo = st.columns(3)

        with c_copy:
            roteiro_js = st.session_state.roteiro.replace("`", "\\`").replace("\n", "\\n")
            copy_js = f"""
            <button onclick="navigator.clipboard.writeText(`{roteiro_js}`).then(()=>this.innerText='✓ Copiado!')"
                style="width:100%;padding:0.45rem;background:#EF819E;color:#FFFFFF;border:1px solid #E1587D;
                       border-radius:8px;cursor:pointer;font-family:'Libre Baskerville',serif;font-size:0.85rem;">
                📋 Copiar
            </button>
            """
            st.markdown(copy_js, unsafe_allow_html=True)

        with c_pdf:
            st.download_button(
                label="⬇️ Baixar PDF",
                data=gerar_pdf(st.session_state.roteiro),
                file_name="roteiro_easyscript.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with c_novo:
            if st.button("🔄 Novo roteiro", use_container_width=True):
                st.session_state.roteiro = ""
                st.rerun()
    else:
        st.markdown("")
        st.markdown(
            """
            <div style="margin-top:4rem;text-align:center;color:#888;">
                <div style="font-size:3rem;">🎬</div>
                <p style="font-size:1rem;margin-top:0.5rem;">
                    Preencha os campos ao lado e clique em<br>
                    <strong style="color:#E1587D;">Gerar Roteiro</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
