package org.xiaoxian.commands;

import net.mamoe.mirai.Bot;
import net.mamoe.mirai.console.command.CommandSender;
import net.mamoe.mirai.console.command.java.JRawCommand;
import net.mamoe.mirai.message.data.MessageChain;
import org.jetbrains.annotations.NotNull;
import org.xiaoxian.ATBot;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.xiaoxian.ATBot.*;

public final class ATinfo extends JRawCommand {
    public static final ATinfo INSTANCE = new ATinfo();
    static String systemName = "";
    static String cpuModel = "";
    static String ramSize = "";
    static String ramUseSize = "";
    static String ramFreeSize = "";
    static String cpuUse = "";
    static String ramUse = "";

    public ATinfo() {
        super(ATBot.INSTANCE, "atinfo");
        setUsage("/atinfo");
        setDescription("查询机器人服务器状态");
        setPrefixOptional(true);
    }

    // 控制台命令监听
    @Override
    public void onCommand(@NotNull CommandSender sender, @NotNull MessageChain args) {
        sender.sendMessage("调用 ATinfo.java");
        System.out.println(onGetBotInfo());
    }

    // 计算运行时间
    public static String setTime() {
        long milliseconds = System.currentTimeMillis() - startTime;
        long seconds = milliseconds / 1000;
        long minutes = seconds / 60;
        long hours = minutes / 60;
        long days = hours / 24;

        long sec = seconds % 60;
        long min = minutes % 60;
        long hr = hours % 24;

        return days + "天 " + hr + "时 " + min + "分 " + sec + "秒";
    }

    // 获取好友数量（默认获取登录的第一个QQ）
    public static int onGetFriendsListNumber() {
        int i = 0;
        try {
            List<Long> bots = onGetBotsList();
            if (bots.size() > 0) {
                i = Bot.getInstance(bots.get(0)).getFriends().getSize();
                return i;
            }
        } catch (NoSuchElementException ignored) {
        }
        return i;
    }

    // 获取群聊数量（默认获取登录的第一个QQ）
    public static int onGetGroupListNumber() {
        int i = 0;
        try {
            List<Long> bots = onGetBotsList();
            if (bots.size() > 0) {
                i = Bot.getInstance(bots.get(0)).getGroups().getSize();
            }
        } catch (NoSuchElementException ignored) {
        }
        return i;
    }

    // 获取所有登录的QQ
    public static List<Long> onGetBotsList() {
        List<Long> botIds = new ArrayList<>();
        for (Bot bot : Bot.getInstances()) {
            botIds.add(bot.getBot().getId());
        }
        return botIds;
    }

    public static long onGetOneQQNumber() {
        long i = 0;
        try {
            List<Long> bots = onGetBotsList();
            if (bots.size() > 0) {
                i = bots.get(0);
            }
        } catch (NoSuchElementException ignored) {
        }
        return i;
    }

    // 获取Windows系统信息
    public static void onGetWinSystemInfo() {
        Process systemNameProcess;
        Process cpuProcess;
        Process ramSizeProcess;
        Process ramFreeSizeProcess;
        Process cpuUseProcess;

        systemName = "";
        cpuModel = "";
        ramSize = "";
        ramUseSize = "";
        ramFreeSize = "";
        cpuUse = "";
        ramUse = "";

        try {
            // CPU型号
            cpuProcess = Runtime.getRuntime().exec("wmic cpu get name");
            // 系统版本名
            systemNameProcess = Runtime.getRuntime().exec("wmic OS get Caption");
            // 总物理内存
            ramSizeProcess = Runtime.getRuntime().exec("wmic os get TotalVisibleMemorySize");
            // 可用物理内存
            ramFreeSizeProcess = Runtime.getRuntime().exec("wmic os get FreePhysicalMemory");
            // CPU使用率
            cpuUseProcess = Runtime.getRuntime().exec("typeperf \"\\Processor Information(_Total)\\% Processor Utility\" -sc 1");

            BufferedReader cpubr = new BufferedReader(new InputStreamReader(cpuProcess.getInputStream()));
            BufferedReader systemNamebr = new BufferedReader(new InputStreamReader(systemNameProcess.getInputStream()));
            BufferedReader ramSizebr = new BufferedReader(new InputStreamReader(ramSizeProcess.getInputStream()));
            BufferedReader ramFreeSizebr = new BufferedReader(new InputStreamReader(ramFreeSizeProcess.getInputStream()));
            BufferedReader cpuUsebr = new BufferedReader(new InputStreamReader(cpuUseProcess.getInputStream()));

            String line;

            // 格式化CPU信息
            while ((line = cpubr.readLine()) != null) {
                if (line.contains("Name")) {
                    continue;
                }
                cpuModel += line.trim();
            }

            // 格式化systemName信息
            while ((line = systemNamebr.readLine()) != null) {
                if (line.contains("Caption")) {
                    continue;
                }
                systemName += line.trim();
            }

            // 格式化ramSize信息
            while ((line = ramSizebr.readLine()) != null) {
                if (line.contains("TotalVisibleMemorySize")) {
                    continue;
                }
                ramSize += line.trim();
            }
            ramSize = String.valueOf(String.format("%.2f",Integer.parseInt(ramSize) / 1024f / 1024f));

            // 格式化ramFreeSize信息
            while ((line = ramFreeSizebr.readLine()) != null) {
                if (line.contains("FreePhysicalMemory")) {
                    continue;
                }
                ramFreeSize += line.trim();
            }
            ramFreeSize = String.valueOf(String.format("%.2f",Integer.parseInt(ramFreeSize) / 1024f / 1024f));

            // 格式化ramUseSize
            ramUseSize = String.format("%.2f", Double.parseDouble(ramSize) - Double.parseDouble(ramFreeSize));

            // 格式化CPU占用率
            while ((line = cpuUsebr.readLine()) != null) {
                if (line.contains("Processor")) {
                    continue;
                }
                cpuUse += line.trim();
            }
            String[] array = cpuUse.split(",");
            cpuUse = array[1];
            cpuUse = cpuUse.replace("\"", "");
            Pattern pattern = Pattern.compile("\\d+\\.\\d+");
            Matcher matcher = pattern.matcher(cpuUse);
            while (matcher.find()) {
                cpuUse = matcher.group();
            }
            cpuUse = String.format("%.2f",Double.parseDouble(cpuUse));

            // 格式化RAM占用率
            ramUse = String.format("%.2f",Double.parseDouble(ramUseSize) / Double.parseDouble(ramSize) * 100);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // 获取Linux系统信息
    public static void onGetLinuxSystemInfo() {
        try {
            // 获取系统名称和版本
            ProcessBuilder osProcessBuilder = new ProcessBuilder("bash", "-c", "cat /etc/os-release | grep PRETTY_NAME");
            Process osProcess = osProcessBuilder.start();
            BufferedReader osbr = new BufferedReader(new InputStreamReader(osProcess.getInputStream()));
            systemName = osbr.readLine().split("=")[1].replace("\"", "").trim();
            if (systemName.contains(" ")) {
                String[] parts = systemName.split(" ");
                systemName = parts[0] + " " + parts[1];
            }

            // 获取CPU型号
            ProcessBuilder cpuProcessBuilder = new ProcessBuilder("bash", "-c", "cat /proc/cpuinfo | grep 'model name' | head -1\n");
            Process cpuProcess = cpuProcessBuilder.start();
            BufferedReader cpubr = new BufferedReader(new InputStreamReader(cpuProcess.getInputStream()));
            cpuModel = cpubr.readLine().split(":")[1].trim();

            // 获取RAM信息
            ProcessBuilder ramProcessBuilder = new ProcessBuilder("bash", "-c", "free -m | grep Mem:");
            Process ramProcess = ramProcessBuilder.start();
            BufferedReader rambr = new BufferedReader(new InputStreamReader(ramProcess.getInputStream()));
            String[] ramParts = rambr.readLine().split("\\s+");
            ramSize = String.format("%.2f", Integer.parseInt(ramParts[1]) / 1024.0);
            ramUseSize = String.format("%.2f", Integer.parseInt(ramParts[2]) / 1024.0);
            rambr.close();
            ramProcess.destroy();

            // 获取CPU使用率
            ProcessBuilder cpuUseProcessBuilder = new ProcessBuilder("bash", "-c", "vmstat | tail -1 | awk '{print $15}'");
            Process cpuUseProcess = cpuUseProcessBuilder.start();
            BufferedReader cpuUsebr = new BufferedReader(new InputStreamReader(cpuUseProcess.getInputStream()));
            cpuUse = String.valueOf(100 - Double.parseDouble(cpuUsebr.readLine().trim()));

            // 计算RAM使用率
            ramUse = String.format("%.2f", (Double.parseDouble(ramUseSize) / Double.parseDouble(ramSize) * 100));

        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    public static String onGetBotInfo() {
        String os = System.getProperty("os.name").toLowerCase();
        System.out.println(os);
        if (os.contains("win")) {
            onGetWinSystemInfo();
        } else if (os.contains("nix") || os.contains("nux") || os.contains("mac")) {
            onGetLinuxSystemInfo();
        }

        return "=====AxTBot=====" +
                "\n系统: " + systemName +
                "\nCPU: " + cpuModel +
                "\nRAM: " + ramUseSize + "/" + ramSize + "GB" +
                "\nCPU使用: " + cpuUse + "%" +
                "\nRAM使用: " + ramUse + "%" +
                "\n\n群聊数: " + onGetGroupListNumber() +
                "\n好友数: " + onGetFriendsListNumber() +
                "\n发送消息数: " + SendMsgNumber +
                "\n接收消息数: " + BackMsgNumber +
                "\n\n正常运行:" +
                "\n" + setTime() +
                "\n======AxTBot v" + atVer + "=====";
    }
}
