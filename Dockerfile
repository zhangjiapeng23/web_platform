FROM python:3.8.10

COPY ./* /djangoProj/mobileqaserve
RUN pip3 install -r /djangoProj/mobileqaserve/requirements.txt

EXPOSE 8080

CMD ["python", "/djangoProj/mobileqaserve/manage.py", "runserver", "0.0.0.0:8080"]

