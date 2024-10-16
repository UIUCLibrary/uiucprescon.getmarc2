library identifier: 'JenkinsPythonHelperLibrary@2024.7.0', retriever: modernSCM(
  [$class: 'GitSCMSource',
   remote: 'https://github.com/UIUCLibrary/JenkinsPythonHelperLibrary.git',
   ])


SUPPORTED_MAC_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']
SUPPORTED_LINUX_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']
SUPPORTED_WINDOWS_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']


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

def test_packages(){
    script{
        def linuxTestStages = [:]
        SUPPORTED_LINUX_VERSIONS.each{ pythonVersion ->
            def architectures = ['x86']
            if(params.INCLUDE_ARM_LINUX == true){
                architectures.add("arm64")
            }
            architectures.each{ processorArchitecture ->
                linuxTestStages["Linux-${processorArchitecture} - Python ${pythonVersion}: wheel"] = {
                    testPythonPkg(
                        agent: [
                            dockerfile: [
                                label: "linux && docker && ${processorArchitecture}",
                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_DOWNLOAD_CACHE=/.cache/pip',
                                args: '-v pipcache_uiucprescon_getmarc2:/.cache/pip',
                            ]
                        ],
                        retries: 2,
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
                linuxTestStages["Linux-${processorArchitecture} - Python ${pythonVersion}: sdist"] = {
                    testPythonPkg(
                        agent: [
                            dockerfile: [
                                label: "linux && docker && ${processorArchitecture}",
                                filename: 'ci/docker/python/linux/tox/Dockerfile',
                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_DOWNLOAD_CACHE=/.cache/pip',
                                args: '-v pipcache_uiucprescon_getmarc2:/.cache/pip',
                            ]
                        ],
                        retries: 2,
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
        }
        def macTestStages = [:]
        SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
            def architectures = []
            if(params.INCLUDE_X86_64_MACOS == true){
                architectures.add('x86_64')
            }
            if(params.INCLUDE_ARM_MACOS == true){
                architectures.add("m1")
            }
            architectures.each{ processorArchitecture ->
                macTestStages["MacOS-${processorArchitecture} - Python ${pythonVersion}: wheel"] = {
                    testPythonPkg(
                        agent: [
                            label: "mac && python${pythonVersion} && ${processorArchitecture}",
                        ],
                        retries: 3,
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
                                   pip install -r requirements/requirements_tox.txt
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
                macTestStages["MacOS-${processorArchitecture} - Python ${pythonVersion}: sdist"] = {
                    testPythonPkg(
                        agent: [
                            label: "mac && python${pythonVersion} && ${processorArchitecture}",
                        ],
                        retries: 3,
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
                                              pip install -r requirements/requirements_tox.txt
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
        }
        def windowsTestStages = [:]
        if(params.INCLUDE_WINDOWS_X86_64 == true){
            SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
                windowsTestStages["Windows - Python ${pythonVersion}: wheel"] = {
                    testPythonPkg(
                        agent: [
                            dockerfile: [
                                label: 'windows && docker && x86',
                                filename: 'ci/docker/python/windows/tox/Dockerfile',
                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip',
                                args: '-v pipcache_uiucprescon_getmarc2:c:/users/containeradministrator/appdata/local/pip',
                                dockerImageName: "${currentBuild.fullProjectName}_test".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                            ]
                        ],
                        retries: 3,
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
                    testPythonPkg(
                        agent: [
                            dockerfile: [
                                label: 'windows && docker && x86',
                                filename: 'ci/docker/python/windows/tox/Dockerfile',
                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip',
                                args: '-v pipcache_uiucprescon_getmarc2:c:/users/containeradministrator/appdata/local/pip',
                                dockerImageName: "${currentBuild.fullProjectName}_test".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                            ]
                        ],
                        retries: 3,
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
        }
        parallel(windowsTestStages + linuxTestStages + macTestStages)
    }
}

pipeline {
    agent none
    parameters {
        booleanParam(name: 'RUN_CHECKS', defaultValue: true, description: 'Run checks on code')
        booleanParam(name: 'TEST_RUN_TOX', defaultValue: false, description: 'Run Tox Tests')
        booleanParam(name: 'USE_SONARQUBE', defaultValue: true, description: 'Send data test data to SonarQube')
        booleanParam(name: 'BUILD_PACKAGES', defaultValue: false, description: 'Build Python packages')
        booleanParam(name: 'BUILD_CHOCOLATEY_PACKAGE', defaultValue: false, description: 'Build package for chocolatey package manager')
        booleanParam(name: 'TEST_PACKAGES', defaultValue: true, description: 'Test Python packages by installing them and running tests on the installed package')
        booleanParam(name: 'INCLUDE_ARM_MACOS', defaultValue: false, description: 'Include ARM(m1) architecture for Mac')
        booleanParam(name: 'INCLUDE_X86_64_MACOS', defaultValue: false, description: 'Include x86_64 architecture for Mac')
        booleanParam(name: 'INCLUDE_ARM_LINUX', defaultValue: false, description: 'Include ARM architecture for Linux')
        booleanParam(name: 'INCLUDE_WINDOWS_X86_64', defaultValue: true, description: 'Include x86_64 architecture for Windows')
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
                                def props = readTOML( file: 'pyproject.toml')['project']
                                zip archive: true, dir: 'build/docs/html', glob: '', zipFile: "dist/${props.name}-${props.version}.doc.zip"
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
                                                withEnv(['PYLINTHOME=.']) {
                                                    catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                                        tee('reports/pylint.txt'){
                                                            sh(
                                                                script: 'pylint uiucprescon.getmarc2 -r n --persistent=n --verbose --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"',
                                                                label: 'Running pylint'
                                                            )
                                                        }
                                                    }
                                                    sh(
                                                        script: '''pylint uiucprescon.getmarc2 -r n --persistent=n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt''',
                                                        label: 'Running pylint for sonarqube',
                                                        returnStatus: true
                                                    )
                                                }
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
                                            recordCoverage(tools: [[parser: 'COBERTURA', pattern: 'reports/coverage.xml']])
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
                                            def props = readTOML( file: 'pyproject.toml')['project']
                                            withSonarQubeEnv(installationName:'sonarcloud', credentialsId: 'sonarcloud_token') {
                                                if (env.CHANGE_ID){
                                                    sh(
                                                        label: 'Running Sonar Scanner',
                                                        script:"sonar-scanner -Dsonar.projectVersion=${props.version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
                                                        )
                                                } else {
                                                    sh(
                                                        label: 'Running Sonar Scanner',
                                                        script: "sonar-scanner -Dsonar.projectVersion=${props.version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME}"
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
                                    when{
                                        expression {return nodesByLabel('linux && docker').size() > 0}
                                    }
                                    steps {
                                        script{
                                            parallel(
                                                getToxTestsParallel(
                                                    envNamePrefix: 'Tox Linux',
                                                    label: 'linux && docker',
                                                    dockerfile: 'ci/docker/python/linux/tox/Dockerfile',
                                                    dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg PIP_DOWNLOAD_CACHE=/.cache/pip',
                                                    dockerRunArgs: '-v pipcache_uiucprescon_getmarc2:/.cache/pip',
                                                    retry: 2
                                                )
                                            )
                                        }
                                    }
                                }
                                stage('Windows') {
                                    when{
                                        expression {return nodesByLabel('windows && docker && x86').size() > 0}
                                    }
                                    steps {
                                        script{
                                            parallel(
                                                getToxTestsParallel(
                                                    envNamePrefix: 'Tox Windows',
                                                    label: 'windows && docker && x86',
                                                    dockerfile: 'ci/docker/python/windows/tox/Dockerfile',
                                                    dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg PIP_DOWNLOAD_CACHE=c:/users/containeradministrator/appdata/local/pip',
                                                    dockerRunArgs: "-v pipcache_uiucprescon_getmarc2:c:/users/containeradministrator/appdata/local/pip ",
                                                    retry: 2
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
                    options {
                        retry(3)
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
                                    def props = readTOML( file: 'pyproject.toml')['project']
                                        def sanitized_packageversion=sanitize_chocolatey_version(props.version)
                                        powershell(
                                            label: 'Configuring new package for Chocolatey',
                                            script: """\$ErrorActionPreference = 'Stop'; # stop on all errors
                                                       choco new getmarc packageversion=${sanitized_packageversion} PythonSummary="${props.description}" InstallerFile=${it.path} MaintainerName="${props.maintainers[0].name}" -t pythonscript --outputdirectory packages
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
                                    def props = readTOML( file: 'pyproject.toml')['project']
                                    def sanitized_packageversion=sanitize_chocolatey_version(props.version)
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
            when{
                anyOf{
                    equals expected: true, actual: params.DEPLOY_CHOCOLATEY
                    equals expected: true, actual: params.DEPLOY_DOCS
                }
            }
            stages{
                stage('Deploy Additional') {
                    when{
                        anyOf{
                            equals expected: true, actual: params.DEPLOY_CHOCOLATEY
                            equals expected: true, actual: params.DEPLOY_DOCS
                        }
                    }
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
