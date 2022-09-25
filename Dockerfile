FROM python:3.9

COPY canvas_bot/ canvas_bot/
COPY requirements.txt ./requirements.txt
COPY .env /.env

RUN pip install -r requirements.txt

CMD ["python", "-m", "canvas_bot" ]