FROM ubuntu:20.04 as wheel_builder_base
COPY ci/docker/python/linux/tox/apt-packages.txt /tmp/
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    cat /tmp/apt-packages.txt | xargs apt-get -y install
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

FROM wheel_builder_base as WHEEL_BUILDER_PY36
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt  requirements.txt  /tmp/
RUN PYTHON=python3.6 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY37
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt  requirements.txt  /tmp/
RUN PYTHON=python3.7 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY38
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/python/shared/requirements-ci.txt  requirements.txt  /tmp/
RUN PYTHON=python3.8 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY39
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
RUN mkdir -p /.cache/pip && chmod -R 777 /.cache/
COPY --from=WHEEL_BUILDER_PY36 /wheels/* /wheels/
COPY --from=WHEEL_BUILDER_PY37 /wheels/* /wheels/
COPY --from=WHEEL_BUILDER_PY38 /wheels/* /wheels/
COPY --from=WHEEL_BUILDER_PY39 /wheels/* /wheels/

ENV PIP_FIND_LINKS=/wheels
RUN python3 -m pip install pip --upgrade && \
    pip3 install wheel && \
    pip3 install tox devpi_client && \
    pip3 wheel -w /wheels --no-cache-dir wheel
WORKDIR /src
CMD tox --workdir /tmp/tox --recreate