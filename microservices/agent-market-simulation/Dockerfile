# Dockerfile of agent1
FROM python:3.13-slim

WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED True
ENV PORT 8080
COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY agent_core .

CMD ["sh", "-c","adk web --port $PORT --host 0.0.0.0"]