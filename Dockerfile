FROM ubuntu:18.04

COPY src/requirements.txt /requirements.txt
RUN apt-get update && \
    apt-get -y install python3-pip python-pip gcc && \
    rm -rf /var/cache/apt && \
    apt-get clean && \
    pip3 install -r /requirements.txt

COPY app /app
RUN export PYTHONPATH=$PYTHONPATH:/app
RUN chmod +x /app/main.py /app/start.sh

WORKDIR /app

ENTRYPOINT ["/app/start.sh"]