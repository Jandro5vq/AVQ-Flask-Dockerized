# Usa una imagen base de Debian
FROM debian:latest

# Instalación de dependencias necesarias
RUN apt-get update && \
    apt-get install -y \
    neofetch \
    nano \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-xcb1 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libatspi2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcups2 \
    libnspr4 \
    libxtst6 \
    xdg-utils \
    python3 \
    python3-pip \
    python3.11-venv \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Descargar e instalar ChromeDriver
RUN CHROMEDRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

RUN echo 'clear' >> /root/.bashrc
RUN echo 'neofetch' >> /root/.bashrc

# Establece el directorio de trabajo
WORKDIR /app

COPY . .

# Crear un entorno virtual y activar
RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /app/requirements.txt

# Configurar el contenedor para usar el entorno virtual
ENV PATH="/venv/bin:$PATH"

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]