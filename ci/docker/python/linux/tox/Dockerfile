ARG PIP_DOWNLOAD_CACHE=/.cache/pip
FROM ubuntu:20.04
COPY ci/docker/python/linux/tox/apt-packages.txt /tmp/
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    cat /tmp/apt-packages.txt | xargs apt-get -y install

ARG PIP_DOWNLOAD_CACHE
RUN mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE}

COPY requirements/ /tmp/requirements
RUN python3 -m pip install pip --upgrade && \
    pip3 install wheel && \
    pip3 install -r /tmp/requirements/requirements_tox.txt devpi_client && \
    pip3 wheel -w /wheels --no-cache-dir wheel
WORKDIR /src
CMD tox --workdir /tmp/tox --recreate
