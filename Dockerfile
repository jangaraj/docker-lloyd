FROM dckr/docker-backup
MAINTAINER Johannes 'fish' Ziemke <fish@docker.com>

RUN \
  apk update && \
  apk upgrade && \
  apk add git py-pip python py-setuptools py-dateutil ssmtp bash && \
  git clone https://github.com/s3tools/s3cmd.git /s3cmd && \
  pip install docker-py && \
  cd /s3cmd && python setup.py install

ADD run   /docker-backup/
ADD docker_backup.py /docker-backup/
ADD s3cfg /.s3cfg
ENTRYPOINT [ "./run" ]
