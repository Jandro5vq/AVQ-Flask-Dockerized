# Usa una imagen base de Debian
FROM debian:latest

# Instalación de dependencias necesarias
RUN apt-get update && \
    apt-get install -y \
    neofetch \
    nano \
    wget \
    unzip \
    jq \
    python3 \
    python3-pip \
    python3.11-venv \
    && rm -rf /var/lib/apt/lists/*

# Obtener y procesar el JSON para descargar Google Chrome y ChromeDriver
RUN echo "Descargando JSON de versiones de Chrome..." && \
    wget --show-progress -q https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json -O /tmp/chrome-versions.json && \
    echo "JSON descargado, extrayendo URLs..." && \
    CHROME_URL=$(jq -r '.channels.Stable.downloads.chrome[] | select(.platform=="linux64") | .url' /tmp/chrome-versions.json) && \
    CHROMEDRIVER_URL=$(jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url' /tmp/chrome-versions.json) && \
    echo "URL de Chrome: $CHROME_URL" && \
    echo "URL de ChromeDriver: $CHROMEDRIVER_URL" && \
    echo "Descargando Google Chrome..." && \
    wget --show-progress -q $CHROME_URL -O /tmp/chrome-linux64.zip && \
    echo "Descargando ChromeDriver..." && \
    wget --show-progress -q $CHROMEDRIVER_URL -O /tmp/chromedriver-linux64.zip && \
    echo "Creando directorio para Google Chrome..." && \
    mkdir -p /opt/google/chrome && \
    echo "Descomprimiendo Google Chrome..." && \
    unzip /tmp/chrome-linux64.zip -d /opt/google/chrome && \
    echo "Descomprimiendo ChromeDriver..." && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    echo "Limpieza de archivos temporales..." && \
    rm /tmp/chrome-linux64.zip /tmp/chromedriver-linux64.zip /tmp/chrome-versions.json

# Personalizar bashrc para ejecutar comandos al iniciar la shell
RUN echo 'clear' >> /root/.bashrc
RUN echo 'neofetch' >> /root/.bashrc

# Establece el directorio de trabajo
WORKDIR /app

# Copiar el contenido del directorio actual en la imagen
COPY . .

# Crear un entorno virtual y activar
RUN echo "Creando entorno virtual de Python..." && \
    python3 -m venv /venv && \
    echo "Actualizando pip..." && \
    /venv/bin/pip install --upgrade pip && \
    echo "Instalando dependencias de Python..." && \
    /venv/bin/pip install -r /app/requirements.txt

# Configurar el contenedor para usar el entorno virtual
ENV PATH="/venv/bin:$PATH"

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
