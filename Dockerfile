FROM python:3.11.9-alpine3.18 as builder

WORKDIR /app
COPY requirements.txt .
RUN apk add --no-cache --update gcc python3-dev linux-headers musl-dev
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11.9-alpine3.18 AS main

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
RUN rm -rf /app
COPY . .

CMD ["/bin/sh", "run.sh"]