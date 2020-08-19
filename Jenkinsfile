
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
def sanitize_chocolatey_version(version){
    script{
        def dot_to_slash_pattern = '(?<=\\d)\\.?(?=(dev|b|a|rc)(\\d)?)'

        def dashed_version = version.replaceFirst(dot_to_slash_pattern, "-")

        def beta_pattern = "(?<=\\d(\\.?))b((?=\\d)?)"
        if(dashed_version.matches(beta_pattern)){
            return dashed_version.replaceFirst(beta_pattern, "beta")
        }

        def alpha_pattern = "(?<=\\d(\\.?))a((?=\\d)?)"
        if(dashed_version.matches(alpha_pattern)){
            return dashed_version.replaceFirst(alpha_pattern, "alpha")
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
//         TODO make true
        booleanParam(name: "RUN_CHECKS", defaultValue: false, description: "Run checks on code")
        booleanParam(name: "USE_SONARQUBE", defaultValue: true, description: "Send data test data to SonarQube")
        booleanParam(name: "BUILD_PACKAGES", defaultValue: false, description: "Build Python packages")
        booleanParam(name: 'BUILD_CHOCOLATEY_PACKAGE', defaultValue: true, description: '')
        booleanParam(name: "TEST_PACKAGES_ON_MAC", defaultValue: false, description: "Test Python packages on Mac")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to production devpi on https://devpi.library.illinois.edu/production/release. Master branch Only")
        booleanParam(name: 'DEPLOY_DOCS', defaultValue: false, description: '')
        booleanParam(name: 'DEPLOY_CHOLOCATEY', defaultValue: false, description: 'Deploy to Chocolatey repository')
//         TODO make false
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
            when{
                equals expected: true, actual: params.RUN_CHECKS
            }
            stages{
                stage("Check Code") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
                        }
                    }
                    stages{
                        stage("Configuring Testing Environment"){
                            steps{
                                sh(
                                    label: "Creating logging and report directories",
                                    script: """
                                        mkdir -p logs
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
                                        sh(
                                            label:"Running doctest",
                                            script: """mkdir -p reports/doctests
                                                      coverage run --parallel-mode --source uiucprescon -m sphinx -b doctest -d build/docs/doctrees docs reports/doctest -w logs/doctest.log
                                                      """
                                        )
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
                                            tee("logs/mypy.log"){
                                                sh(
                                                    label: "Run mypy",
                                                    script:"""mkdir -p reports/mypy/html
                                                      mypy -p uiucprescon.getmarc2 --namespace-packages --html-report reports/mypy/html/
                                                      """
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
                                    sh(
                                        label:"Combine Coverage data and generate a report",
                                        script: """mkdir -p reports/coverage
                                                  coverage combine && coverage xml -o reports/coverage.xml
                                                  """
                                    )
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
                stage("Send to Sonarcloud for Analysis"){
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
                            args '--mount source=sonar-cache-uiucprescon-getmarc2,target=/home/user/.sonar/cache'
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
            }
        }
        stage("Distribution Packages"){
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
                stage("Creating Package") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
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
                stage('Testing Packages on mac') {
                    agent {
                        label 'mac'
                    }
                    when{
                        equals expected: true, actual: params.TEST_PACKAGES_ON_MAC
                        beforeAgent true
                    }
                    steps{
                        sh(
                            label:"Installing tox",
                            script: """python3 -m venv venv
                                       venv/bin/python -m pip install pip --upgrade
                                       venv/bin/python -m pip install wheel
                                       venv/bin/python -m pip install --upgrade setuptools
                                       venv/bin/python -m pip install tox
                                       """
                            )
                        unstash "PYTHON_PACKAGES"
                        script{
                            findFiles(glob: "dist/*.tar.gz,dist/*.zip,dist/*.whl").each{
                                sh(
                                    label: "Testing ${it}",
                                    script: "venv/bin/tox --installpkg=${it.path} -e py -vv --recreate"
                                )
                            }
                        }
                    }
                    post{
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'venv/', type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
                stage('Testing all Package') {
                    when{
                        equals expected: true, actual: params.BUILD_PACKAGES
                    }
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
                stage("Chocolatey"){
                    when{
                        anyOf{
                            equals expected: true, actual: params.DEPLOY_CHOCOLATEY
                            equals expected: true, actual: params.BUILD_CHOCOLATEY_PACKAGE
                        }
                        beforeInput true
                    }
                    stages{
                        stage("Package for Chocolatey"){
                            agent {
                                dockerfile {
                                    filename 'ci/docker/chocolatey_package/Dockerfile'
                                    label 'windows && docker'
                                    additionalBuildArgs "--build-arg CHOCOLATEY_SOURCE"
                                  }
                            }
                            steps{
                                script {
                                   unstash "DIST-INFO"
                                    def props = readProperties interpolate: true, file: 'uiucprescon.getmarc2.dist-info/METADATA'
                                    unstash "PYTHON_PACKAGES"
                                    findFiles(glob: "dist/*.whl").each{
                                        def sanitized_packageversion=sanitize_chocolatey_version(props.Version)
                                        powershell(
                                            label: "Configuring new package for Chocolatey",
                                            script: """\$ErrorActionPreference = 'Stop'; # stop on all errors
                                                       choco new getmarc packageversion=${sanitized_packageversion} InstallerFile=${it.path} -t pythonscript --outputdirectory packages
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
                                    stash includes: 'packages/*.nupkg', name: "CHOCOLATEY_PACKAGE"
                                }
                            }
                        }
                        stage("Testing Chocolatey Package"){
                            agent {
                                dockerfile {
                                    filename 'ci/docker/chocolatey_package/Dockerfile'
                                    label 'windows && docker'
                                    additionalBuildArgs "--build-arg CHOCOLATEY_SOURCE"
                                  }
                            }
                            steps{
                                unstash "DIST-INFO"
                                unstash "CHOCOLATEY_PACKAGE"
                                script{
                                    def props = readProperties interpolate: true, file: 'uiucprescon.getmarc2.dist-info/METADATA'
                                    def sanitized_packageversion=sanitize_chocolatey_version(props.Version)
                                    powershell(
                                        label: "installing getmarc",
                                        script:"""\$ErrorActionPreference = 'Stop'; # stop on all errors
                                                  choco install getmarc -y -dv  --version=${sanitized_packageversion} -s './packages/;CHOCOLATEY_SOURCE;chocolatey' --no-progress
                                                  """
                                    )
                                }
                                bat "getmarc --help"

                            }
                            post{
                                success{
                                    archiveArtifacts artifacts: "packages/*.nupkg", fingerprint: true
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
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
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
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL'
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
                                docker.build("getmarc:devpi",'-f ./ci/docker/python/linux/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg PIP_EXTRA_INDEX_URL .').inside{
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
            parallel{
                stage("Deploy to Chocolatey") {
                    when{
                        equals expected: true, actual: params.DEPLOY_CHOLOCATEY
                        beforeInput true
                        beforeAgent true
                    }
                    agent {
                        dockerfile {
                            filename 'ci/docker/chocolatey_package/Dockerfile'
                            label 'windows && docker'
                            additionalBuildArgs "--build-arg CHOCOLATEY_SOURCE"
                          }
                    }
                    input {
                      message 'Select Chocolatey server'
                      parameters {
                        choice choices: ['https://jenkins.library.illinois.edu/nexus/repository/chocolatey-hosted-beta/', 'https://jenkins.library.illinois.edu/nexus/repository/chocolatey-hosted-public/'], description: 'Chocolatey Server to deploy to', name: 'CHOCOLATEY_SERVER'
                        credentials credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl', defaultValue: 'NEXUS_NUGET_API_KEY', description: 'Nuget API key for Chocolatey', name: 'CHOCO_REPO_KEY', required: true
                      }
                    }
                    steps{
                        unstash "CHOCOLATEY_PACKAGE"
                        withCredentials([string(credentialsId: "${CHOCO_REPO_KEY}", variable: 'KEY')]) {
                            bat(
                                label: "Deploying to Chocolatey",
                                script: "choco push packages/getmarc.0.1.0-dev2.nupkg -s %CHOCOLATEY_SERVER% -k %KEY%"
                            )
                        }
                    }
                }
                stage("Deploy Documentation"){
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                        beforeInput true
                    }
                    input {
                        message 'Deploy documentation'
                        id 'DEPLOY_DOCUMENTATION'
                        parameters {
                            string defaultValue: 'getmarc2', description: '', name: 'DEPLOY_DOCS_URL_SUBFOLDER', trim: true
                        }
                    }
                    agent any
                    steps{
                        unstash "DOCS_ARCHIVE"
                        sshPublisher(
                            publishers: [
                                sshPublisherDesc(
                                    configName: 'apache-ns - lib-dccuser-updater',
                                    transfers: [
                                        sshTransfer(
                                            cleanRemote: false,
                                            excludes: '',
                                            execCommand: '',
                                            execTimeout: 120000,
                                            flatten: false,
                                            makeEmptyDirs: false,
                                            noDefaultExcludes: false,
                                            patternSeparator: '[, ]+',
                                            remoteDirectory: "${DEPLOY_DOCS_URL_SUBFOLDER}",
                                            remoteDirectorySDF: false,
                                            removePrefix: 'build/docs/html',
                                            sourceFiles: 'build/docs/html/**'
                                        )
                                    ],
                                    usePromotionTimestamp: false,
                                    useWorkspaceInPromotion: false,
                                    verbose: false
                                )
                            ]
                        )
                    }
                    post{
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: "build/", type: 'INCLUDE'],
                                    [pattern: "dist/", type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
            }
        }
    }
}
