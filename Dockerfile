FROM python:3.11-alpine
WORKDIR /app

# ignore pip root user warning
ENV PIP_ROOT_USER_ACTION=ignore

# required for "/advanced version" command
RUN apk add --no-cache git

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

# docker uses ./src as the root directory, pycharm ./
ENV PYTHONPATH /app

# -u unbuffered output (the output does not always work without this)
CMD ["python", "-u", "src/main.py"]
