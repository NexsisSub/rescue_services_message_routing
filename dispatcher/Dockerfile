FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY ./app /app
COPY ./scripts/wait-for-it.sh /scripts/wait-for-it.sh

RUN chmod +x /scripts/wait-for-it.sh
CMD ["/scripts/wait-for-it.sh", "$${AMQP_URI}",  "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8881", "--reload"]
 