package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.BotLeaveEvent;
import org.xiaoxian.data.Config;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.SendMsgNumber;

public class BotLeaveByKick implements Consumer<BotLeaveEvent> {
    @Override
    public void accept(BotLeaveEvent event) {
        switch (Config.getNotify("LeaveGroup")){
            case 0:
                break;
            case 1:
                event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[Leave&Kick] 检测到机器人退出群聊（禁言/被踢）" +
                        "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                SendMsgNumber ++;
                break;
            case 2:
                event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[Leave&Kick] 检测到机器人退出群聊（禁言/被踢）" +
                        "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                SendMsgNumber ++;
                break;
            case 3:
                event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[Leave&Kick] 检测到机器人退出群聊（禁言/被踢）" +
                        "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                SendMsgNumber ++;
                event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[Leave&Kick] 检测到机器人退出群聊（禁言/被踢）" +
                        "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                SendMsgNumber ++;
        }
    }
}
