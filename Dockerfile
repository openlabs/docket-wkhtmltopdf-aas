FROM ubuntu:14.04.3
MAINTAINER Sharoon Thomas <sharoon.thomas@openlabs.co.in>

RUN sed 's/main$/main universe/' -i /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

# Download and install wkhtmltopdf
RUN apt-get install -y build-essential xorg libssl-dev libxrender-dev wget gdebi
RUN wget http://download.gna.org/wkhtmltopdf/0.12/0.12.2.1/wkhtmltox-0.12.2.1_linux-trusty-amd64.deb
RUN gdebi --n wkhtmltox-0.12.2.1_linux-trusty-amd64.deb

# Install dependencies for running web service
RUN apt-get install -y python-pip
RUN pip install werkzeug executor gunicorn

# Copy the python app that gunicorn will use
ADD app.py /app.py
EXPOSE 80

# Execute gunicorn on the docker
ENTRYPOINT ["/usr/local/bin/gunicorn"]
CMD ["-b", "0.0.0.0:80", "--log-file", "-", "app:application"]
