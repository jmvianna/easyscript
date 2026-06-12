# EasyScript

Gerador automático de roteiros para vídeos curtos de redes sociais (Instagram Reels, TikTok e YouTube Shorts), feito em Python com Streamlit e integrado à API da OpenAI.

## Funcionalidades

- Gera roteiros estruturados com hook, desenvolvimento e fechamento
- Suporta múltiplos gêneros: comédia, educativo, motivacional, storytelling, tutorial e mais
- Configurações de público-alvo, tom de narração, plataforma e duração
- Exportação do roteiro em `.txt`
- Interface dark mode com identidade visual moderna

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/easyscript.git
cd easyscript

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Configuração da API

1. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```
2. Abra o `.env` e substitua `sua_chave_aqui` pela sua chave da OpenAI:
   ```
   OPENAI_API_KEY=sk-...
   ```

## Execução

```bash
streamlit run app.py
```

Acesse em: `http://localhost:8501`

## Deploy no Streamlit Cloud

1. Suba o repositório no GitHub.
2. Acesse [share.streamlit.io](https://share.streamlit.io) e conecte o repositório.
3. Em **Secrets**, adicione:
   ```
   OPENAI_API_KEY = "sk-..."
   ```
4. Clique em **Deploy**.

## Estrutura do projeto

```
easyscript/
├── app.py              # Aplicativo principal
├── requirements.txt    # Dependências
├── .env.example        # Exemplo de variável de ambiente
├── .gitignore
└── README.md
```
