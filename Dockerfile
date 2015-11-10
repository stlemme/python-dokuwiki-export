
FROM python:3.4

RUN mkdir -p /usr/share/python-dokuwiki-export
WORKDIR /usr/share/python-dokuwiki-export

COPY requirements.txt /usr/share/python-dokuwiki-export/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/share/python-dokuwiki-export
RUN mkdir -p /usr/share/python-dokuwiki-export/_catalog

RUN apt-get install -y git
RUN git submodule update --init

# RUN ls -al

CMD [ "./cron_regenerate.sh" ]

