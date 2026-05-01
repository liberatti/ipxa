FROM --platform=$BUILDPLATFORM node:lts AS build_frontend

WORKDIR /app/web

COPY web/package*.json .
RUN npm install

COPY web /app/web
COPY *.json /app/web/

RUN npm run build

FROM --platform=$TARGETPLATFORM alpine:3.23.3 AS main

RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    gcc
  
ENV PYTHONUSERBASE=/opt/ipxa/site-packages
ENV PATH=/opt/ipxa/venv/bin:$PATH
ENV APP_BASE=/opt/ipxa
ENV DB_PATH=/data

WORKDIR /opt/ipxa

COPY requirements.txt .
RUN python3 -m venv /opt/ipxa/venv \
  && /opt/ipxa/venv/bin/pip install --upgrade pip \
  && /opt/ipxa/venv/bin/pip install -r requirements.txt

COPY --from=build_frontend /app/web/dist static
COPY --from=build_frontend /app/web/dist/index.html templates/
COPY --from=build_frontend /app/web/package.json .

COPY *.py .
COPY api api
COPY config config

RUN adduser -D -s /sbin/nologin nxguard

RUN mkdir -p /data \
  && chown nxguard:nxguard /data

USER nxguard

EXPOSE 5000

VOLUME [ "/data" ]

ENTRYPOINT ["gunicorn", "-c", "api/gunicorn_config.py", "main:app"]
