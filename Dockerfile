FROM python:3.11-alpine
WORKDIR /app

# take git hash from build pipeline and set it as an environment variable
ARG GIT_HASH
ENV GIT_HASH ${GIT_HASH}

# ignore pip root user warning
ENV PIP_ROOT_USER_ACTION=ignore

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

# docker uses ./src as the root directory, pycharm ./
ENV PYTHONPATH /app

# -u unbuffered output (the output does not always work without this)
CMD ["python", "-u", "src/main.py"]
