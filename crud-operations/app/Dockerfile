FROM python:3.8.12

WORKDIR /

RUN apt-get update
COPY requirements.txt /
RUN pip3 install -r requirements.txt
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install poppler-utils -y
RUN pip3 install "uvicorn[standard]" gunicorn
RUN pip3 install reportlab==3.6.11
COPY . .
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["sh", "/startup.sh"]