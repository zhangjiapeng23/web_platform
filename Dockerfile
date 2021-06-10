FROM python:3.8.10

COPY ./ /djangoProj/mobileqaserve
RUN pip3 install -r /djangoProj/mobileqaserve/requirements.txt \
    pip3 install uwsgi

EXPOSE 8080
CMD ["cd", "/djangoProj/mobileqaserve"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]
#CMD ["python", "/djangoProj/mobileqaserve/manage.py", "runserver", "0.0.0.0:8080", "--settings=mobile_QA_web_platform.settings.prod"]

