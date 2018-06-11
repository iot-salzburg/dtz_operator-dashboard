FROM python:3.6.1-onbuild
MAINTAINER Christoph Schranz <christoph.schranz@salzburgresearch.at>

RUN pip install -r requirements.txt


ADD . /usr/src/

ENV PYTHONPATH .
ENTRYPOINT ["python", "operator_dashboard.py"]
