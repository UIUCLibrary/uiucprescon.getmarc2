SUPPORTED_MAC_VERSIONS = ['3.8', '3.9', '3.10']
SUPPORTED_LINUX_VERSIONS = ['3.7', '3.8', '3.9', '3.10']
SUPPORTED_WINDOWS_VERSIONS = ['3.7', '3.8', '3.9', '3.10']


def getDevpiConfig() {
    node(){
        configFileProvider([configFile(fileId: 'devpi_config', variable: 'CONFIG_FILE')]) {
            def configProperties = readProperties(file: CONFIG_FILE)
            configProperties.stagingIndex = {
                if (env.TAG_NAME?.trim()){
                    return 'tag_staging'
                } else{
                    return "${env.BRANCH_NAME}_staging"
                }
            }()
            return configProperties
        }
    }
}

def DEVPI_CONFIG = getDevpiConfig()

def sanitize_chocolatey_version(version){
    script{
        def dot_to_slash_pattern = '(?<=\\d)\\.?(?=(dev|b|a|rc)(\\d)?)'

        def dashed_version = version.replaceFirst(dot_to_slash_pattern, '-')

        def beta_pattern = "(?<=\\d(\\.?))b((?=\\d)?)"
        if(dashed_version.matches(beta_pattern)){
            return dashed_version.replaceFirst(beta_pattern, 'beta')
        }

        def alpha_pattern = "(?<=\\d(\\.?))a((?=\\d)?)"
        if(dashed_version.matches(alpha_pattern)){
            return dashed_version.replaceFirst(alpha_pattern, 'alpha')
        }
        return dashed_version
        return new_version
    }
}
def get_sonarqube_unresolved_issues(report_task_file){
    script{
        if (! fileExists(report_task_file)){
            error "File not found ${report_task_file}"
        }
        def props = readProperties  file: report_task_file
        def response = httpRequest url : props['serverUrl'] + "/api/issues/search?componentKeys=" + props['projectKey'] + "&resolved=no"
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}

def get_mac_devpi_stages(packageName, packageVersion, devpiServer, devpiCredentials, stagingIndex, supportedPythonVersions){
    def devpi
     node('') {
        checkout scm
        devpi = load('ci/jenkins/scripts/devpi.groovy')
     }
    def macPackages = [:]
    supportedPythonVersions.each{pythonVersion ->
        macPackages["MacOS x86_64 - Python ${pythonVersion}: wheel"] = {
            withEnv([
                'PATH+EXTRA=./venv/bin'
            ]) {
                devpi.testDevpiPackage(
                    agent: [
                        label: "mac && python${pythonVersion} && x86 && devpi-access"
                    ],
                    devpi: [
                        index: stagingIndex,
                        server: devpiServer,
                        credentialsId: devpiCredentials,
                        devpiExec: 'venv/bin/devpi'
                    ],
                    package:[
                        name: packageName,
                        version: packageVersion,
                        selector: "whl"
                    ],
                    test:[
                        setup: {
                            checkout scm
                            sh(
                                label: 'Installing Devpi client',
                                script: '''python3 -m venv venv
                                           . ./venv/bin/activate
                                            python -m pip install pip --upgrade
                                            python -m pip install devpi_client  -r requirements/requirements_tox.txt
                                            '''
                            )
                        },
                        toxEnv: "py${pythonVersion}".replace('.',''),
                        teardown: {
                            sh( label: 'Remove Devpi client', script: 'rm -r venv')
                        }
                    ]
                )
            }
        }
        macPackages["MacOS m1 - Python ${pythonVersion}: wheel"] = {
            withEnv(['PATH+EXTRA=./venv/bin']) {
                devpi.testDevpiPackage(
                    agent: [
                        label: "mac && python${pythonVersion} && m1 && devpi-access"
                    ],
                    devpi: [
                        index: stagingIndex,
                        server: devpiServer,
                        credentialsId: devpiCredentials,
                        devpiExec: 'venv/bin/devpi'
                    ],
                    package:[
                        name: packageName,
                        version: packageVersion,
                        selector: 'whl'
                    ],
                    test:[
                        setup: {
                           checkout scm
                           sh(
                               label: 'Installing Devpi client',
                               script: '''python3 -m venv venv
                                          . ./venv/bin/activate
                                           python -m pip install pip --upgrade
                                           python -m pip install devpi_client  -r requirements/requirements_tox.txt
                                           '''
                           )
                        },
                        toxEnv: "py${pythonVersion}".replace('.',''),
                        teardown: {
                            sh( label: 'Remove Devpi client', script: 'rm -r venv')
                        }
                    ]
                )
            }
        }
        macPackages["MacOS x86_64 - Python ${pythonVersion}: sdist"]= {
            withEnv([
                'PATH+EXTRA=./venv/bin'

            ]) {
                devpi.testDevpiPackage(
                    agent: [
                        label: "mac && python${pythonVersion} && x86 && devpi-access"
                    ],
                    devpi: [
                        index: stagingIndex,
                        server: devpiServer,
                        credentialsId: devpiCredentials,
                        devpiExec: 'venv/bin/devpi'
                    ],
                    package:[
                        name: packageName,
                        version: packageVersion,
                        selector: 'tar.gz'
                    ],
                    test:[
                        setup: {
                            checkout scm
                            sh(
                                label: 'Installing Devpi client',
                                script: '''python3 -m venv venv
                                            venv/bin/python -m pip install pip --upgrade
                                            venv/bin/python -m pip install devpi_client -r requirements/requirements_tox.txt
                                            '''
                            )
                        },
                        toxEnv: "py${pythonVersion}".replace('.',''),
                        teardown: {
                            sh( label: 'Remove Devpi client', script: 'rm -r venv')
                        }
                    ]
                )
            }
        }
        macPackages["MacOS m1 - Python ${pythonVersion}: sdist"]= {
            withEnv(['PATH+EXTRA=./venv/bin']) {
                devpi.testDevpiPackage(
                    agent: [
                        label: "mac && python${pythonVersion} && m1 && devpi-access"
                    ],
                    devpi: [
                        index: stagingIndex,
                        server: devpiServer,
                        credentialsId: devpiCredentials,
                        devpiExec: 'venv/bin/devpi'
                    ],
                    package:[
                        name: packageName,
                        version: packageVersion,
                        selector: 'tar.gz'
                    ],
                    test:[
                        setup: {
                            checkout scm
                            sh(
                                label:'Installing Devpi client',
                                script: '''python3 -m venv venv
                                            venv/bin/python -m pip install pip --upgrade
                                            venv/bin/python -m pip install devpi_client -r requirements/requirements_tox.txt
                                            '''
                            )
                        },
                        toxEnv: "py${pythonVersion}".replace('.',''),
                        teardown: {
                            sh( label: 'Remove Devpi client', script: 'rm -r venv')
                        }
                    ]
                )
            }
        }
    }
    return macPackages
}

def test_packages(){
    script{
        def packages
        node(){
            checkout scm
            packages = load 'ci/jenkins/scripts/packaging.groovy'
        }
        def linuxTestStages = [:]
        SUPPORTED_LINUX_VERSIONS.each{ pythonVersion ->
            linuxTestStages["Linux - Python ${pythonVersion}: wheel"] = {
                packages.testPkg2(
                    agent: [
                        dockerfile: [
                            label: 'linux && docker && x86',
                            filename: 'ci/docker/python/linux/tox/Dockerfile',
                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                        ]
                    ],
                    testSetup: {
                        checkout scm
                        unstash 'PYTHON_PACKAGES'
                    },
                    testCommand: {
                        findFiles(glob: 'dist/*.whl').each{
                            timeout(5){
                                sh(
                                    label: 'Running Tox',
                                    script: "tox --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}"
                                    )
                            }
                        }
                    },
                    post:[
                        cleanup: {
                            cleanWs(
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                    ],
                                notFailBuild: true,
                                deleteDirs: true
                            )
                        },
                        success: {
                            archiveArtifacts artifacts: 'dist/*.whl'
                        },
                    ]
                )
            }
            linuxTestStages["Linux - Python ${pythonVersion}: sdist"] = {
                packages.testPkg2(
                    agent: [
                        dockerfile: [
                            label: 'linux && docker && x86',
                            filename: 'ci/docker/python/linux/tox/Dockerfile',
                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                        ]
                    ],
                    testSetup: {
                        checkout scm
                        unstash 'PYTHON_PACKAGES'
                    },
                    testCommand: {
                        findFiles(glob: 'dist/*.tar.gz').each{
                            sh(
                                label: 'Running Tox',
                                script: "tox --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}"
                                )
                        }
                    },
                    post:[
                        cleanup: {
                            cleanWs(
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                    ],
                                notFailBuild: true,
                                deleteDirs: true
                            )
                        },
                    ]
                )
            }
        }
        def macTestStages = [:]
        SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
            macTestStages["MacOS - Python ${pythonVersion}: wheel"] = {
                packages.testPkg2(
                    agent: [
                        label: "mac && python${pythonVersion}",
                    ],
                    testSetup: {
                        checkout scm
                        unstash 'PYTHON_PACKAGES'
                    },
                    testCommand: {
                        findFiles(glob: 'dist/*.whl').each{
                            sh(label: 'Running Tox',
                               script: """python${pythonVersion} -m venv venv
                               . ./venv/bin/activate
                               python -m pip install --upgrade pip
                               pip install devpi_client -r requirements/requirements_tox.txt
                               tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
                            )
                        }

                    },
                    post:[
                        cleanup: {
                            cleanWs(
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: 'venv/', type: 'INCLUDE'],
                                        [pattern: '.tox/', type: 'INCLUDE'],
                                    ],
                                notFailBuild: true,
                                deleteDirs: true
                            )
                        },
                        success: {
                             archiveArtifacts artifacts: 'dist/*.whl'
                        }
                    ]
                )
            }
            macTestStages["MacOS - Python ${pythonVersion}: sdist"] = {
                packages.testPkg2(
                    agent: [
                        label: "mac && python${pythonVersion}",
                    ],
                    testSetup: {
                        checkout scm
                        unstash 'PYTHON_PACKAGES'
                    },
                    testCommand: {
                        findFiles(glob: 'dist/*.tar.gz').each{
                            sh(label: 'Running Tox',
                               script: """python${pythonVersion} -m venv venv
                                          . ./venv/bin/activate
                                          python -m pip install --upgrade pip
                                          pip install devpi_client -r requirements/requirements_tox.txt
                                          tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                       """
                            )
                        }

                    },
                    post:[
                        cleanup: {
                            cleanWs(
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: 'venv/', type: 'INCLUDE'],
                                        [pattern: '.tox/', type: 'INCLUDE'],
                                    ],
                                notFailBuild: true,
                                deleteDirs: true
                            )
                        },
                    ]
                )
            }
        }
        def windowsTestStages = [:]
        SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
            windowsTestStages["Windows - Python ${pythonVersion}: wheel"] = {
                packages.testPkg2(
                    agent: [
                        dockerfile: [
                            label: 'windows && docker && x86',
                            filename: 'ci/docker/python/windows/tox/Dockerfile',
                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                        ]
                    ],
                    dockerImageName: "${currentBuild.fullProjectName}_test".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                    testSetup: {
                         checkout scm
                         unstash 'PYTHON_PACKAGES'
                    },
                    testCommand: {
                         findFiles(glob: 'dist/*.whl').each{
                             powershell(label: 'Running Tox', script: "tox --installpkg ${it.path} --workdir \$env:TEMP\\tox  -e py${pythonVersion.replace('.', '')}")
                         }

                    },
                    post:[
                        cleanup: {
                            cleanWs(
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                    ],
                                notFailBuild: true,
                                deleteDirs: true
                            )
                        },
                        success: {
                            archiveArtifacts artifacts: 'dist/*.whl'
                        }
                    ]
                )
            }
            windowsTestStages["Windows - Python ${pythonVersion}: sdist"] = {
                packages.testPkg2(
                    agent: [
                        dockerfile: [
                            label: 'windows && docker && x86',
                            filename: 'ci/docker/python/windows/tox/Dockerfile',
                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                        ]
                    ],
                    dockerImageName: "${currentBuild.fullProjectName}_test".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                    testSetup: {
                        checkout scm
                        unstash 'PYTHON_PACKAGES'
                    },
                    testCommand: {
                        findFiles(glob: 'dist/*.tar.gz').each{
                            bat(label: 'Running Tox', script: "tox --workdir %TEMP%\\tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')} -v")
                        }
                    },
                    post:[
                        cleanup: {
                            cleanWs(
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                    ],
                                notFailBuild: true,
                                deleteDirs: true
                            )
                        },
                    ]
                )
            }
        }
        def testingStages = windowsTestStages + linuxTestStages
        if(params.TEST_PACKAGES_ON_MAC == true){
            testingStages = testingStages + macTestStages
        }
        parallel(testingStages)
    }
}
def startup(){
    stage('Getting Distribution Info'){
        node('linux && docker') {
            ws{
                checkout scm
                try{
                    docker.image('python').inside {
                        timeout(2){
                            withEnv(['PIP_NO_CACHE_DIR=off']) {
                                sh(
                                   label: 'Running setup.py with dist_info',
                                   script: '''python --version
                                              python setup.py dist_info
                                           '''
                                )
                            }
                            stash includes: '*.dist-info/**', name: 'DIST-INFO'
                            archiveArtifacts artifacts: '*.dist-info/**'
                        }
                    }
                } finally{
                    cleanWs(
                        deleteDirs: true,
                        patterns: [
                            [pattern: '*.dist-info/', type: 'INCLUDE'],
                            [pattern: '**/__pycache__', type: 'INCLUDE'],
                        ]
                    )
                }
            }
        }
    }
}

def get_props(){
    stage('Reading Package Metadata'){
        node() {
            try{
                unstash 'DIST-INFO'
                def metadataFile = findFiles(excludes: '', glob: '*.dist-info/METADATA')[0]
                def package_metadata = readProperties interpolate: true, file: metadataFile.path
                echo """Metadata:

    Name      ${package_metadata.Name}
    Version   ${package_metadata.Version}
    """
                return package_metadata
            } finally {
                cleanWs(
                    patterns: [
                            [pattern: '*.dist-info/**', type: 'INCLUDE'],
                        ],
                    notFailBuild: true,
                    deleteDirs: true
                )
            }
        }
    }
}

startup()
props = get_props()

pipeline {
    agent none
    parameters {
        booleanParam(name: 'RUN_CHECKS', defaultValue: true, description: 'Run checks on code')
        booleanParam(name: 'TEST_RUN_TOX', defaultValue: false, description: 'Run Tox Tests')
        booleanParam(name: 'USE_SONARQUBE', defaultValue: true, description: 'Send data test data to SonarQube')
        booleanParam(name: 'BUILD_PACKAGES', defaultValue: false, description: 'Build Python packages')
        booleanParam(name: 'BUILD_CHOCOLATEY_PACKAGE', defaultValue: false, description: 'Build package for chocolatey package manager')
        booleanParam(name: 'TEST_PACKAGES', defaultValue: true, description: 'Test Python packages by installing them and running tests on the installed package')
        booleanParam(name: 'TEST_PACKAGES_ON_MAC', defaultValue: false, description: 'Test Python packages on Mac')
        booleanParam(name: 'DEPLOY_DEVPI', defaultValue: false, description: "Deploy to devpi on http://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: 'DEPLOY_DEVPI_PRODUCTION', defaultValue: false, description: "Deploy to production devpi on https://devpi.library.illinois.edu/production/release. Master branch Only")
        booleanParam(name: 'DEPLOY_CHOCOLATEY', defaultValue: false, description: 'Deploy to Chocolatey repository')
        booleanParam(name: 'DEPLOY_DOCS', defaultValue: false, description: '')
    }
    options {
        timeout(time: 1, unit: 'DAYS')
    }
    stages {
        stage('Building and Testing'){
            when{
                anyOf{
                    equals expected: true, actual: params.RUN_CHECKS
                    equals expected: true, actual: params.TEST_RUN_TOX
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DOCS
                }
            }
            stages{
                stage('Sphinx Documentation'){
                    agent{
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker && x86'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                        }
                    }
                    when{
                        anyOf{
                            equals expected: true, actual: params.RUN_CHECKS
                            equals expected: true, actual: params.DEPLOY_DEVPI
                            equals expected: true, actual: params.DEPLOY_DOCS
                        }
                        beforeAgent true
                    }
                    steps {
                        sh(
                            label: 'Building docs',
                            script: '''mkdir -p logs
                                       python -m sphinx docs build/docs/html -d build/docs/.doctrees -w logs/build_sphinx.log
                                    '''
                        )
                    }
                    post{
                        always {
                            recordIssues(tools: [sphinxBuild(pattern: 'logs/build_sphinx.log')])
                        }
                        success{
                            publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            script{
                                zip archive: true, dir: 'build/docs/html', glob: '', zipFile: "dist/${props.Name}-${props.Version}.doc.zip"
                                stash includes: "dist/*.doc.zip,build/docs/html/**", name: 'DOCS_ARCHIVE'
                            }

                        }
                        cleanup{
                            cleanWs(
                                patterns: [
                                    [pattern: 'logs/', type: 'INCLUDE'],
                                    [pattern: 'build/docs/', type: 'INCLUDE'],
                                    [pattern: 'dist/', type: 'INCLUDE']
                                ],
                                deleteDirs: true
                            )
                        }
                    }
                }
                stage('Checks') {
                    stages{
                        stage('Check Code') {
                            when{
                                equals expected: true, actual: params.RUN_CHECKS
                            }
                            agent {
                                dockerfile {
                                    filename 'ci/docker/python/linux/jenkins/Dockerfile'
                                    label 'linux && docker && x86'
                                    additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                                    args '--mount source=sonar-cache-uiucprescon-getmarc2,target=/opt/sonar/.sonar/cache'
                                }
                            }
                            stages{
                                stage('Configuring Testing Environment'){
                                    steps{
                                        sh(
                                            label: 'Creating logging and report directories',
                                            script: 'mkdir -p logs'
                                        )
                                    }
                                }
                                stage('Running Tests'){
                                    parallel {
                                        stage('PyTest'){
                                            steps{
                                                sh "coverage run --parallel-mode --source uiucprescon -m pytest --junitxml=reports/pytest/junit-pytest.xml "
                                            }
                                            post {
                                                always {
                                                    junit 'reports/pytest/junit-pytest.xml'
                                                }
                                            }
                                        }
                                        stage('Doctest'){
                                            steps {
                                                sh(
                                                    label:'Running doctest',
                                                    script: '''mkdir -p reports/doctests
                                                               coverage run --parallel-mode --source uiucprescon -m sphinx -b doctest -d build/docs/doctrees docs reports/doctest -w logs/doctest.log
                                                               '''
                                                )
                                            }
                                            post{
                                                always {
                                                    recordIssues(tools: [sphinxBuild(name: 'Sphinx Doctest', pattern: 'logs/doctest.log', id: 'doctest')])
                                                }

                                            }
                                        }
                                        stage('pyDocStyle'){
                                            steps{
                                                catchError(buildResult: 'SUCCESS', message: 'Did not pass all pyDocStyle tests', stageResult: 'UNSTABLE') {
                                                    sh(
                                                        label: 'Run pydocstyle',
                                                        script: '''mkdir -p reports
                                                                   pydocstyle uiucprescon > reports/pydocstyle-report.txt
                                                                   '''
                                                    )
                                                }
                                            }
                                            post {
                                                always{
                                                    recordIssues(tools: [pyDocStyle(pattern: 'reports/pydocstyle-report.txt')])
                                                }
                                            }
                                        }
                                        stage('Task Scanner'){
                                            steps{
                                                recordIssues(tools: [taskScanner(highTags: 'FIXME', includePattern: 'uiucprescon/**/*.py', normalTags: 'TODO')])
                                            }
                                        }
                                        stage('MyPy') {
                                            steps{
                                                catchError(buildResult: 'SUCCESS', message: 'mypy found issues', stageResult: 'UNSTABLE') {
                                                    tee('logs/mypy.log'){
                                                        sh(
                                                            label: 'Run mypy',
                                                            script: '''mkdir -p reports/mypy/html
                                                                       mypy -p uiucprescon.getmarc2 --namespace-packages --html-report reports/mypy/html/
                                                                       '''
                                                        )
                                                    }
                                                }
                                            }
                                            post {
                                                always {
                                                    recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                                }
                                            }
                                        }
                                        stage('Bandit') {
                                            steps{
                                                catchError(buildResult: 'SUCCESS', message: 'Bandit found issues', stageResult: 'UNSTABLE') {
                                                    sh(
                                                        label: 'Running bandit',
                                                        script: "bandit --format json --output reports/bandit-report.json --recursive uiucprescon || bandit -f html --recursive uiucprescon --output reports/bandit-report.html"
                                                    )
                                                }
                                            }
                                            post {
                                                unstable{
                                                    script{
                                                        if(fileExists('reports/bandit-report.html')){
                                                            publishHTML([
                                                                allowMissing: false,
                                                                alwaysLinkToLastBuild: false,
                                                                keepAll: false,
                                                                reportDir: 'reports',
                                                                reportFiles: 'bandit-report.html',
                                                                reportName: 'Bandit Report', reportTitles: ''
                                                                ])
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        stage('PyLint') {
                                            steps{
                                                catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                                    tee('reports/pylint.txt'){
                                                        sh(
                                                            script: 'pylint uiucprescon --init-hook="import sys; sys.path.insert(0, '.')" -r n --persistent=n --verbose --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"',
                                                            label: 'Running pylint'
                                                        )
                                                    }
                                                }
                                                sh(
                                                    script: '''pylint uiucprescon --init-hook="import sys; sys.path.insert(0, '.')" -r n --persistent=n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt''',
                                                    label: 'Running pylint for sonarqube',
                                                    returnStatus: true
                                                )
                                            }
                                            post{
                                                always{
                                                    recordIssues(tools: [pyLint(pattern: 'reports/pylint.txt')])
                                                }
                                            }
                                        }
                                        stage('Flake8') {
                                            steps{
                                                catchError(buildResult: 'SUCCESS', message: 'Flake8 found issues', stageResult: 'UNSTABLE') {
                                                    sh(label: 'Running Flake8',
                                                       script: '''mkdir -p logs
                                                                  flake8 uiucprescon --tee --output-file=logs/flake8.log
                                                               '''
                                                       )
                                                }
                                            }
                                            post {
                                                always {
                                                    recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                                }
                                            }
                                        }
                                    }
                                    post{
                                        always{
                                            sh(
                                                label: 'Combine Coverage data and generate a report',
                                                script: '''mkdir -p reports/coverage
                                                          coverage combine && coverage xml -o reports/coverage.xml
                                                          '''
                                            )
                                            publishCoverage adapters: [
                                                            coberturaAdapter('reports/coverage.xml')
                                                            ],
                                                        sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
                                        }
                                    }
                                }
                                stage('Send to Sonarcloud for Analysis'){
                                    options{
                                        lock('uiucprescon.getmarc2-sonarscanner')
                                    }
                                    when{
                                        equals expected: true, actual: params.USE_SONARQUBE
                                        beforeAgent true
                                        beforeOptions true
                                    }
                                    steps{
                                        script{
                                            withSonarQubeEnv(installationName:'sonarcloud', credentialsId: 'sonarcloud-uiucprescon.getmarc2') {
                                                if (env.CHANGE_ID){
                                                    sh(
                                                        label: 'Running Sonar Scanner',
                                                        script:"sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
                                                        )
                                                } else {
                                                    sh(
                                                        label: 'Running Sonar Scanner',
                                                        script: "sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME}"
                                                        )
                                                }
                                            }
                                            timeout(time: 1, unit: 'HOURS') {
                                                def sonarqube_result = waitForQualityGate(abortPipeline: false)
                                                if (sonarqube_result.status != 'OK') {
                                                    unstable "SonarQube quality gate: ${sonarqube_result.status}"
                                                }
                                                def outstandingIssues = get_sonarqube_unresolved_issues('.scannerwork/report-task.txt')
                                                writeJSON file: 'reports/sonar-report.json', json: outstandingIssues
                                            }
                                        }
                                    }
                                    post {
                                        always{
                                            script{
                                                if(fileExists('reports/sonar-report.json')){
                                                    stash includes: 'reports/sonar-report.json', name: 'SONAR_REPORT'
                                                    archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/sonar-report.json'
                                                    recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            post{
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: 'dist/', type: 'INCLUDE'],
                                            [pattern: 'build/', type: 'INCLUDE'],
                                            [pattern: '.pytest_cache/', type: 'INCLUDE'],
                                            [pattern: '.mypy_cache/', type: 'INCLUDE'],
                                            [pattern: '.tox/', type: 'INCLUDE'],
                                            [pattern: 'uiucprescon1.stats', type: 'INCLUDE'],
                                            [pattern: 'uiucprescon.getmarc2.egg-info/', type: 'INCLUDE'],
                                            [pattern: 'uiucprescon.getmarc2.dist-info/', type: 'INCLUDE'],
                                            [pattern: 'reports/', type: 'INCLUDE'],
                                            [pattern: 'logs/', type: 'INCLUDE'],
                                            [pattern: '.scannerwork/', type: 'INCLUDE'],
                                            ]
                                    )
                                }
                            }
                        }
                        stage('Tox') {
                            when{
                                equals expected: true, actual: params.TEST_RUN_TOX
                            }
                            parallel{
                                stage('Linux') {
                                    steps {
                                        script{
                                            def tox = fileLoader.fromGit(
                                                'tox',
                                                'https://github.com/UIUCLibrary/jenkins_helper_scripts.git',
                                                '4',
                                                null,
                                                ''
                                            )
                                            def jobs = tox.getToxTestsParallel(
                                                                            envNamePrefix: 'Tox Linux',
                                                                            label: 'linux && docker',
                                                                            dockerfile: 'ci/docker/python/linux/tox/Dockerfile',
                                                                            dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                                            dockerRunArgs: "-v pipcache_uiucprescon_getmarc2:/.cache/pip"
                                                                        )
                                            parallel(jobs)
                                        }
                                    }
                                }
                                stage('Windows') {
                                    steps {
                                        script{
                                            def tox = fileLoader.fromGit(
                                                'tox',
                                                'https://github.com/UIUCLibrary/jenkins_helper_scripts.git',
                                                '4',
                                                null,
                                                ''
                                            )
                                             parallel(
                                                tox.getToxTestsParallel(
                                                    envNamePrefix: 'Tox Windows',
                                                    label: 'windows && docker && x86',
                                                    dockerfile: 'ci/docker/python/windows/tox/Dockerfile',
                                                    dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE',
                                                    dockerRunArgs: "-v pipcache_uiucprescon_getmarc2:c:/users/containeradministrator/appdata/local/pip"
                                                )
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Distribution Packages'){
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                    equals expected: true, actual: params.BUILD_CHOCOLATEY_PACKAGE
                    equals expected: true, actual: params.TEST_PACKAGES_ON_MAC
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                    equals expected: true, actual: params.DEPLOY_CHOCOLATEY
                }
                beforeAgent true
            }
            stages{
                stage('Creating Python Packages') {
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker && x86'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                        }
                    }
                    steps {
                        sh(label: 'Building python distribution packages', script: 'python -m build')
                    }
                    post {
                        always{
                            stash includes: 'dist/*.*', name: 'PYTHON_PACKAGES'
                        }
                        success {
                            archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz,dist/*.zip", fingerprint: true
                        }
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'dist/', type: 'INCLUDE'],
                                    [pattern: 'build/', type: 'INCLUDE'],
                                    [pattern: 'uiucprescon.getmarc2.egg-info/', type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
                stage('Testing'){
                    when{
                        equals expected: true, actual: params.TEST_PACKAGES
                    }
                    steps{
                        test_packages()
                    }
                }
                stage('Chocolatey'){
                    when{
                        anyOf{
                            equals expected: true, actual: params.DEPLOY_CHOCOLATEY
                            equals expected: true, actual: params.BUILD_CHOCOLATEY_PACKAGE
                        }
                        beforeInput true
                    }
                    stages{
                        stage('Package for Chocolatey'){
                            agent {
                                dockerfile {
                                    filename 'ci/docker/chocolatey_package/Dockerfile'
                                    label 'windows && docker && x86'
                                    additionalBuildArgs '--build-arg CHOCOLATEY_SOURCE'
                                  }
                            }
                            steps{
                                script {
                                    unstash 'PYTHON_PACKAGES'
                                    findFiles(glob: 'dist/*.whl').each{
                                        def sanitized_packageversion=sanitize_chocolatey_version(props.Version)
                                        powershell(
                                            label: 'Configuring new package for Chocolatey',
                                            script: """\$ErrorActionPreference = 'Stop'; # stop on all errors
                                                       choco new getmarc packageversion=${sanitized_packageversion} PythonSummary="${props.Summary}" InstallerFile=${it.path} MaintainerName="${props.Maintainer}" -t pythonscript --outputdirectory packages
                                                       New-Item -ItemType File -Path ".\\packages\\getmarc\\${it.path}" -Force | Out-Null
                                                       Move-Item -Path "${it.path}"  -Destination "./packages/getmarc/${it.path}"  -Force | Out-Null
                                                       choco pack .\\packages\\getmarc\\getmarc.nuspec --outputdirectory .\\packages
                                                       """
                                        )
                                    }
                                }
                            }
                            post{
                                always{
                                    archiveArtifacts artifacts: 'packages/**/*.nuspec'
                                    stash includes: 'packages/*.nupkg', name: 'CHOCOLATEY_PACKAGE'
                                }
                            }
                        }
                        stage('Testing Chocolatey Package'){
                            agent {
                                dockerfile {
                                    filename 'ci/docker/chocolatey_package/Dockerfile'
                                    label 'windows && docker && x86'
                                    additionalBuildArgs '--build-arg CHOCOLATEY_SOURCE'
                                  }
                            }
                            steps{
                                unstash 'CHOCOLATEY_PACKAGE'
                                script{
                                    def sanitized_packageversion=sanitize_chocolatey_version(props.Version)
                                    powershell(
                                        label: 'Installing Chocolatey Package',
                                        script:"""\$ErrorActionPreference = 'Stop'; # stop on all errors
                                                  choco install getmarc -y -dv  --version=${sanitized_packageversion} -s './packages/;CHOCOLATEY_SOURCE;chocolatey' --no-progress
                                                  """
                                    )
                                }
                                bat 'getmarc --help'

                            }
                            post{
                                success{
                                    archiveArtifacts artifacts: 'packages/*.nupkg', fingerprint: true
                                }
                                cleanup{
                                    cleanWs(
                                        notFailBuild: true,
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: 'packages/', type: 'INCLUDE'],
                                            [pattern: 'uiucprescon.getmarc2.dist-info/', type: 'INCLUDE'],
                                        ]
                                    )
                                }
                                failure{
                                    powershell('Get-ChildItem -Path C:\\ProgramData\\chocolatey\\logs -Recurse -Include chocolatey.log | Copy-Item -Destination $ENV:WORKSPACE')
                                    archiveArtifacts artifacts: 'chocolatey.log', allowEmptyArchive: true
                                    echo 'Check chocolatey.log for more details on failure'
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Deploy'){
            stages{
                stage('Devpi'){
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI
                            anyOf {
                                equals expected: 'master', actual: env.BRANCH_NAME
                                equals expected: 'dev', actual: env.BRANCH_NAME
                                tag '*'
                            }
                        }
                        beforeAgent true
                        beforeOptions true
                    }
                    agent none
                    options{
                        lock('uiucprescon.getmarc2-devpi')
                    }
                    stages{
                        stage('Deploy to Devpi Staging') {
                            agent {
                                dockerfile {
                                    filename 'ci/docker/python/linux/jenkins/Dockerfile'
                                    label 'linux && docker && devpi-access'
                                    additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                                }
                            }
                            steps {
                                unstash 'PYTHON_PACKAGES'
                                unstash 'DOCS_ARCHIVE'
                                script{
                                    def devpi = load('ci/jenkins/scripts/devpi.groovy')
                                    devpi.upload(
                                        server: DEVPI_CONFIG.server,
                                        credentialsId: DEVPI_CONFIG.credentialsId,
                                        index: DEVPI_CONFIG.stagingIndex,
                                        clientDir: './devpi'
                                    )
                                }
                            }
                        }
                        stage('Test DevPi Package') {
                            steps{
                                script{
                                    def devpi
                                    node(){
                                        checkout scm
                                        devpi = load('ci/jenkins/scripts/devpi.groovy')
                                    }
                                    def macPackages = get_mac_devpi_stages(props.Name, props.Version, DEVPI_CONFIG.server, DEVPI_CONFIG.credentialsId, DEVPI_CONFIG.stagingIndex, SUPPORTED_MAC_VERSIONS)
                                    linuxPackages = [:]
                                    SUPPORTED_LINUX_VERSIONS.each{pythonVersion ->
                                        linuxPackages["Test Python ${pythonVersion}: sdist Linux"] = {
                                            devpi.testDevpiPackage(
                                                agent: [
                                                    dockerfile: [
                                                        filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                        additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                        label: 'linux && docker && x86 && devpi-access'
                                                    ]
                                                ],
                                                retryTimes: 3,
                                                devpi: [
                                                    index: DEVPI_CONFIG.stagingIndex,
                                                    server: DEVPI_CONFIG.server,
                                                    credentialsId: DEVPI_CONFIG.credentialsId,
                                                ],
                                                package:[
                                                    name: props.Name,
                                                    version: props.Version,
                                                    selector: 'tar.gz'
                                                ],
                                                test:[
                                                    toxEnv: "py${pythonVersion}".replace('.',''),
                                                ]
                                            )
                                        }
                                        linuxPackages["Test Python ${pythonVersion}: wheel Linux"] = {
                                            devpi.testDevpiPackage(
                                                agent: [
                                                    dockerfile: [
                                                        filename: 'ci/docker/python/linux/tox/Dockerfile',
                                                        additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                        label: 'linux && docker && x86 && devpi-access'
                                                    ]
                                                ],
                                                retryTimes: 3,
                                                devpi: [
                                                    index: DEVPI_CONFIG.stagingIndex,
                                                    server: DEVPI_CONFIG.server,
                                                    credentialsId: DEVPI_CONFIG.credentialsId,
                                                ],
                                                package:[
                                                    name: props.Name,
                                                    version: props.Version,
                                                    selector: 'whl'
                                                ],
                                                test:[
                                                    toxEnv: "py${pythonVersion}".replace('.',''),
                                                ]
                                            )
                                        }
                                    }
                                    def windowsPackages = [:]
                                    SUPPORTED_WINDOWS_VERSIONS.each{pythonVersion ->
                                        windowsPackages["Test Python ${pythonVersion}: sdist Windows"] = {
                                            devpi.testDevpiPackage(
                                                agent: [
                                                    dockerfile: [
                                                        filename: 'ci/docker/python/windows/tox/Dockerfile',
                                                        additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE',
                                                        label: 'windows && docker && x86 && devpi-access'
                                                    ]
                                                ],
                                                retryTimes: 3,
                                                devpi: [
                                                    index: DEVPI_CONFIG.stagingIndex,
                                                    server: DEVPI_CONFIG.server,
                                                    credentialsId: DEVPI_CONFIG.credentialsId,
                                                ],
                                                package:[
                                                    name: props.Name,
                                                    version: props.Version,
                                                    selector: 'tar.gz'
                                                ],
                                                test:[
                                                    toxEnv: "py${pythonVersion}".replace('.',''),
                                                    teardown: {
                                                        bat('python -m pip list')
                                                    }
                                                ],
                                            )
                                        }
                                        windowsPackages["Test Python ${pythonVersion}: wheel Windows"] = {
                                            devpi.testDevpiPackage(
                                                agent: [
                                                    dockerfile: [
                                                        filename: 'ci/docker/python/windows/tox/Dockerfile',
                                                        additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE',
                                                        label: 'windows && docker && x86 && devpi-access'
                                                    ]
                                                ],
                                                retryTimes: 3,
                                                devpi: [
                                                    index: DEVPI_CONFIG.stagingIndex,
                                                    server: DEVPI_CONFIG.server,
                                                    credentialsId: DEVPI_CONFIG.credentialsId,
                                                ],
                                                package:[
                                                    name: props.Name,
                                                    version: props.Version,
                                                    selector: 'whl'
                                                ],
                                                test:[
                                                    toxEnv: "py${pythonVersion}".replace('.',''),
                                                    teardown: {
                                                        bat('python -m pip list')
                                                    }
                                                ],
                                            )
                                        }
                                    }
                                    parallel(macPackages + windowsPackages + linuxPackages)
                                }
                            }
                        }
                        stage('Deploy to DevPi Production') {
                            when {
                                allOf{
                                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                                    anyOf {
                                        branch 'master'
                                        tag '*'
                                    }
                                }
                                beforeInput true
                            }
                            options{
                                  timeout(time: 1, unit: 'DAYS')
                            }
                            input {
                              message 'Release to DevPi Production? '
                            }
                            agent {
                                dockerfile {
                                    filename 'ci/docker/python/linux/jenkins/Dockerfile'
                                    label 'linux && docker && devpi-access'
                                    additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                                }
                            }
                            steps {
                                script{
                                    load('ci/jenkins/scripts/devpi.groovy').pushPackageToIndex(
                                        pkgName: props.Name,
                                        pkgVersion: props.Version,
                                        server: DEVPI_CONFIG.server,
                                        indexSource: DEVPI_CONFIG.stagingIndex,
                                        indexDestination: 'production/release',
                                        credentialsId: DEVPI_CONFIG.credentialsId
                                    )
                                }
                            }
                        }
                    }
                    post{
                        success{
                            node('linux && docker && x86 && devpi-access') {
                                script{
                                    if (!env.TAG_NAME?.trim()){
                                        checkout scm
                                        def devpi = load('ci/jenkins/scripts/devpi.groovy')
                                        docker.build("getmarc:devpi",'-f ./ci/docker/python/linux/jenkins/Dockerfile --build-arg PIP_EXTRA_INDEX_URL .').inside{
                                            devpi.pushPackageToIndex(
                                                pkgName: props.Name,
                                                pkgVersion: props.Version,
                                                server: DEVPI_CONFIG.server,
                                                indexSource: DEVPI_CONFIG.stagingIndex,
                                                indexDestination: "DS_Jenkins/${env.BRANCH_NAME}",
                                                credentialsId: DEVPI_CONFIG.credentialsId
                                            )
                                        }
                                    }
                               }
                            }
                        }
                        cleanup{
                            node('linux && docker && x86 && devpi-access') {
                               script{
                                    checkout scm
                                    def devpi = load('ci/jenkins/scripts/devpi.groovy')
                                    docker.build("getmarc:devpi",'-f ./ci/docker/python/linux/jenkins/Dockerfile --build-arg PIP_EXTRA_INDEX_URL .').inside{
                                        devpi.removePackage(
                                            pkgName: props.Name,
                                            pkgVersion: props.Version,
                                            index: DEVPI_CONFIG.stagingIndex,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,

                                        )
                                    }
                               }
                            }
                        }
                    }
                }
                stage('Deploy Additional') {
                    parallel{
                        stage('Deploy to Chocolatey') {
                            when{
                                equals expected: true, actual: params.DEPLOY_CHOCOLATEY
                                beforeInput true
                                beforeAgent true
                            }
                            agent {
                                dockerfile {
                                    filename 'ci/docker/chocolatey_package/Dockerfile'
                                    label 'windows && docker && x86'
                                    additionalBuildArgs '--build-arg CHOCOLATEY_SOURCE'
                                  }
                            }
                            options{
                                timeout(time: 1, unit: 'DAYS')
                                retry(3)
                            }
                            input {
                                message 'Deploy to Chocolatey server'
                                id 'CHOCOLATEY_DEPLOYMENT'
                                parameters {
                                    choice(
                                        choices: [
                                            'https://jenkins.library.illinois.edu/nexus/repository/chocolatey-hosted-beta/',
                                            'https://jenkins.library.illinois.edu/nexus/repository/chocolatey-hosted-public/'
                                        ],
                                        description: 'Chocolatey Server to deploy to',
                                        name: 'CHOCOLATEY_SERVER'
                                    )
                                }
                            }
                            steps{
                                unstash 'CHOCOLATEY_PACKAGE'
                                script{
                                    def pkgs = []
                                    findFiles(glob: 'packages/*.nupkg').each{
                                        pkgs << it.path
                                    }
                                    def deployment_options = input(
                                        message: 'Chocolatey server',
                                        parameters: [
                                            credentials(
                                                credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl',
                                                defaultValue: 'NEXUS_NUGET_API_KEY',
                                                description: 'Nuget API key for Chocolatey',
                                                name: 'CHOCO_REPO_KEY',
                                                required: true
                                            ),
                                            choice(
                                                choices: pkgs,
                                                description: 'Package to use',
                                                name: 'NUPKG'
                                            ),
                                        ]
                                    )
                                    withCredentials([string(credentialsId: deployment_options['CHOCO_REPO_KEY'], variable: 'KEY')]) {
                                        bat(
                                            label: "Deploying ${deployment_options['NUPKG']} to Chocolatey",
                                            script: "choco push ${deployment_options['NUPKG']} -s ${CHOCOLATEY_SERVER} -k %KEY%"
                                        )
                                    }
                                }
                            }
                        }
                        stage('Deploy Online Documentation') {
                            when{
                                equals expected: true, actual: params.DEPLOY_DOCS
                                beforeAgent true
                                beforeInput true
                            }
                            agent {
                                dockerfile {
                                    filename 'ci/docker/python/linux/jenkins/Dockerfile'
                                    label 'linux && docker && x86'
                                    additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                                }
                            }
                            options{
                                timeout(time: 1, unit: 'DAYS')
                            }
                            input {
                                message 'Update project documentation?'
                            }
                            steps{
                                unstash 'DOCS_ARCHIVE'
                                withCredentials([usernamePassword(credentialsId: 'dccdocs-server', passwordVariable: 'docsPassword', usernameVariable: 'docsUsername')]) {
                                    sh 'python utils/upload_docs.py --username=$docsUsername --password=$docsPassword --subroute=getmarc2 build/docs/html apache-ns.library.illinois.edu'
                                }
                            }
                            post{
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: 'build/', type: 'INCLUDE'],
                                            [pattern: 'dist/', type: 'INCLUDE'],
                                        ]
                                    )
                                }
                            }
                        }
//                         stage('Deploy Documentation'){
//                             when{
//                                 equals expected: true, actual: params.DEPLOY_DOCS
//                                 beforeInput true
//                             }
//                             input {
//                                 message 'Deploy documentation'
//                                 id 'DEPLOY_DOCUMENTATION'
//                                 parameters {
//                                     string defaultValue: 'getmarc2', description: '', name: 'DEPLOY_DOCS_URL_SUBFOLDER', trim: true
//                                 }
//                             }
//                             agent any
//                             steps{
//                                 unstash 'DOCS_ARCHIVE'
//                                 sshPublisher(
//                                     publishers: [
//                                         sshPublisherDesc(
//                                             configName: 'apache-ns - lib-dccuser-updater',
//                                             transfers: [
//                                                 sshTransfer(
//                                                     cleanRemote: false,
//                                                     excludes: '',
//                                                     execCommand: '',
//                                                     execTimeout: 120000,
//                                                     flatten: false,
//                                                     makeEmptyDirs: false,
//                                                     noDefaultExcludes: false,
//                                                     patternSeparator: '[, ]+',
//                                                     remoteDirectory: "${DEPLOY_DOCS_URL_SUBFOLDER}",
//                                                     remoteDirectorySDF: false,
//                                                     removePrefix: 'build/docs/html',
//                                                     sourceFiles: 'build/docs/html/**'
//                                                 )
//                                             ],
//                                             usePromotionTimestamp: false,
//                                             useWorkspaceInPromotion: false,
//                                             verbose: false
//                                         )
//                                     ]
//                                 )
//                             }
//                             post{
//                                 cleanup{
//                                     cleanWs(
//                                         deleteDirs: true,
//                                         patterns: [
//                                             [pattern: 'build/', type: 'INCLUDE'],
//                                             [pattern: 'dist/', type: 'INCLUDE'],
//                                         ]
//                                     )
//                                 }
//                             }
//                         }
                    }
                }
            }
        }
    }
}
