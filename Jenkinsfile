pipeline {
    agent any
    
    parameters {
        string(name: 'GAME_VERSION', defaultValue: '1.0.0', description: '游戏版本号')
        choice(name: 'GAME_TYPE', choices: ['release', 'debug'], description: '构建类型')
        string(name: 'CONFIG_PATH', defaultValue: 'buildConfig_android.json', description: '构建配置文件路径')
        string(name: 'CREATOR_PATH', defaultValue: 'C:/ProgramData/cocos/editors/Creator/3.6.3/CocosCreator.exe', description: 'Cocos Creator路径')
        string(name: 'PROJECT_PATH', defaultValue: 'D:/work/Game363', description: '项目路径')
    }

    options {
        // 设置构建保留天数和个数
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // 禁止同时运行
        disableConcurrentBuilds()
        // 添加构建时间戳
        timestamps()
    }
    
    stages {
        stage('准备环境') {
            steps {
                echo "====== 开始构建流程 ======"
                echo "构建版本: ${params.GAME_VERSION}"
                echo "构建类型: ${params.GAME_TYPE}"
                echo "配置文件: ${params.CONFIG_PATH}"
                
                ws('D:/work/GameBuildScript') {
                    script {
                        // 构造参数 JSON 内容
                        def paramsMap = [
                            game_version: params.GAME_VERSION, 
                            game_type: params.GAME_TYPE,
                            config_path: params.CONFIG_PATH,
                            creator_path: params.CREATOR_PATH,
                            project_path: params.PROJECT_PATH
                        ]
                        def jsonText = groovy.json.JsonOutput.prettyPrint(
                            groovy.json.JsonOutput.toJson(paramsMap)
                        )

                        // 写入 build_params.json 文件
                        writeFile file: 'build_params.json', text: jsonText
                        echo "参数已保存到 build_params.json：\n${jsonText}"
                    }
                }
            }
        }
        
        stage('Git 更新') {
            steps {
                ws('D:/work/GameBuildScript') {
                    echo "====== 开始 Git 更新 ======"
                    bat "run_git_update.bat"
                    echo "Git 更新阶段完成"
                }
            }
        }
        
        stage('Cocos 工程生成') {
            steps {
                ws('D:/work/GameBuildScript') {
                    echo "====== 开始 Cocos 工程生成 ======"
                    bat "run_cocos_build.bat"
                    echo "Cocos 工程生成阶段完成"
                }
            }
        }
        
        stage('APK 打包生成') {
            steps {
                ws('D:/work/GameBuildScript') {
                    echo "====== 开始 APK 打包生成 ======"
                    bat "run_apk_build.bat"
                    echo "APK 打包生成阶段完成"
                }
            }
        }
        
        stage('构建结果验证') {
            steps {
                ws('D:/work/GameBuildScript') {
                    echo "====== 验证构建结果 ======"
                    bat "run_verify_build.bat"
                    echo "构建结果验证完成"
                }
            }
        }
    }
    
    post {
        success {
            echo "构建成功！✅"
            echo "游戏版本: ${params.GAME_VERSION}"
            echo "构建类型: ${params.GAME_TYPE}"
        }
        failure {
            echo "构建失败！❌"
        }
        always {
            echo "==========================="
            echo "构建结束时间: ${new Date().format('yyyy-MM-dd HH:mm:ss')}"
            echo "==========================="
        }
    }
} 