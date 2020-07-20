# escape=`
ARG PYTHON_VERSION="3.8"
FROM python:${PYTHON_VERSION} as wheel_builder

ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST

RUN python -m pip install pip --upgrade ; `
    python -m pip install wheel ; `
    python -m pip install setuptools --upgrade

ADD requirements.txt ci/docker/python/shared/requirements-ci.txt c:/temp/

RUN pip wheel --wheel-dir=c:\temp\wheels `
                        -r c:/temp/requirements.txt `
                        -r c:/temp/requirements-ci.txt

FROM python:${PYTHON_VERSION}

RUN certutil -generateSSTFromWU roots.sst ; `
    certutil -addstore -f root roots.sst ; `
    del roots.sst


RUN python -m pip install pip --upgrade ; `
    python -m pip install wheel ; `
    python -m pip install setuptools --upgrade

COPY --from=wheel_builder c:\temp\wheels c:/wheels/
ADD requirements.txt  ci/docker/python/shared/requirements-ci.txt c:/temp/

RUN python -m pip install --find-links c:\wheels\ `
        -r c:\temp\requirements.txt `
        -r c:\temp\requirements-ci.txt

ENV PIP_FIND_LINKS=c:\wheels\