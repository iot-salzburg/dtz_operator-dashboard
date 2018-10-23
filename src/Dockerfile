FROM python:3.6
MAINTAINER Christoph Schranz <christoph.schranz@salzburgresearch.at>

# install the official librdkafka client written in C
ARG LIBRDKAFKA_VERSION
RUN apt-get update && \
    git clone https://github.com/edenhill/librdkafka && cd librdkafka && \
    git checkout v${LIBRDKAFKA_VERSION} && \
    ./configure && make && make install && ldconfig

# install confluent-kafka-client
ARG CONFLUENT_KAFKA_VERSION
RUN pip install confluent-kafka==${CONFLUENT_KAFKA_VERSION}


# install requirements
ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . /usr/src/

ENV PYTHONPATH .
ENTRYPOINT ["python", "/usr/src/operator_dashboard.py"]
