# escape=`
FROM mcr.microsoft.com/windows/servercore:ltsc2019 as choco_builder
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]

ADD ci/docker/chocolatey_package/chocolatey/install_choco.ps1 choco/install_choco.ps1
ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
ARG ChocolateyEnvironmentDebug=false
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
    ./choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_SOURCE ; `
    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
    { `
        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"$env:CHOCOLATEY_SOURCE\" ; `
    }; `
    Remove-Item C:\ProgramData\chocolatey\bin\cpack.exe

COPY ci/docker/chocolatey_package/choco_package_template/pythonscript/ C:/ProgramData/chocolatey/templates/pythonscript/
#===============================
#COPY ci/docker/chocolatey_package/choco_package_template/uiucprescon.getmarc2-0.1.0.dev2-py3-none-any.whl c:/pkg/
#WORKDIR c:/packageme/
#RUN choco new getmarc packageversion=1.0 InstallerFile=dist\uiucprescon.getmarc2-0.1.0.dev2-py3-none-any.whl -t pythonscript
#RUN New-Item -Path "c:\packageme\getmarc\\" -Name "dist" -ItemType "directory" | Out-Null ; `
#    Move-Item -Path "c:\pkg\*"  -Destination "c:\packageme\getmarc\dist\\" | Out-Null
#
#RUN ls c:\packageme\getmarc\ ;  choco pack c:\packageme\getmarc\getmarc.nuspec --outputdirectory c:\packageme\getmarc
#
#FROM mcr.microsoft.com/windows/servercore:ltsc2019
#SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop';"]
#
#ADD ci/docker/chocolatey_package/chocolatey/install_choco.ps1 choco/install_choco.ps1
#ARG CHOCOLATEY_SOURCE=https://chocolatey.org/api/v2
#ARG ChocolateyEnvironmentDebug=false
#RUN Set-ExecutionPolicy Bypass -Scope Process -Force; `
#    ./choco/install_choco.ps1 -packageRepo $env:CHOCOLATEY_SOURCE ; `
#    if( -not ([string]::IsNullOrEmpty($Env:CHOCOLATEY_SOURCE ))) `
#    { `
#        Write-Host "Adding $env:CHOCOLATEY_SOURCE to chocolatey sources" ; `
#        choco source add -n=CHOCOLATEY_SOURCE --priority=1 -s=\"$env:CHOCOLATEY_SOURCE\" ; `
#    }
#COPY --from=choco_builder c:/packageme/getmarc c:/packageme/getmarc/
#WORKDIR c:/packageme/
#RUN cd getmarc; choco install getmarc -y -dv -s  '.;CHOCOLATEY_SOURCE;chocolatey'
#RUN getmarc --help