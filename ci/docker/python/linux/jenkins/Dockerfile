ARG PYTHON_VERSION="3.8"
FROM python:${PYTHON_VERSION} as wheel_builder

ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST

RUN python -m pip install --upgrade pip &&  \
    pip install setuptools && \
    pip install wheel

ADD requirements.txt ci/docker/python/shared/requirements-ci.txt /tmp/

RUN pip wheel --wheel-dir=/wheels  \
        -r /tmp/requirements.txt \
        -r /tmp/requirements-ci.txt && \
    rm -rf  /root/.cache


FROM python:${PYTHON_VERSION} as base_image
RUN apt update && apt install -y libenchant1c2a
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

RUN mkdir -p /.cache/pip && chmod -R 777 /.cache

#USER user
#ENV SONAR_SCANNER_VERSION=4.4.0.2170
#ENV SONAR_SCANNER_HOME=/home/user/.sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux
#RUN curl --create-dirs -sSLo $HOME/.sonar/sonar-scanner.zip \
#        https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip && \
#    unzip -o $HOME/.sonar/sonar-scanner.zip -d $HOME/.sonar/ && \
#    rm $HOME/.sonar/sonar-scanner.zip && \
#    mkdir -p /home/user/.sonar/cache && \
#    chown user:user /home/user/.sonar/cache
#ENV PATH=$SONAR_SCANNER_HOME/bin:$PATH
#ENV SONAR_SCANNER_OPTS="-server"

ENV SONAR_SCANNER_OPTS="-server"
ENV CONAN_NON_INTERACTIVE=1
ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST
ARG PIP_INDEX_URL

#==============================================================================
FROM base_image as SONAR_BUILDER
RUN apt-get update && \
    apt-get install -y unzip
ENV SONAR_SCANNER_VERSION=4.4.0.2170
ARG SONAR_SCANNER_HOME=/opt/sonar/${SONAR_SCANNER_VERSION}-linux
ENV SONAR_USER_HOME=/opt/sonar/.sonar

RUN curl --create-dirs -sSLo /tmp/sonar-scanner.zip \
        https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip && \
    unzip -o /tmp/sonar-scanner.zip -d /opt/sonar/ && \
    rm /tmp/sonar-scanner.zip && \
    mkdir -p $SONAR_USER_HOME/cache && \
    chmod -R 777 "${SONAR_USER_HOME}" &&\
    ln -s /opt/sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    which sonar-scanner

FROM base_image
COPY --from=SONAR_BUILDER /opt/sonar /opt/sonar/

ENV SONAR_SCANNER_VERSION=4.4.0.2170
ARG SONAR_SCANNER_HOME=/opt/sonar/${SONAR_SCANNER_VERSION}-linux
RUN ln -s /opt/sonar/sonar-scanner-${SONAR_SCANNER_VERSION}-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    which sonar-scanner

COPY --from=wheel_builder /wheels /wheels/
ADD requirements.txt ci/docker/python/shared/requirements-ci.txt /tmp/
ENV PIP_FIND_LINKS=/wheels
RUN pip install --no-index --find-links=/wheels \
    -r /tmp/requirements.txt \
    -r /tmp/requirements-ci.txt
