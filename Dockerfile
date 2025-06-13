FROM python:3.11.13

WORKDIR /app

COPY . /app

RUN pip install -r env/requirements.txt

CMD ["python", "src/main.py"]