FROM python:3.8.10

RUN localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
ENV LC_ALL zh_CN.UTF-8

COPY ./* /djangoProj/mobileqaserve
RUN pip3 install -r /djangoProj/mobileqaserve/requirements.txt

EXPOSE 8080

CMD ["python", "/djangoProj/mobileqaserve/manage.py", "runserver", "0.0.0.0:8080"]

