plugins {
    val kotlinVersion = "1.5.30"
    kotlin("jvm") version kotlinVersion
    kotlin("plugin.serialization") version kotlinVersion

    id("net.mamoe.mirai-console") version "2.12.3"
}

group = "org.xiaoxian"
version = "2.0"

repositories {
    maven("https://maven.aliyun.com/repository/public")
    mavenCentral()
}

dependencies {
    implementation(files("lib/json.jar"))
    implementation(files("lib/snakeyaml-2.2.jar"))
    implementation(files("lib/mysql-connector-j-8.1.0.jar"))
}

tasks.jar {
    from(
        configurations.runtimeClasspath.get().map {
            if (it.isDirectory)
                it
            else
                zipTree(it)
        }
    )
}