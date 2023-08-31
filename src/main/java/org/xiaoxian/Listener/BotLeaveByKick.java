package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.BotLeaveEvent;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.SendMsgNumber;

public class BotLeaveByKick implements Consumer<BotLeaveEvent> {
    @Override
    public void accept(BotLeaveEvent event) {
        event.getBot().getFriend(1680839).sendMessage("[Leave&Kick] 检测到机器人退出群聊（禁言/被踢）" +
                "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
        SendMsgNumber ++;
    }
}
