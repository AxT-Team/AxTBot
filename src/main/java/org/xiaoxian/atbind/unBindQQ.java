package org.xiaoxian.atbind;

import net.mamoe.mirai.Bot;
import net.mamoe.mirai.contact.Group;

import java.io.*;
import java.util.List;

import static org.xiaoxian.ATBot.dataPath;
import static org.xiaoxian.atbind.GetBindQQ.getBindGroup;

public class unBindQQ {
    public static boolean unBindAllGroup(long QQ) {
        File file = new File(dataPath, "List.txt");
        File tempFile = new File(dataPath, "temp.txt");

        try (BufferedReader reader = new BufferedReader(new FileReader(file));
             BufferedWriter writer = new BufferedWriter(new FileWriter(tempFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("=");
                if (parts.length == 2 && parts[0].equals(String.valueOf(QQ))) {
                    continue;
                }
                writer.write(line);
                writer.newLine();
            }
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }

        if (!file.delete()) {
            System.out.println("无法删除原始文件");
            return false;
        }
        if (!tempFile.renameTo(file)) {
            System.out.println("temp.txt更名失败，请检查是否有程序占用了temp.txt文件");
            return false;
        }

        return true;
    }

    public static boolean unBindGroup(long QQ, String num) {
        File file = new File(dataPath, "List.txt");
        File tempFile = new File(dataPath, "temp.txt");

        try (BufferedReader reader = new BufferedReader(new FileReader(file));
             BufferedWriter writer = new BufferedWriter(new FileWriter(tempFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("=");
                if (parts.length == 2 && parts[0].equals(String.valueOf(QQ)) && parts[1].equals(num)) {
                    continue;
                }
                writer.write(line);
                writer.newLine();
            }
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }

        if (!file.delete()) {
            System.out.println("无法删除原始文件");
            return false;
        }
        if (!tempFile.renameTo(file)) {
            System.out.println("temp.txt更名失败，请检查是否有程序占用了temp.txt文件");
            return false;
        }

        return true;
    }

    public static void quitGroup(Bot bot, String groupID) {
        bot.getGroup(Long.parseLong(groupID)).quit();
        System.out.println("Bot 已退出群聊 " + groupID + ".");
    }

    public static void quitAllBindGroup(Bot bot, long QQ) {
        List<String> bindGroups = getBindGroup(QQ);
        System.out.println("QQ " + QQ + " 绑定的群聊: " + bindGroups);

        for (String groupNum : bindGroups) {
            long groupId;
            try {
                groupId = Long.parseLong(groupNum);
            } catch (NumberFormatException e) {
                e.printStackTrace();
                continue;
            }

            Group group = bot.getGroup(groupId);
            if (group == null) {
                System.out.println("Bot群聊列表里不存在 " + groupId);
                continue;
            }

            group.quit();
            System.out.println("Bot已退出群聊 " + groupId + ".");
        }
    }

}
