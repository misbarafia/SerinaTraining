FROM python:3.8.12
WORKDIR /
RUN apt-get update
COPY requirements.txt /
RUN pip3 install -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]