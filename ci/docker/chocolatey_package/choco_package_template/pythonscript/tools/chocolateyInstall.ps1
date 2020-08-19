#function Create-Virtualenv{
#  param(
#    [string]$pythonLocation
#  )
#
#  Write-Host "Creating new Python virtualenv at $pythonLocation"
#}

# Custom value: [[CustomValue]]
$ErrorActionPreference = 'Stop'; # stop on all errors

[[AutomaticPackageNotesInstaller]]
$packageName  = '[[PackageName]]'
$toolsDir     = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$installDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

$fileLocation = Join-Path $toolsDir '[[InstallerFile]]'
$packageSourceUrl =  '[[PackageSourceUrl]]'
#Create-Virtualenv($installDir\venv\Scripts\python.exe)

Write-Host "Creating Python virtualenv at $installDir\venv"
python -m venv $installDir\venv
& "$installDir\venv\Scripts\python.exe" -m pip install pip --upgrade --no-compile
& "$installDir\venv\Scripts\python.exe" -m pip install $fileLocation

$files = get-childitem $installDir -include *.exe -recurse
foreach ($file in $files) {
  #generate an ignore file
  New-Item "$file.ignore" -type file -force | Out-Null
}
Install-BinFile -Name $packageName -Path "$installDir\venv\Scripts\$packageName.exe"
