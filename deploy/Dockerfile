FROM python:3.12-slim

WORKDIR /app/Ge-Prime-Matrix

COPY Ge-Prime-Matrix/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Ge-Prime-Matrix/ .

ENV GE_PRIME_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV HOST=0.0.0.0
ENV OPEN_BROWSER=0

EXPOSE 5000

CMD ["python", "scripts/run_server.py"]
