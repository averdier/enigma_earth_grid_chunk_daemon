FROM python:3.7

ADD ./requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir /daemon

ADD ./app/ /daemon/app
ADD ./utils/ /daemon/utils
ADD ./config.py /daemon/config.py
ADD ./run_daemon.py /daemon/run_daemon.py

WORKDIR /daemon

CMD ["python3", "run_daemon.py"]