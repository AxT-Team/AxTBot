package org.xiaoxian.atcore;

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

    public ATinfo() {
        super(ATBot.INSTANCE, "atinfo");
        setUsage("/atinfo"); // 指令
        setDescription("查询机器人服务器状态");// help里面的描述
        setPrefixOptional(true); // 指令前缀 "/"
    }

    // 控制台命令监听
    @Override
    public void onCommand(@NotNull CommandSender sender, @NotNull MessageChain args) {
        sender.sendMessage("机器人状态正常");
        System.out.println(onGetWinSystemInfo());
        List<Long> bots = onGetBotsList();
        Bot.getInstance(bots.get(0)).getFriend(1680839).sendMessage("Test Friend Msg");
        Bot.getInstance(bots.get(0)).getGroup(198921528).sendMessage("Test Group Msg");
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

    // 获取Windows系统信息及机器人信息
    public static String onGetWinSystemInfo() {
        Process systemNameProcess;
        Process cpuProcess;
        Process ramSizeProcess;
        Process ramFreeSizeProcess;
        Process cpuUseProcess;

        String systemName = "";
        String cpuModel = "";
        String ramSize = "";
        String ramUseSize = "";
        String ramFreeSize = "";
        String cpuUse = "";
        String ramUse = "";

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
