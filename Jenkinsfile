pipeline {
    agent none
    parameters {
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
//         booleanParam(name: "USE_SONARQUBE", defaultValue: true, description: "Send data test data to SonarQube")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to production devpi on https://devpi.library.illinois.edu/production/release. Master branch Only")
    }
    stages {
        stage("Getting Distribution Info"){
            agent {
                dockerfile {
                    filename 'ci/docker/python/linux/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
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
        stage("Test") {
            agent {
                dockerfile {
                    filename 'ci/docker/python/linux/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
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
                        stage("Run PyTest Unit Tests"){
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
//                         stage("Run Doctest Tests"){
//                             steps {
//                                 sh "coverage run --parallel-mode --source uiucprescon -m sphinx -b doctest -d build/docs/doctrees docs/source reports/doctest -w logs/doctest.log"
//                             }
//                             post{
//                                 always {
//                                     archiveArtifacts artifacts: 'reports/doctest/output.txt'
//                                     archiveArtifacts artifacts: 'logs/doctest.log'
//                                     recordIssues(tools: [sphinxBuild(name: 'Sphinx Doctest', pattern: 'logs/doctest.log', id: 'doctest')])
//                                 }
//
//                             }
//                         }
                        stage("Run MyPy Static Analysis") {
                            steps{
                                catchError(buildResult: 'SUCCESS', message: 'mypy found issues', stageResult: 'UNSTABLE') {
                                    sh "mypy -p uiucprescon --html-report reports/mypy/html/  | tee logs/mypy.log"
                                }
                            }
                            post {
                                always {
                                    recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                }
                            }
                        }
                        stage("Run Tox test") {
                            when{
                                equals expected: true, actual: params.TEST_RUN_TOX
                            }
                            steps {
                                sh "tox -e py"

                            }
                        }
                        stage("Run Bandit Static Analysis") {
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
                                    archiveArtifacts "reports/bandit-report.json"
                                    stash includes: "reports/bandit-report.json", name: 'BANDIT_REPORT'
                                }
                            }
                        }
                        stage("Run Pylint Static Analysis") {
                            steps{
                                withEnv(['PYLINTHOME=.']) {
                                    catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                        sh(
                                            script: '''mkdir -p logs
                                                       mkdir -p reports
                                                       pylint uiucprescon -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint.txt
                                                       ''',
                                            label: "Running pylint"
                                        )
                                    }
                                    sh(
                                        script: 'pylint uiucprescon  -r n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt',
                                        label: "Running pylint for sonarqube",
                                        returnStatus: true
                                    )
                                }
                            }
                            post{
                                always{
                                    stash includes: "reports/pylint_issues.txt,reports/pylint.txt", name: 'PYLINT_REPORT'
                                    archiveArtifacts allowEmptyArchive: true, artifacts: "reports/pylint.txt"
                                    recordIssues(tools: [pyLint(pattern: 'reports/pylint.txt')])
                                }
                            }
                        }
                        stage("Run Flake8 Static Analysis") {
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
                    cleanWs(patterns: [
                            [pattern: 'reports/coverage.xml', type: 'INCLUDE'],
                            [pattern: 'reports/coverage', type: 'INCLUDE'],
                        ])
                }
            }
        }
    }
}