FROM python:3

WORKDIR /code

COPY requirement.txt ./

RUN pip install -r requirement.txt

COPY . /code/

EXPOSE 8000

CMD ["uvicorn", "Library_Management.main:app", "--host", "0.0.0.0", "--port", "8000"]
