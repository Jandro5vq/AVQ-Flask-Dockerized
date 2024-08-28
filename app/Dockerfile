# Usa la imagen base de Python
FROM python:3.12-bullseye

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]