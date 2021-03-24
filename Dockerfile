FROM python:slim

WORKDIR /tmp/ventilator

COPY requirements.txt .
COPY setup.cfg .
COPY setup.py .
COPY README.md .
COPY ventilator/ ./ventilator/

RUN pip3 install .

ENTRYPOINT ["ventilator"]
