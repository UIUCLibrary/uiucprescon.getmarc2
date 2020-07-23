
// def CONFIGURATIONS = [
//     "3.7": [
//             package_testing: [
//                 whl: [
//                     pkgRegex: "*.whl",
//                 ],
//                 sdist:[
//                     pkgRegex: "*.zip",
//                 ]
//             ],
//             test_docker_image: [
//                 windows: "python:3.7",
//                 linux: "python:3.7"
//             ],
//             tox_env: "py37",
//             devpi_wheel_regex: "cp37"
//         ],
//     "3.8": [
//             package_testing: [
//                 whl: [
//                     pkgRegex: "*.whl",
//                 ],
//                 sdist:[
//                     pkgRegex: "*.zip",
//                 ]
//             ],
//             test_docker_image: [
//                 windows: "python:3.8",
//                 linux: "python:3.8"
//             ],
//             tox_env: "py38",
//             devpi_wheel_regex: "cp38"
//         ]
// ]


def getDevPiStagingIndex(){

    if (env.TAG_NAME?.trim()){
        return "tag_staging"
    } else{
        return "${env.BRANCH_NAME}_staging"
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


def devpiRunTest(pkgPropertiesFile, devpiIndex, devpiSelector, devpiUsername, devpiPassword, toxEnv){
    script{
        def props = readProperties interpolate: false, file: pkgPropertiesFile
        if (isUnix()){
            sh(
                label: "Running test",
                script: """devpi use https://devpi.library.illinois.edu --clientdir certs/
                           devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs/
                           devpi use ${devpiIndex} --clientdir certs/
                           devpi test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs/ -e ${toxEnv} --tox-args=\"-vv\"
                """
            )
        } else {
            bat(
                label: "Running tests on Devpi",
                script: """devpi use https://devpi.library.illinois.edu --clientdir certs\\
                           devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
                           devpi use ${devpiIndex} --clientdir certs\\
                           devpi test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs\\ -e ${toxEnv} --tox-args=\"-vv\"
                           """
            )
        }
    }
}


pipeline {
    agent none
    parameters {
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
//         TODO: turn USE_SONARQUBE default to true
        booleanParam(name: "USE_SONARQUBE", defaultValue: false, description: "Send data test data to SonarQube")
        booleanParam(name: "BUILD_PACKAGES", defaultValue: false, description: "Build Python packages")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to production devpi on https://devpi.library.illinois.edu/production/release. Master branch Only")
        booleanParam(name: "DEPLOY", defaultValue: false, description: "Deploy")
    }
    stages {
        stage("Getting Distribution Info"){
            agent {
                dockerfile {
                    filename 'ci/docker/python/linux/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
                }
            }
            steps{
                timeout(5){
                    sh "python setup.py dist_info"
                }
            }
            post{
                success{
                    stash includes: "uiucprescon.getmarc2.dist-info/**", name: 'DIST-INFO'
                    archiveArtifacts artifacts: "uiucprescon.getmarc2.dist-info/**"
                }
                cleanup{
                    cleanWs(
                        deleteDirs: true,
                        patterns: [
                            [pattern: "uiucprescon.getmarc2.dist-info/", type: 'INCLUDE'],
                            ]
                    )
                }
            }
        }
        stage("Sphinx Documentation"){
            agent{
                dockerfile {
                        filename 'ci/docker/python/linux/Dockerfile'
                        label 'linux && docker'
                        additionalBuildArgs "--build-arg USER_ID=\$(id -u) --build-arg GROUP_ID=\$(id -g) --build-arg PIP_EXTRA_INDEX_URL"
                    }
                }
                steps {
                    sh(
                        label: "Building docs",
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
                        unstash "DIST-INFO"
                        script{
                            def props = readProperties interpolate: false, file: "uiucprescon.getmarc2.dist-info/METADATA"
                            def DOC_ZIP_FILENAME = "${props.Name}-${props.Version}.doc.zip"
                            zip archive: true, dir: "${WORKSPACE}/build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
                            stash includes: "dist/${DOC_ZIP_FILENAME},build/docs/html/**", name: 'DOCS_ARCHIVE'
                        }

                    }
                    cleanup{
                        cleanWs(
                            patterns: [
                                [pattern: 'logs/', type: 'INCLUDE'],
                                [pattern: "build/docs/", type: 'INCLUDE'],
                                [pattern: "dist/", type: 'INCLUDE']
                            ],
                            deleteDirs: true
                        )
                    }
                }
            }
        stage("Checks") {
            agent {
                dockerfile {
                    filename 'ci/docker/python/linux/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs "--build-arg PIP_EXTRA_INDEX_URL"
                }
            }
            stages{
                stage("Configuring Testing Environment"){
                    steps{
                        sh(
                            label: "Creating logging and report directories",
                            script: """
                                mkdir -p logs
                                mkdir -p reports/coverage
                                mkdir -p reports/doctests
                                mkdir -p reports/mypy/html
                            """
                        )
                    }
                }
                stage("Running Tests"){
                    parallel {
                        stage("PyTest"){
                            steps{
                                sh "coverage run --parallel-mode --source uiucprescon -m pytest --junitxml=reports/pytest/junit-pytest.xml "
                            }
                            post {
                                always {
                                    junit "reports/pytest/junit-pytest.xml"
                                    stash includes: "reports/pytest/*.xml", name: 'PYTEST_REPORT'
                                }
                            }
                        }
                        stage("Doctest"){
                            steps {
                                sh "coverage run --parallel-mode --source uiucprescon -m sphinx -b doctest -d build/docs/doctrees docs reports/doctest -w logs/doctest.log"
                            }
                            post{
                                always {
                                    recordIssues(tools: [sphinxBuild(name: 'Sphinx Doctest', pattern: 'logs/doctest.log', id: 'doctest')])
                                }

                            }
                        }
                        stage("pyDocStyle"){
                            steps{
                                catchError(buildResult: 'SUCCESS', message: 'Did not pass all pyDocStyle tests', stageResult: 'UNSTABLE') {
                                    sh(
                                        label: "Run pydocstyle",
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
                        stage("MyPy") {
                            steps{
                                catchError(buildResult: 'SUCCESS', message: 'mypy found issues', stageResult: 'UNSTABLE') {
                                    sh "mypy -p uiucprescon.getmarc2 --namespace-packages --html-report reports/mypy/html/  | tee logs/mypy.log"
                                }
                            }
                            post {
                                always {
                                    recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                }
                            }
                        }
                        stage("Tox") {
                            when{
                                equals expected: true, actual: params.TEST_RUN_TOX
                            }
                            steps {
                                sh "tox -e py"

                            }
                        }
                        stage("Bandit") {
                            steps{
                                catchError(buildResult: 'SUCCESS', message: 'Bandit found issues', stageResult: 'UNSTABLE') {
                                    sh(
                                        label: "Running bandit",
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
                                always {
                                    stash includes: "reports/bandit-report.json", name: 'BANDIT_REPORT'
                                }
                            }
                        }
                        stage("PyLint") {
                            steps{
                                catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                    tee("reports/pylint.txt"){
                                        sh(
                                            script: '''pylint uiucprescon -r n --persistent=n --verbose --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"
                                                       ''',
                                            label: "Running pylint"
                                        )
                                    }
                                }
                                sh(
                                    script: 'pylint uiucprescon  -r n --persistent=n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt',
                                    label: "Running pylint for sonarqube",
                                    returnStatus: true
                                )
                            }
                            post{
                                always{
                                    stash includes: "reports/pylint_issues.txt,reports/pylint.txt", name: 'PYLINT_REPORT'
                                    recordIssues(tools: [pyLint(pattern: 'reports/pylint.txt')])
                                }
                            }
                        }
                        stage("Flake8") {
                            steps{
                                catchError(buildResult: 'SUCCESS', message: 'Flake8 found issues', stageResult: 'UNSTABLE') {
                                    sh(label: "Running Flake8",
                                       script: '''mkdir -p logs
                                                  flake8 uiucprescon --tee --output-file=logs/flake8.log
                                               '''
                                       )
                                }
                            }
                            post {
                                always {
                                    recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                    stash includes: "logs/flake8.log", name: 'FLAKE8_REPORT'
                                }
                            }
                        }
                    }
                    post{
                        always{
                            sh "coverage combine && coverage xml -o reports/coverage.xml && coverage html -d reports/coverage"
                            publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/coverage", reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                            publishCoverage adapters: [
                                            coberturaAdapter('reports/coverage.xml')
                                            ],
                                        sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
                            stash includes: "reports/coverage.xml", name: 'COVERAGE_REPORT'
                        }
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: "dist/", type: 'INCLUDE'],
                                    [pattern: 'build/', type: 'INCLUDE'],
                                    [pattern: '.pytest_cache/', type: 'INCLUDE'],
                                    [pattern: '.mypy_cache/', type: 'INCLUDE'],
                                    [pattern: '.tox/', type: 'INCLUDE'],
                                    [pattern: 'uiucprescon1.stats', type: 'INCLUDE'],
                                    [pattern: 'uiucprescon.packager.egg-info/', type: 'INCLUDE'],
                                    [pattern: 'reports/', type: 'INCLUDE'],
                                    [pattern: 'logs/', type: 'INCLUDE']
                                    ]
                            )
                        }
                    }
                }
            }
            post{
                cleanup{
                    cleanWs(
                        deleteDirs: true,
                        patterns: [
                            [pattern: 'reports/coverage.xml', type: 'INCLUDE'],
                            [pattern: 'reports/coverage', type: 'INCLUDE'],
                        ])
                }
            }
        }
        stage("Sonarcloud Analysis"){
            agent {
              dockerfile {
                filename 'ci/docker/sonarcloud/Dockerfile'
                label 'linux && docker'
              }
            }
            options{
                lock("uiucprescon.getmarc2-sonarscanner")
            }
            when{
                equals expected: true, actual: params.USE_SONARQUBE
                beforeAgent true
                beforeOptions true
            }
            steps{
                checkout scm
                sh "git fetch --all"
                unstash "COVERAGE_REPORT"
                unstash "PYTEST_REPORT"
                unstash "BANDIT_REPORT"
                unstash "PYLINT_REPORT"
                unstash "FLAKE8_REPORT"
                script{
                    withSonarQubeEnv(installationName:"sonarcloud", credentialsId: 'sonarcloud-uiucprescon.getmarc2') {
                        unstash "DIST-INFO"
                        def props = readProperties(interpolate: false, file: "uiucprescon.getmarc2.dist-info/METADATA")
                        if (env.CHANGE_ID){
                            sh(
                                label: "Running Sonar Scanner",
                                script:"sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
                                )
                        } else {
                            sh(
                                label: "Running Sonar Scanner",
                                script: "sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME}"
                                )
                        }
                    }
                    timeout(time: 1, unit: 'HOURS') {
                        def sonarqube_result = waitForQualityGate(abortPipeline: false)
                        if (sonarqube_result.status != 'OK') {
                            unstable "SonarQube quality gate: ${sonarqube_result.status}"
                        }
                        def outstandingIssues = get_sonarqube_unresolved_issues(".scannerwork/report-task.txt")
                        writeJSON file: 'reports/sonar-report.json', json: outstandingIssues
                    }
                }
            }
            post {
                always{
                    script{
                        if(fileExists('reports/sonar-report.json')){
                            stash includes: "reports/sonar-report.json", name: 'SONAR_REPORT'
                            archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/sonar-report.json'
                            recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
                        }
                    }
                }
                cleanup{
                    cleanWs(
                        deleteDirs: true,
                        patterns: [
                            [pattern: 'reports/', type: 'INCLUDE'],
                            [pattern: 'logs/', type: 'INCLUDE'],
                            [pattern: 'uiucprescon.getmarc2.dist-info/', type: 'INCLUDE'],
                            [pattern: '.scannerwork/', type: 'INCLUDE'],
                        ]
                    )
                }
            }
        }
        stage("Distribution Packages"){
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                }
                beforeAgent true
            }
            stages{
                stage("Creating Package") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                        }
                    }
                    steps {
                        sh(label: "Building python distribution packages", script: 'python -m pep517.build .')
                    }
                    post {
                        always{
                            stash includes: 'dist/*.*', name: "PYTHON_PACKAGES"
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
                stage('Testing all Package') {
                    matrix{
                        axes{
                            axis {
                                name "PLATFORM"
                                values(
                                    "windows",
                                    "linux"
                                )
                            }
                            axis {
                                name "PYTHON_VERSION"
                                values(
                                    "3.7",
                                    "3.8"
                                )
                            }
                        }
                        agent {
                            dockerfile {
                                filename "ci/docker/python/${PLATFORM}/Dockerfile"
                                label "${PLATFORM} && docker"
                                additionalBuildArgs "--build-arg PYTHON_VERSION=${PYTHON_VERSION} --build-arg PIP_EXTRA_INDEX_URL"
                            }
                        }
                        stages{
                            stage("Testing Package sdist"){
                                options {
                                    warnError('Package Testing Failed')
                                }
                                steps{
                                    unstash "PYTHON_PACKAGES"
                                    script{
                                        findFiles(glob: "**/*.tar.gz").each{
                                            timeout(15){
                                                if(PLATFORM == "windows"){
                                                    bat(
                                                        script: """python --version
                                                                   tox --installpkg=${it.path} -e py -vv
                                                                   """,
                                                        label: "Testing ${it}"
                                                    )
                                                } else {
                                                    sh(
                                                        script: """python --version
                                                                   tox --installpkg=${it.path} -e py -vv
                                                                   """,
                                                        label: "Testing ${it}"
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                                post{
                                    cleanup{
                                        cleanWs(
                                            notFailBuild: true,
                                            deleteDirs: true,
                                            patterns: [
                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                [pattern: 'build/', type: 'INCLUDE'],
                                                [pattern: '.tox/', type: 'INCLUDE'],
                                                ]
                                        )
                                    }
                                }
                            }
                            stage("Testing Package Wheel"){
                                options {
                                    warnError('Package Testing Failed')
                                }
                                steps{
                                    unstash "PYTHON_PACKAGES"
                                    script{
                                        findFiles(glob: "**/*.whl").each{
                                            timeout(15){
                                                if(PLATFORM == "windows"){
                                                    bat(
                                                        script: """python --version
                                                                   tox --installpkg=${it.path} -e py -vv
                                                                   """,
                                                        label: "Testing ${it}"
                                                    )
                                                } else {
                                                    sh(
                                                        script: """python --version
                                                                   tox --installpkg=${it.path} -e py -vv
                                                                   """,
                                                        label: "Testing ${it}"
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                                post{
                                    cleanup{
                                        cleanWs(
                                            notFailBuild: true,
                                            deleteDirs: true,
                                            patterns: [
                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                [pattern: 'build/', type: 'INCLUDE'],
                                                [pattern: '.tox/', type: 'INCLUDE'],
                                                ]
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        stage("Deploy to Devpi"){
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                        tag "*"
                    }
                }
                beforeAgent true
                beforeOptions true
            }
            agent none
            environment{
                DEVPI = credentials("DS_devpi")
                devpiStagingIndex = getDevPiStagingIndex()
            }
            options{
                lock("uiucprescon.getmarc2-devpi")
            }
            stages{
                stage("Deploy to Devpi Staging") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                          }
                    }
                    steps {
                        unstash "PYTHON_PACKAGES"
                        unstash "DOCS_ARCHIVE"
                        sh(
                            label: "Uploading to DevPi Staging",
                            script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                       devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                       devpi use /${env.DEVPI_USR}/${env.devpiStagingIndex} --clientdir ./devpi
                                       devpi upload --from-dir dist --clientdir ./devpi"""
                        )
                    }
                }
                stage("Test DevPi Package") {
                    matrix {
                        axes {
                            axis {
                                name 'PLATFORM'
                                values(
                                    "linux",
                                    "windows"
                                )
                            }
                            axis {
                                name 'PYTHON_VERSION'
                                values '3.7', '3.8'
                            }
                        }
                        agent none
                        stages{
                            stage("Testing DevPi wheel Package"){
                                agent {
                                    dockerfile {
                                        filename "ci/docker/python/${PLATFORM}/Dockerfile"
                                        label "${PLATFORM} && docker"
                                        additionalBuildArgs "--build-arg PYTHON_VERSION=${PYTHON_VERSION} --build-arg PIP_EXTRA_INDEX_URL"
                                    }
                                }
                                options {
                                    warnError('Package Testing Failed')
                                }
                                steps{
                                    timeout(10){
                                        unstash "DIST-INFO"
                                        devpiRunTest(
                                            "uiucprescon.getmarc2.dist-info/METADATA",
                                            env.devpiStagingIndex,
                                            "whl",
                                            DEVPI_USR,
                                            DEVPI_PSW,
                                            "py${PYTHON_VERSION.replace('.', '')}"
                                            )
                                    }
                                }
                            }
                            stage("Testing DevPi sdist Package"){
                                agent {
                                    dockerfile {
                                        filename "ci/docker/python/${PLATFORM}/Dockerfile"
                                        label "${PLATFORM} && docker"
                                        additionalBuildArgs "--build-arg PYTHON_VERSION=${PYTHON_VERSION} --build-arg PIP_EXTRA_INDEX_URL"
                                    }
                                }
                                options {
                                    warnError('Package Testing Failed')
                                }
                                steps{
                                    timeout(10){
                                        unstash "DIST-INFO"
                                        devpiRunTest(
                                            "uiucprescon.getmarc2.dist-info/METADATA",
                                            env.devpiStagingIndex,
                                            "tar.gz",
                                            DEVPI_USR,
                                            DEVPI_PSW,
                                            "py${PYTHON_VERSION.replace('.', '')}"
                                            )
                                    }
                                }
                            }
                        }
                    }
                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            anyOf {
                                branch "master"
                                tag "*"
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
                            filename 'ci/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                        }
                    }
                    steps {
                        script {
                            unstash "DIST-INFO"
                            def props = readProperties interpolate: true, file: 'uiucprescon.getmarc2.dist-info/METADATA'
                            sh(
                                label: "Pushing to production/release index",
                                script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                           devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                           devpi push --index DS_Jenkins/${env.devpiStagingIndex} ${props.Name}==${props.Version} production/release --clientdir ./devpi
                                           """
                            )
                        }
                    }
                }
            }
            post{
                success{
                    node('linux && docker') {
                       script{
                            if (!env.TAG_NAME?.trim()){
                                docker.build("getmarc:devpi",'-f ./ci/docker/python/linux/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                    unstash "DIST-INFO"
                                    def props = readProperties interpolate: true, file: 'uiucprescon.getmarc2.dist-info/METADATA'
                                    sh(
                                        label: "Moving DevPi package from staging index to index",
                                        script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                                   devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                                   devpi use /DS_Jenkins/${env.devpiStagingIndex} --clientdir ./devpi
                                                   devpi push ${props.Name}==${props.Version} DS_Jenkins/${env.BRANCH_NAME} --clientdir ./devpi
                                                   """
                                    )
                                }
                           }
                       }
                    }
                }
                cleanup{
                    node('linux && docker') {
                       script{
                            docker.build("getmarc:devpi",'-f ./ci/docker/python/linux/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                unstash "DIST-INFO"
                                def props = readProperties interpolate: true, file: 'uiucprescon.getmarc2.dist-info/METADATA'
                                sh(
                                    label: "Removing Package from DevPi staging index",
                                    script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                               devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                               devpi use /DS_Jenkins/${env.devpiStagingIndex} --clientdir ./devpi
                                               devpi remove -y ${props.Name}==${props.Version} --clientdir ./devpi
                                               """
                                   )
                            }
                       }
                    }
                }
            }
        }
        stage("Deploy") {
            when{
                equals expected: true, actual: params.DEPLOY
                beforeInput true
            }
            input {
              message 'Deploy Documentation'
              parameters {
                booleanParam defaultValue: false, description: '', name: 'DEPLOY_DOCS'
              }
            }
            parallel{
                stage("Deploy Documentation"){
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                    }
                    agent any
                    steps{
                        echo "Hellol DEPLOY_DOCS = ${DEPLOY_DOCS}"
                    }
                }
                stage("Hello"){
                    agent any
                    steps{
                        echo "Hellol DEPLOY_DOCS = ${DEPLOY_DOCS}"
                        echo "Hellol params.DEPLOY_DOCS = ${params.DEPLOY_DOCS}"
                    }
                }

            }
        }
    }
}