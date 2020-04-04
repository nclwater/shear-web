FROM continuumio/miniconda
COPY environment.yml .
RUN conda env update -n base -f environment.yml
COPY app /app
WORKDIR /app
EXPOSE 8000
CMD gunicorn index:server -b 0.0.0.0:8000