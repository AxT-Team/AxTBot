package org.xiaoxian.atbind;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static org.xiaoxian.ATBot.dataPath;

public class GetBindQQ {
    public static boolean isGroupBindByQQ(long QQ, String num) {
        List<String> bindValues = getBindGroup(QQ);
        return bindValues.contains(num);
    }

    public static List<String> getBindGroup(long QQ) {
        List<String> bindValues = new ArrayList<>();
        File file = new File(dataPath, "List.txt");
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("=");
                if (parts.length == 2 && parts[0].equals(String.valueOf(QQ))) {
                    bindValues.add(parts[1]);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return bindValues;
    }
}
