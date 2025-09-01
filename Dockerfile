FROM python:3.12-slim

# Essa variável de ambiente é usada para controlar se o Python deve 
# gravar arquivos de bytecode (.pyc) no disco. 1 = Não, 0 = Sim
ENV PYTHONDONTWRITEBYTECODE 1

# Define que a saída do Python será exibida imediatamente no console ou em 
# outros dispositivos de saída, sem ser armazenada em buffer.
# Em resumo, você verá os outputs do Python em tempo real.
ENV PYTHONUNBUFFERED 1

# Copia a pasta "backend" e "scripts" para dentro do container.
COPY backend /backend
COPY scripts /scripts

# Entra na pasta backend no container
WORKDIR /backend

# A porta 8000 estará disponível para conexões externas ao container
# É a porta que vamos usar para o Django.
EXPOSE 8000

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências do Python e preparar o ambiente
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /backend/requirements.txt && \
    # Remover a criação do usuário `duser` e ajustar permissões
    mkdir -p /data/web/static && \
    mkdir -p /data/web/media && \
    chmod -R 755 /data/web/static && \
    chmod -R 755 /data/web/media && \
    # Deixar as permissões para o usuário root (padrão do Docker)
    chmod -R +x /scripts

# Adiciona a pasta `scripts` e `venv/bin` no $PATH do container
ENV PATH="/scripts:/venv/bin:$PATH"
# Executa o arquivo scripts/commands.sh
CMD ["commands.sh"]