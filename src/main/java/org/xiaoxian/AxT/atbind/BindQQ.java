package org.xiaoxian.AxT.atbind;

import org.xiaoxian.ATBot;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

import static org.xiaoxian.AxT.atbind.GetBindQQ.getBindGroup;
import static org.xiaoxian.AxT.atbind.WhiteListGroup.isInWhiteList;

public class BindQQ {

    public static boolean bindQQAndGroup(long QQ, String number) {
        if (isInWhiteList(number)) {
            return false;
        }

        List<String> bindValues = getBindGroup(QQ);
        if (bindValues.contains(number)) {
            return false;
        }

        File file = new File(ATBot.getDataPath(), "List.txt");
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(file, true))) {
            writer.write(QQ + "=" + number);
            writer.newLine();
            return true;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }
}
