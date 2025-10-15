FROM my_backend_base:3.13     

# Copy the rest of the backend code
COPY . /app/backend

# Make sure Python finds backend modules
ENV PYTHONPATH=/app

ARG BACKEND_PORT=8000
EXPOSE ${BACKEND_PORT}

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${BACKEND_PORT}"]
