FROM python:3.8.10

COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt &&\
    pip3 install uwsgi

COPY ./ /mobileqaserve
RUN python /mobileqaserve/manage.py collectstatic --settings=mobile_QA_web_platform.settings.prod

EXPOSE 8023
CMD ["uwsgi", "--ini", "/mobileqaserve/uwsgi.ini"]

