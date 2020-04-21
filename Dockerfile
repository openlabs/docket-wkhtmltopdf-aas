FROM madnight/docker-alpine-wkhtmltopdf
MAINTAINER Artem Khizhka <artem.khizhka.work@gmail.com>

# Install dependencies for running web service
RUN apk add --update py-pip
RUN apk add --update bash
RUN pip install werkzeug executor gunicorn

ADD app.py /app.py
EXPOSE 80

ENTRYPOINT ["gunicorn"]

# Show the extended help
CMD ["-b", "0.0.0.0:80", "--log-file", "-", "app:application"]
