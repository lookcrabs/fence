#!groovy

@Library('cdis-jenkins-lib@refactor/microservices') _

//runPipeline {
//  pipeline = 'microservice'

//  namespaces = [
//    "jenkins-brain",
//    "jenkins-niaid"
//  ]

//  skipDeploy = 'true'
//}

import uchicago.cdis.*
Map pipelineDefinition = [
    myVariable: "hello world"
]

def pl = new MicroservicePipeline()
pl.setup()
pl.execute()