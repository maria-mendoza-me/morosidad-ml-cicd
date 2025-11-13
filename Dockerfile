FROM python:3.11-slim

LABEL maintainer="m.mendozame@alum.up.edu.pe"
LABEL description="API de predicción de morosidad - Norte Andino SAC"

WORKDIR /app

COPY requirements_d.txt .

RUN pip install --no-cache-dir -r requirements_d.txt

COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/

EXPOSE 5000

CMD ["python", "src/app.py"]
