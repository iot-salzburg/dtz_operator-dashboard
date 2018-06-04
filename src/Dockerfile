FROM python:3.6.1-onbuild
MAINTAINER Christoph Schranz <christoph.schranz@salzburgresearch.at>

RUN pip install -r requirements.txt
ADD . /home/src

ENV PYTHONPATH .
ENTRYPOINT ["python", "app/operator_dashboard.py"]
