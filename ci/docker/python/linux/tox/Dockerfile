FROM ubuntu:20.04 as wheel_builder_base
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update
RUN cat /tmp/apt-packages.txt | xargs apt install -y python3-pip
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

FROM wheel_builder_base as wheel_builder_py36
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

RUN apt install -y python3.6-dev python3.6-venv
COPY ci/docker/python/shared/requirements-ci.txt  requirements.txt  /tmp/
RUN PYTHON=python3.6 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt

# ==============================================================================
FROM wheel_builder_base as wheel_builder_py37
RUN apt install -y python3.7-dev python3.7-venv
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt  requirements.txt  /tmp/
RUN PYTHON=python3.7 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt

# ==============================================================================
FROM wheel_builder_base as wheel_builder_py38
RUN apt install -y python3.8-dev python3.8-venv
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt  requirements.txt  /tmp/
RUN PYTHON=python3.8 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt

# ==============================================================================
FROM wheel_builder_base as wheel_builder_py39
RUN apt install -y python3.9-dev python3.9-venv
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt  requirements.txt  /tmp/
RUN PYTHON=python3.9 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt

# ==============================================================================
FROM wheel_builder_base
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY --from=wheel_builder_py36 /wheels/* /wheels/
COPY --from=wheel_builder_py37 /wheels/* /wheels/
COPY --from=wheel_builder_py38 /wheels/* /wheels/
COPY --from=wheel_builder_py39 /wheels/* /wheels/
ENV PIP_FIND_LINKS=/wheels
RUN pip3 install tox