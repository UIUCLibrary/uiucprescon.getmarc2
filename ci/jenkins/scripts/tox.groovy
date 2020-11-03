def getToxEnvs(){
    def envs
    if(isUnix()){
        envs = sh(returnStdout: true, script: "tox -l").trim().split('\n')
    } else{
        envs = bat(returnStdout: true, script: "@tox -l").trim().split('\n')
    }
    envs.collect{
        it.trim()
    }
    return envs
}
def generateToxPackageReport(testEnv){

        def packageReport = "\n**Installed Packages:**"
        testEnv['installed_packages'].each{
            packageReport =  packageReport + "\n ${it}"
        }

        return packageReport
}

def getBasicToxMetadataReport(toxResultFile){
    def tox_result = readJSON(file: toxResultFile)
    def testingEnvReport = """# Testing Environment

**Tox Version:** ${tox_result['toxversion']}
**Platform:**   ${tox_result['platform']}
"""
    return testingEnvReport
}
def getPackageToxMetadataReport(tox_env, toxResultFile){
    def tox_result = readJSON(file: toxResultFile)

    if(! tox_result['testenvs'].containsKey(tox_env)){
        def w = tox_result['testenvs']
        echo "${w}"
        tox_result['testenvs'].each{key, test_env->
            echo "${test_env}"
            test_env.each{
                echo "${it}"
                echo "${it.getClass()}"
            }
        }
        error "No test env for ${tox_env} found in ${toxResultFile}"
    }
    def tox_test_env = tox_result['testenvs'][tox_env]
    def packageReport = generateToxPackageReport(tox_test_env)
    return packageReport
}

def generateToxReport(tox_env, toxResultFile){
    if(!fileExists(toxResultFile)){
        error "No file found for ${toxResultFile}"
    }
    def testingEnvReport = getBasicToxMetadataReport(toxResultFile)
    def packageReport
    try{
        packageReport = getPackageToxMetadataReport(tox_env, toxResultFile)
    }catch(e){
        packageReport = ""
    }
    echo "packageReport = ${packageReport}"
    try{
        def errorMessages = []
        try{
            testEnv["test"].each{
                if (it['retcode'] != 0){
                    echo "Found error ${it}"
                    def errorOutput =  it['output']
                    def failedCommand = it['command']
                    errorMessages += "**${failedCommand}**\n${errorOutput}"
                }
            }
        }
        catch (e) {
            echo "unable to parse Error output: Reason ${e}"
            throw e
        }
        def resultsReport = "# Results"
        if (errorMessages.size() > 0){
            resultsReport = resultsReport + "\n" + errorMessages.join("\n") + "\n"
        } else{
            resultsReport = resultsReport + "\n" + "Success\n"
        }
//         =========
        checksReportText = testingEnvReport + " \n" + resultsReport
        return checksReportText
    } catch (e){
        echo "Unable to parse json file, Falling back to reading the file as text. \nReason: ${e}"
        def data =  readFile(toxResultFile)
        data = "``` json\n${data}\n```"
        return data
    }
}

def getToxTestsParallel(envNamePrefix, label, dockerfile, dockerArgs){
    script{
        def TOX_RESULT_FILE_NAME = "tox_result.json"
        def envs
        def originalNodeLabel
        node(label){
            originalNodeLabel = env.NODE_NAME
            checkout scm
            def dockerImageName = "tox${currentBuild.projectName}".replaceAll("-", "").toLowerCase()
            def dockerImage = docker.build(dockerImageName, "-f ${dockerfile} ${dockerArgs} .")
            dockerImage.inside{
                envs = getToxEnvs()
            }
            if(isUnix()){
                sh(
                    label: "Removing Docker Image used to run tox",
                    script: "docker image ls ${dockerImageName}"
                )
            } else {
                bat(
                    label: "Removing Docker Image used to run tox",
                    script: """docker image ls ${dockerImageName}
                               """
                )
            }
        }
        echo "Found tox environments for ${envs.join(', ')}"
        def dockerImageForTesting
        node(originalNodeLabel){
            def dockerImageName = "tox"
            checkout scm
            dockerImageForTesting = docker.build(dockerImageName, "-f ${dockerfile} ${dockerArgs} . ")

        }
        echo "Adding jobs to ${originalNodeLabel} with ${dockerImageForTesting}"
        def jobs = envs.collectEntries({ tox_env ->
            def tox_result
            def githubChecksName = "Tox: ${tox_env} ${envNamePrefix}"
            def jenkinsStageName = "${envNamePrefix} ${tox_env}"

            [jenkinsStageName,{
                node(originalNodeLabel){
                    ws{
                        checkout scm
                        dockerImageForTesting.inside{
                            try{
                                publishChecks(
                                    conclusion: 'NONE',
                                    name: githubChecksName,
                                    status: 'IN_PROGRESS',
                                    summary: 'Use Tox to test installed package',
                                    title: 'Running Tox'
                                )
                                if(isUnix()){
                                    sh(
                                        label: "Running Tox with ${tox_env} environment",
                                        script: "tox  -vv --parallel--safe-build --result-json=${TOX_RESULT_FILE_NAME} -e $tox_env"
                                    )
                                } else {
                                    bat(
                                        label: "Running Tox with ${tox_env} environment",
                                        script: "tox  -vv --parallel--safe-build --result-json=${TOX_RESULT_FILE_NAME} -e $tox_env "
                                    )
                                }
                            } catch (e){
                                def text
                                try{
                                    text = generateToxReport(tox_env, 'tox_result.json')
                                }
                                catch (ex){
                                    text = "No details given. Unable to read tox_result.json"
                                }
                                publishChecks(
                                    name: githubChecksName,
                                    summary: 'Use Tox to test installed package',
                                    text: text,
                                    conclusion: 'FAILURE',
                                    title: 'Failed'
                                )
                                throw e
                            }
                            def checksReportText = generateToxReport(tox_env, 'tox_result.json')
                            echo "publishing \n${checksReportText}"
                            publishChecks(
                                    name: githubChecksName,
                                    summary: 'Use Tox to test installed package',
                                    text: "${checksReportText}",
                                    title: 'Passed'
                                )
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: TOX_RESULT_FILE_NAME, type: 'INCLUDE'],
                                    [pattern: ".tox/", type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
            }]
        })
        return jobs
    }
}
return this