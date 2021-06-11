FROM python:3.8.10

COPY ./ /mobileqaserve
RUN pip3 install -r /mobileqaserve/requirements.txt &&\
    pip3 install uwsgi &&\
    python /mobileqaserve/manage.py collectstatic --settings=mobile_QA_web_platform.settings.prod

EXPOSE 8023
CMD ["uwsgi", "--ini", "/mobileqaserve/uwsgi.ini"]

