# escape=`

ARG PYTHON_36_VERSION=3.6.8
ARG PYTHON_37_VERSION=3.7.9
ARG PYTHON_38_VERSION=3.8.5
ARG PYTHON_39_VERSION=3.9.0

ARG FROM_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
FROM ${FROM_IMAGE} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${FROM_IMAGE} as BASE_BUILDER

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
COPY ci/docker/python/shared/chocolatey/install_choco.ps1 C:/choco/install_choco.ps1
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    c://choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_SOURCE ; `
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"$env:CHOCOLATEY_SOURCE\"; `
        choco source remove -n=chocolatey ;`
    }; `
    Write-Host "Disabling Showing Download Progress" ; `
    choco feature disable -n=showDownloadProgress ; `
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe ; `
    Remove-Item -Force -Recurse ${Env:TEMP}\*

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY36
ARG PYTHON_36_VERSION
ARG CHOCOLATEY_SOURCE
RUN choco install -y --stoponfirstfailure --no-progress --verbose python3 --version=${Env:PYTHON_36_VERSION}
SHELL ["cmd", "/S", "/C" ]
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements.txt ci/docker/python/shared/requirements-ci.txt c:/requirements/
RUN pip install --upgrade pip wheel && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements.txt

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY37
ARG PYTHON_37_VERSION
ARG CHOCOLATEY_SOURCE
RUN choco install -y --stoponfirstfailure --no-progress --verbose python3 --version=${Env:PYTHON_37_VERSION}
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt ci/docker/python/shared/requirements-ci.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN pip install --upgrade pip wheel && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements.txt
# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY38
ARG PYTHON_38_VERSION
ARG CHOCOLATEY_SOURCE
RUN choco install -y --stoponfirstfailure --no-progress --verbose python3 --version=${Env:PYTHON_38_VERSION}
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt ci/docker/python/shared/requirements-ci.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN pip install --upgrade pip wheel && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements.txt
# ==============================================================================

# ==============================================================================
FROM BASE_BUILDER as WHEEL_BUilDER_PY39
ARG PYTHON_39_VERSION
ARG CHOCOLATEY_SOURCE
RUN choco install -y --stoponfirstfailure --no-progress --verbose python3 --version=${Env:PYTHON_39_VERSION}
SHELL ["cmd", "/S", "/C" ]
COPY requirements.txt ci/docker/python/shared/requirements-ci.txt c:/requirements/
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN pip install --upgrade pip wheel && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements-ci.txt && `
    pip wheel -w c:\wheels\ --no-cache-dir -r c:/requirements/requirements.txt

# ==============================================================================
FROM BASE_BUILDER
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG PYTHON_36_VERSION
RUN choco install python3 --version ${Env:PYTHON_36_VERSION} -my

ARG PYTHON_37_VERSION
RUN choco install python3 --version ${Env:PYTHON_37_VERSION} -my

ARG PYTHON_38_VERSION
RUN choco install python3 --version ${Env:PYTHON_38_VERSION} -my

ARG PYTHON_39_VERSION
RUN choco install python3 --version ${Env:PYTHON_39_VERSION} -my

COPY --from=WHEEL_BUilDER_PY36 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY37 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY38 c:/wheels/ c:/wheels/
COPY --from=WHEEL_BUilDER_PY39 c:/wheels/ c:/wheels/

ENV PIP_FIND_LINKS=c:\wheels

RUN python -m pip install pip --upgrade ; pip install tox
WORKDIR C:/src
CMD tox --workdir ${Env:TEMP}\tox\ -vv  --recreate