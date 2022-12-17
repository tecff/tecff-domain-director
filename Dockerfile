FROM python:3.7

WORKDIR /director

COPY MANIFEST.in README.rst Pipfile Pipfile.lock domains.geojson setup.py /director/

COPY director /director/director

RUN pip install ./

EXPOSE 28530

CMD ["python", "-u", "-m", "director", "--config", "config.yml"]