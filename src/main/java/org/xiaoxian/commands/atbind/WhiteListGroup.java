package org.xiaoxian.commands.atbind;

import org.xiaoxian.ATBot;

import java.io.*;
import java.util.HashSet;
import java.util.Set;

public class WhiteListGroup {
    private static final Set<String> whiteListGroups = new HashSet<>();

    public static boolean isInWhiteList(String groupNum) {
        return whiteListGroups.contains(groupNum);
    }

    public static boolean addWhiteListGroup(String num) {
        File file = new File(ATBot.getDataPath(), "WhiteListGroup.txt");
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            while ((line = reader.readLine()) != null) {
                whiteListGroups.add(line.trim());
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        if (isInWhiteList(num)) {
            return false;
        }
        whiteListGroups.add(num);

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(file, true))) {
            writer.write(num);
            writer.newLine();
            return true;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }
}