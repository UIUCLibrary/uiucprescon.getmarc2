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

def call(){
    library(
        identifier: 'JenkinsPythonHelperLibrary@2025.5.0',
        retriever: modernSCM(
            [
                $class: 'GitSCMSource',
                remote: 'https://github.com/UIUCLibrary/JenkinsPythonHelperLibrary.git'
            ]
        )
    )
    pipeline {
        agent none
        parameters {
            booleanParam(name: 'RUN_CHECKS', defaultValue: true, description: 'Run checks on code')
            booleanParam(name: 'TEST_RUN_TOX', defaultValue: false, description: 'Run Tox Tests')
            booleanParam(name: 'USE_SONARQUBE', defaultValue: true, description: 'Send data test data to SonarQube')
            booleanParam(name: 'BUILD_PACKAGES', defaultValue: false, description: 'Build Python packages')
            booleanParam(name: 'TEST_PACKAGES', defaultValue: true, description: 'Test Python packages by installing them and running tests on the installed package')
            booleanParam(name: 'INCLUDE_MACOS-ARM64', defaultValue: false, description: 'Include ARM(m1) architecture for Mac')
            booleanParam(name: 'INCLUDE_MACOS-X86_64', defaultValue: false, description: 'Include x86_64 architecture for Mac')
            booleanParam(name: 'INCLUDE_LINUX-ARM64', defaultValue: false, description: 'Include ARM architecture for Linux')
            booleanParam(name: 'INCLUDE_LINUX-X86_64', defaultValue: true, description: 'Include x86_64 architecture for Linux')
            booleanParam(name: 'INCLUDE_WINDOWS-X86_64', defaultValue: true, description: 'Include x86_64 architecture for Windows')
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
                        agent {
                            docker{
                                image 'python'
                                label 'docker && linux && x86_64' // needed for pysonar-scanner which is x86_64 only as of 0.2.0.520
                                args '--mount source=python-tmp-uiucprescon_getmarc,target=/tmp'
                            }
                        }
                        environment{
                            PIP_CACHE_DIR='/tmp/pipcache'
                            UV_INDEX_STRATEGY='unsafe-best-match'
                            UV_TOOL_DIR='/tmp/uvtools'
                            UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                            UV_CACHE_DIR='/tmp/uvcache'
                            UV_PYTHON = '3.12'
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
                                script: '''python3 -m venv venv
                                           trap "rm -rf venv" EXIT
                                           venv/bin/pip install --disable-pip-version-check uv
                                           . ./venv/bin/activate
                                           mkdir -p logs
                                           uvx --from sphinx --with-editable . --with-requirements requirements-dev.txt sphinx-build docs build/docs/html -d build/docs/.doctrees -w logs/build_sphinx.log
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
                                    docker{
                                        image 'python'
                                        label 'docker && linux && x86_64' // needed for pysonar-scanner which is x86_64 only as of 0.2.0.520
                                        args '--mount source=python-tmp-uiucprescon_getmarc,target=/tmp'
                                    }
                                }
                                environment{
                                    PIP_CACHE_DIR='/tmp/pipcache'
                                    UV_INDEX_STRATEGY='unsafe-best-match'
                                    UV_TOOL_DIR='/tmp/uvtools'
                                    UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                                    UV_CACHE_DIR='/tmp/uvcache'
                                    UV_PYTHON = '3.12'
                                }
                                stages{
                                    stage('Configuring Testing Environment'){
                                        steps{
                                            sh(
                                                label: 'Create virtual environment',
                                                script: '''python3 -m venv bootstrap_uv
                                                           bootstrap_uv/bin/pip install --disable-pip-version-check uv
                                                           bootstrap_uv/bin/uv venv venv
                                                           . ./venv/bin/activate
                                                           bootstrap_uv/bin/uv pip install uv
                                                           rm -rf bootstrap_uv
                                                           uv pip install -r requirements-dev.txt
                                                           '''
                                                       )
                                            sh(
                                                label: 'Install package in development mode',
                                                script: '''. ./venv/bin/activate
                                                           uv pip install -e .
                                                        '''
                                                )
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
                                                    sh '''. ./venv/bin/activate
                                                            coverage run --parallel-mode --source uiucprescon -m pytest --junitxml=reports/pytest/junit-pytest.xml
                                                            '''
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
                                                        script: '''. ./venv/bin/activate
                                                                   mkdir -p reports/doctests
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
                                                            script: '''. ./venv/bin/activate
                                                                       mkdir -p reports
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
                                                                script: '''. ./venv/bin/activate
                                                                           mkdir -p reports/mypy/html
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
                                                            script: '''. ./venv/bin/activate
                                                                       bandit --format json --output reports/bandit-report.json --recursive uiucprescon || bandit -f html --recursive uiucprescon --output reports/bandit-report.html
                                                                    '''
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
                                                                    script: '''. ./venv/bin/activate
                                                                               pylint uiucprescon.getmarc2 -r n --persistent=n --verbose --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"
                                                                            ''',
                                                                    label: 'Running pylint'
                                                                )
                                                            }
                                                        }
                                                        sh(
                                                            script: '''. ./venv/bin/activate
                                                                       pylint uiucprescon.getmarc2 -r n --persistent=n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt
                                                                    ''',
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
                                                           script: '''. ./venv/bin/activate
                                                                      mkdir -p logs
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
                                                    script: '''. ./venv/bin/activate
                                                              mkdir -p reports/coverage
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
                                        environment{
                                            VERSION="${readTOML( file: 'pyproject.toml')['project'].version}"
                                            SONAR_USER_HOME='/tmp/sonar'
                                        }
                                        steps{
                                            script{
                                                withSonarQubeEnv(installationName:'sonarcloud', credentialsId: params.SONARCLOUD_TOKEN) {
                                                    def sourceInstruction
                                                    if (env.CHANGE_ID){
                                                        sourceInstruction = '-Dsonar.pullrequest.key=$CHANGE_ID -Dsonar.pullrequest.base=$BRANCH_NAME'
                                                    } else{
                                                        sourceInstruction = '-Dsonar.branch.name=$BRANCH_NAME'
                                                    }
                                                    sh(
                                                        label: 'Running Sonar Scanner',
                                                        script: """. ./venv/bin/activate
                                                                    uv tool run pysonar-scanner -Dsonar.projectVersion=$VERSION -Dsonar.buildString=\"$BUILD_TAG\" ${sourceInstruction}
                                                                """
                                                    )
                                                }
                                                timeout(time: 1, unit: 'HOURS') {
                                                    def sonarqube_result = waitForQualityGate(abortPipeline: false)
                                                    if (sonarqube_result.status != 'OK') {
                                                        unstable "SonarQube quality gate: ${sonarqube_result.status}"
                                                    }
                                                    def outstandingIssues = get_sonarqube_unresolved_issues('.scannerwork/report-task.txt')
                                                    writeJSON file: 'reports/sonar-report.json', json: outstandingIssues
                                                }
                                                milestone label: 'sonarcloud'
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
                                        environment{
                                            PIP_CACHE_DIR='/tmp/pipcache'
                                            UV_INDEX_STRATEGY='unsafe-best-match'
                                            UV_TOOL_DIR='/tmp/uvtools'
                                            UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                                            UV_CACHE_DIR='/tmp/uvcache'
                                        }
                                        steps{
                                            script{
                                                def envs = []
                                                node('docker && linux'){
                                                    docker.image('python').inside('--mount source=python-tmp-uiucprescon_getmarc,target=/tmp'){
                                                        try{
                                                            checkout scm
                                                            sh(script: 'python3 -m venv venv && venv/bin/pip install --disable-pip-version-check uv')
                                                            envs = sh(
                                                                label: 'Get tox environments',
                                                                script: './venv/bin/uvx --quiet --with tox-uv tox list -d --no-desc',
                                                                returnStdout: true,
                                                            ).trim().split('\n')
                                                        } finally{
                                                            cleanWs(
                                                                patterns: [
                                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                                    [pattern: '.tox', type: 'INCLUDE'],
                                                                    [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                ]
                                                            )
                                                        }
                                                    }
                                                }
                                                parallel(
                                                    envs.collectEntries{toxEnv ->
                                                        def version = toxEnv.replaceAll(/py(\d)(\d+)/, '$1.$2')
                                                        [
                                                            "Tox Environment: ${toxEnv}",
                                                            {
                                                                node('docker && linux'){
                                                                    docker.image('python').inside('--mount source=python-tmp-uiucprescon_getmarc,target=/tmp'){
                                                                        checkout scm
                                                                        try{
                                                                            sh( label: 'Running Tox',
                                                                                script: """python3 -m venv venv && venv/bin/pip install --disable-pip-version-check uv
                                                                                           . ./venv/bin/activate
                                                                                           uv python install cpython-${version}
                                                                                           uvx -p ${version} --with tox-uv tox run -e ${toxEnv}
                                                                                           rm -rf ./.tox
                                                                                           rm -rf ./venv
                                                                                        """
                                                                                )
                                                                        } catch(e) {
                                                                            sh(script: '''. ./venv/bin/activate
                                                                                  uv python list
                                                                                  '''
                                                                                    )
                                                                            throw e
                                                                        } finally{
                                                                            cleanWs(
                                                                                patterns: [
                                                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                                                    [pattern: '.tox', type: 'INCLUDE'],
                                                                                    [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                                ]
                                                                            )
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        ]
                                                    }
                                                )
                                            }
                                         }
                                    }
                                    stage('Windows') {
                                        when{
                                            expression {return nodesByLabel('windows && docker && x86').size() > 0}
                                        }
                                        environment{
                                             UV_INDEX_STRATEGY='unsafe-best-match'
                                             PIP_CACHE_DIR='C:\\Users\\ContainerUser\\Documents\\pipcache'
                                             UV_TOOL_DIR='C:\\Users\\ContainerUser\\Documents\\uvtools'
                                             UV_PYTHON_INSTALL_DIR='C:\\Users\\ContainerUser\\Documents\\uvpython'
                                             UV_CACHE_DIR='C:\\Users\\ContainerUser\\Documents\\uvcache'
                                        }
                                        steps{
                                            script{
                                                def envs = []
                                                node('docker && windows'){
                                                    docker.image(env.DEFAULT_PYTHON_DOCKER_IMAGE ? env.DEFAULT_PYTHON_DOCKER_IMAGE: 'python').inside("--mount type=volume,source=uv_python_install_dir,target=${env.UV_PYTHON_INSTALL_DIR}"){
                                                        try{
                                                            checkout scm
                                                            bat(script: 'python -m venv venv && venv\\Scripts\\pip install --disable-pip-version-check uv')
                                                            envs = bat(
                                                                label: 'Get tox environments',
                                                                script: '@.\\venv\\Scripts\\uvx --quiet --with tox-uv tox list -d --no-desc',
                                                                returnStdout: true,
                                                            ).trim().split('\r\n')
                                                        } finally{
                                                            cleanWs(
                                                                patterns: [
                                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                                    [pattern: '.tox', type: 'INCLUDE'],
                                                                    [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                ]
                                                            )
                                                        }
                                                    }
                                                }
                                                parallel(
                                                    envs.collectEntries{toxEnv ->
                                                        def version = toxEnv.replaceAll(/py(\d)(\d+)/, '$1.$2')
                                                        [
                                                            "Tox Environment: ${toxEnv}",
                                                            {
                                                                node('docker && windows'){
                                                                    retry(3){
                                                                        try{    
                                                                            docker.image(env.DEFAULT_PYTHON_DOCKER_IMAGE ? env.DEFAULT_PYTHON_DOCKER_IMAGE: 'python').inside("--mount type=volume,source=uv_python_install_dir,target=${env.UV_PYTHON_INSTALL_DIR}"){
                                                                                checkout scm
                                                                                bat(label: 'Running Tox',
                                                                                    script: """python -m venv venv && venv\\Scripts\\pip install --disable-pip-version-check uv
                                                                                        call venv\\Scripts\\activate.bat
                                                                                        uv python install cpython-${version}
                                                                                        uvx -p ${version} --with tox-uv tox run -e ${toxEnv}
                                                                                        rmdir /S /Q .tox
                                                                                        rmdir /S /Q venv
                                                                                        """
                                                                                )
                                                                            }
                                                                        } finally{
                                                                             bat "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        ]
                                                    }
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
                    }
                    beforeAgent true
                }
                stages{
                    stage('Creating Python Packages') {
                        agent {
                            docker{
                                image 'python'
                                label 'linux && docker'
                                args '--mount source=python-tmp-uiucprescon_getmarc,target=/tmp'
                              }
                        }
                        environment{
                            PIP_CACHE_DIR='/tmp/pipcache'
                            UV_INDEX_STRATEGY='unsafe-best-match'
                            UV_CACHE_DIR='/tmp/uvcache'
                        }
                        options {
                            retry(2)
                        }
                        steps{
                            timeout(5){
                                sh(
                                    label: 'Package',
                                    script: '''python3 -m venv venv && venv/bin/pip install --disable-pip-version-check uv
                                               trap "rm -rf venv" EXIT
                                               . ./venv/bin/activate
                                               uv build
                                            '''
                                )
                            }
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
                    stage('Testing Packages'){
                        when{
                            equals expected: true, actual: params.TEST_PACKAGES
                        }
                        environment{
                            UV_INDEX_STRATEGY='unsafe-best-match'
                        }
                        steps{
                            customMatrix(
                                axes: [
                                    [
                                        name: 'PYTHON_VERSION',
                                        values: ['3.10', '3.11', '3.12','3.13']
                                    ],
                                    [
                                        name: 'OS',
                                        values: ['linux','macos','windows']
                                    ],
                                    [
                                        name: 'ARCHITECTURE',
                                        values: ['x86_64', 'arm64']
                                    ],
                                    [
                                        name: 'PACKAGE_TYPE',
                                        values: ['wheel', 'sdist'],
                                    ]
                                ],
                                excludes: [
                                    [
                                        [
                                            name: 'OS',
                                            values: 'windows'
                                        ],
                                        [
                                            name: 'ARCHITECTURE',
                                            values: 'arm64',
                                        ]
                                    ]
                                ],
                                when: {entry -> "INCLUDE_${entry.OS}-${entry.ARCHITECTURE}".toUpperCase() && params["INCLUDE_${entry.OS}-${entry.ARCHITECTURE}".toUpperCase()]},
                                stages: [
                                    { entry ->
                                        stage('Test Package') {
                                            node("${entry.OS} && ${entry.ARCHITECTURE} ${['linux', 'windows'].contains(entry.OS) ? '&& docker': ''}"){
                                                try{
                                                    checkout scm
                                                    unstash 'PYTHON_PACKAGES'
                                                    if(['linux', 'windows'].contains(entry.OS) && params.containsKey("INCLUDE_${entry.OS}-${entry.ARCHITECTURE}".toUpperCase()) && params["INCLUDE_${entry.OS}-${entry.ARCHITECTURE}".toUpperCase()]){
                                                        docker.image(env.DEFAULT_PYTHON_DOCKER_IMAGE ? env.DEFAULT_PYTHON_DOCKER_IMAGE: 'python').inside(isUnix() ? '': "--mount type=volume,source=uv_python_install_dir,target=C:\\Users\\ContainerUser\\Documents\\uvpython"){
                                                             if(isUnix()){
                                                                withEnv([
                                                                    'PIP_CACHE_DIR=/tmp/pipcache',
                                                                    'UV_TOOL_DIR=/tmp/uvtools',
                                                                    'UV_PYTHON_INSTALL_DIR=/tmp/uvpython',
                                                                    'UV_CACHE_DIR=/tmp/uvcache',
                                                                ]){
                                                                     sh(
                                                                        label: 'Testing with tox',
                                                                        script: """python3 -m venv venv
                                                                                   ./venv/bin/pip install --disable-pip-version-check uv
                                                                                   ./venv/bin/uv python install cpython-${entry.PYTHON_VERSION}
                                                                                   ./venv/bin/uvx --with tox-uv tox --installpkg ${findFiles(glob: entry.PACKAGE_TYPE == 'wheel' ? 'dist/*.whl' : 'dist/*.tar.gz')[0].path} -e py${entry.PYTHON_VERSION.replace('.', '')}
                                                                                """
                                                                    )
                                                                }
                                                             } else {
                                                                withEnv([
                                                                    'PIP_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\pipcache',
                                                                    'UV_TOOL_DIR=C:\\Users\\ContainerUser\\Documents\\uvtools',
                                                                    'UV_PYTHON_INSTALL_DIR=C:\\Users\\ContainerUser\\Documents\\uvpython',
                                                                    'UV_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\uvcache',
                                                                ]){
                                                                    bat(
                                                                        label: 'Testing with tox',
                                                                        script: """python -m venv venv
                                                                                   .\\venv\\Scripts\\pip install --disable-pip-version-check uv
                                                                                   .\\venv\\Scripts\\uv python install cpython-${entry.PYTHON_VERSION}
                                                                                   .\\venv\\Scripts\\uvx --with tox-uv tox --installpkg ${findFiles(glob: entry.PACKAGE_TYPE == 'wheel' ? 'dist/*.whl' : 'dist/*.tar.gz')[0].path} -e py${entry.PYTHON_VERSION.replace('.', '')}
                                                                                """
                                                                    )
                                                                }
                                                             }
                                                        }
                                                    } else {
                                                        if(isUnix()){
                                                            sh(
                                                                label: 'Testing with tox',
                                                                script: """python3 -m venv venv
                                                                           ./venv/bin/pip install --disable-pip-version-check uv
                                                                           ./venv/bin/uvx --with tox-uv tox --installpkg ${findFiles(glob: entry.PACKAGE_TYPE == 'wheel' ? 'dist/*.whl' : 'dist/*.tar.gz')[0].path} -e py${entry.PYTHON_VERSION.replace('.', '')}
                                                                        """
                                                            )
                                                        } else {
                                                            bat(
                                                                label: 'Testing with tox',
                                                                script: """python -m venv venv
                                                                           .\\venv\\Scripts\\pip install --disable-pip-version-check uv
                                                                           .\\venv\\Scripts\\uv python install cpython-${entry.PYTHON_VERSION}
                                                                           .\\venv\\Scripts\\uvx --with tox-uv tox --installpkg ${findFiles(glob: entry.PACKAGE_TYPE == 'wheel' ? 'dist/*.whl' : 'dist/*.tar.gz')[0].path} -e py${entry.PYTHON_VERSION.replace('.', '')}
                                                                        """
                                                            )
                                                        }
                                                    }
                                                } finally{
                                                    if(isUnix()){
                                                        sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                    } else {
                                                        bat "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                ]
                            )
                        }
                    }
                }
            }
            stage('Deploy'){
                when{
                    anyOf{
                        equals expected: true, actual: params.DEPLOY_DOCS
                    }
                }
                parallel{
                    stage('Deploy Online Documentation') {
                        when{
                            equals expected: true, actual: params.DEPLOY_DOCS
                            beforeAgent true
                            beforeInput true
                        }
                        environment{
                            PIP_CACHE_DIR='/tmp/pipcache'
                            UV_INDEX_STRATEGY='unsafe-best-match'
                            UV_TOOL_DIR='/tmp/uvtools'
                            UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                            UV_CACHE_DIR='/tmp/uvcache'
                        }
                        agent {
                            docker{
                                image 'python'
                                label 'docker && linux'
                                args '--mount source=python-tmp-uiucprescon_getmarc,target=/tmp'
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
                }
//                 stages{
//                     stage('Deploy Additional') {
//                         when{
//                             anyOf{
//                                 equals expected: true, actual: params.DEPLOY_DOCS
//                             }
//                         }
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
    //                     }
    //                }
    //             }
            }
        }
    }
}
