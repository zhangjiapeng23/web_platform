FROM python:3.8.10

COPY ./requirements.txt ./
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ &&\
    pip3 install -r requirements.txt &&\
    pip3 install uwsgi

COPY ./ /mobileqaserve
COPY ./media /media_backup
RUN python /mobileqaserve/manage.py collectstatic --settings=mobile_QA_web_platform.settings.prod &&\
    python /mobileqaserve/manage.py migrate --settings=mobile_QA_web_platform.settings.prod

EXPOSE 8023
CMD ["uwsgi", "--ini", "/mobileqaserve/uwsgi.ini"]

