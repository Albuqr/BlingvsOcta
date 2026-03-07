FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8505/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8505", "--server.address=0.0.0.0"]
