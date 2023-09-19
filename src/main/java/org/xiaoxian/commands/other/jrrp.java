package org.xiaoxian.commands.other;

import net.mamoe.mirai.console.command.CommandSender;
import net.mamoe.mirai.console.command.java.JRawCommand;
import net.mamoe.mirai.message.data.MessageChain;
import org.jetbrains.annotations.NotNull;
import org.xiaoxian.ATBot;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Properties;
import java.util.Random;


public final class jrrp extends JRawCommand {
    public static final jrrp INSTANCE = new jrrp();
    public static String jrrpFilePath; // 当前 jrrp 文件路径
    public static String today;

    public jrrp() {
        super(ATBot.INSTANCE, "jrrp");
        setUsage("jrrp"); // 指令
        setDescription("获取今日人品");// help里面的描述
        setPrefixOptional(false); // 指令前缀 "/"
    }

    // 控制台命令监听
    @Override
    public void onCommand(@NotNull CommandSender sender, @NotNull MessageChain args) {
        sender.sendMessage("请勿在控制台执行此指令！");
        loadJrrpFile();
    }

    public static int getJrrpValue(String QQ) {
        try {
            return getValue(today, QQ);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return -1;
    }

    // 加载 jrrp 文件
    public static void loadJrrpFile() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
        String today = sdf.format(new Date());
        //jrrpFilePath = jrrpDirPath + File.separator + today + ".txt";
        File file = new File(jrrpFilePath);

        // 如果 jrrp 文件不存在，则创建一个空的 ini 文件
        if (!file.exists()) {
            try {
                file.createNewFile();
                System.out.println("创建新人品值文件: " + jrrpFilePath);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public static int getValue(String section, String key) throws IOException {
        Properties prop = new Properties();
        File file = new File(jrrpFilePath);
        if (file.exists()) {
            FileInputStream fis = new FileInputStream(file);
            prop.load(fis);
            fis.close();
        }
        String value = prop.getProperty(section + "." + key);
        if (value == null) {
            // 生成一个0-100的随机数
            Random random = new Random();
            int randomValue = random.nextInt(101);
            // 将随机数写入配置文件
            setValue(section, key, String.valueOf(randomValue));
            return randomValue;
        } else {
            return Integer.parseInt(value);
        }
    }

    public static void setValue(String section, String key, String value) throws IOException {
        Properties prop = new Properties();
        prop.setProperty(section + "." + key, value);
        FileOutputStream fos = new FileOutputStream(jrrpFilePath);
        prop.store(fos, null);
        fos.close();
    }

    public static void clearJrrp() throws IOException {
        Properties prop = new Properties();
        FileOutputStream fos = new FileOutputStream(jrrpFilePath);
        prop.store(fos, null);
        fos.close();
    }
}
