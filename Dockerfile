FROM python:3.14-slim
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv sync --system
COPY . .
EXPOSE 5000
CMD ["python3", "-m", "flask", "--app", "backend/app.py", "run", "--host=0.0.0.0", "--port=5000"]