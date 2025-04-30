FROM python:3.12

WORKDIR /app
COPY . /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    libexpat1 \
    gdal-bin \
    libgdal-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENTRYPOINT ["python", "run.py"]
