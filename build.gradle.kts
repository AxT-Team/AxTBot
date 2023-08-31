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
    implementation(files("lib/json-20230227.jar"))
}
tasks.jar {
    from(configurations.runtimeClasspath.get().map { if (it.isDirectory) it else zipTree(it) })
}

