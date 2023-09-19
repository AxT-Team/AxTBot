package org.xiaoxian.data;

import org.xiaoxian.ATBot;
import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.Map;

public class ConfigManager {

    private static final Yaml yaml;

    static {
        DumperOptions options = new DumperOptions();
        options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
        options.setPrettyFlow(true);
        yaml = new Yaml(options);
    }

    // 加载配置（启动流程）
    public static void loadConfig() throws IOException {
        if (!new File(getConfigFilePath()).exists()) {
            // 创建默认配置文件
            InputStream defaultConfigStream = ConfigManager.class.getClassLoader().getResourceAsStream("config.yml");
            if (defaultConfigStream != null) {
                Files.copy(defaultConfigStream, new File(getConfigFilePath()).toPath(), StandardCopyOption.REPLACE_EXISTING);
                defaultConfigStream.close();
            }
        }

        Config.setAdminQQ(Long.parseLong(getConfig("AdminQQ")));
        Config.setAdminGroupQQ(Long.parseLong(getConfig("AdminGroupQQ")));
        Config.setDataType(Integer.parseInt(getConfig("DataType")));
        if (Config.getDataType() == 1) {
            Config.setMySQL(getConfig("Host"), Integer.parseInt(getConfig("Port")), getConfig("Database"), getConfig("User"), getConfig("Pass"));
        }
        Config.setNotify("NewFriendAdd", Integer.parseInt(getConfig("NewFriendAdd")));
        Config.setNotify("Mute", Integer.parseInt(getConfig("Mute")));
        Config.setNotify("GroupInvited", Integer.parseInt(getConfig("GroupInvited")));
        Config.setNotify("LeaveGroup", Integer.parseInt(getConfig("LeaveGroup")));
    }

    // 设置配置文件
    public static void setConfig(String setting, Object value) throws IOException {
        try (FileInputStream fis = new FileInputStream(getConfigFilePath())) {
            Map<String, Object> config = yaml.load(fis);
            config.put(setting, value);
            try (FileWriter writer = new FileWriter(getConfigFilePath())) {
                yaml.dump(config, writer);
            }
        }
    }

    // 获取配置文件数值
    public static String getConfig(String setting) throws IOException {
        try (FileInputStream fis = new FileInputStream(getConfigFilePath())) {
            Map<String, Object> config = yaml.load(fis);
            Object value = config.get(setting);
            return value.toString();
        }
    }

    private static String getConfigFilePath() {
        return ATBot.getConfigPath() + "\\config.yml";
    }
}
