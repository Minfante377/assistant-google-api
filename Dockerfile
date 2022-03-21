FROM python:3.8
COPY requirements.txt /src/requirements.txt
WORKDIR /src
RUN pip install -r requirements.txt
COPY . /src
ENV PORT $PORT
CMD uvicorn api:app --reload --host 0.0.0.0 --port $PORT
