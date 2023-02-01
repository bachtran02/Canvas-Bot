FROM python:3.9

COPY canvas_bot/ canvas_bot/
COPY requirements.txt ./requirements.txt
COPY secrets/ secrets/

RUN pip install -r requirements.txt

CMD ["python", "-O", "-m", "canvas_bot" ]
