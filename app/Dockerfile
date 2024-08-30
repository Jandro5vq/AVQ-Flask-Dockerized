# Usa una imagen base de Debian
FROM debian:latest

# Instalación de dependencias necesarias
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    libnss3 \
    pkg-config \
    default-libmysqlclient-dev \
    libgbm-dev \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxtst6 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    libvulkan1 \
    xdg-utils \
    python3 \
    python3-pip \
    python3.11-venv \
    curl \
    neofetch \
    && rm -rf /var/lib/apt/lists/*

# Instala Google Chrome
RUN curl -sS https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /tmp/google-chrome.deb && \
    apt-get install -y /tmp/google-chrome.deb && \
    rm /tmp/google-chrome.deb

# Configura .bashrc para ejecutar clear y neofetch al iniciar bash
RUN echo 'clear' >> /root/.bashrc && \
    echo 'neofetch' >> /root/.bashrc

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

# Comando por defecto para iniciar el contenedor
CMD ["flask", "run", "--host=0.0.0.0"]