FROM python:3.6.1-onbuild
MAINTAINER Christoph Schranz <christoph.schranz@salzburgresearch.at>

ADD . /home/src
RUN pip install -r requirements.txt

ENV PYTHONPATH .
ENTRYPOINT ["python", "app/operator_dashboard.py"]
