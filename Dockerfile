FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git 

RUN pip3 install PyYAML --break-system-packages
RUN pip3 install PrettyTable --break-system-packages
RUN pip3 install feedparser --break-system-packages
RUN pip3 install bs4 --break-system-packages
RUN pip3 install requests --break-system-packages

COPY rss.py /usr/bin/rss.py
COPY config.py /usr/bin/config.py

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT  ["/entrypoint.sh"]
