FROM python:3.13-slim

WORKDIR /app/frontend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/frontend

# Expose the port from environment variable, default to 8501
ARG FRONTEND_PORT=8501
EXPOSE ${FRONTEND_PORT}

CMD ["sh", "-c", "streamlit run app.py --server.port=${FRONTEND_PORT} --server.address=0.0.0.0"]    