package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.BotMuteEvent;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.SendMsgNumber;

public class BotMuted implements Consumer<BotMuteEvent> {
    @Override
    public void accept(BotMuteEvent event) {
        if (event.getGroup().getBotMuteRemaining() == 3600) {
            event.getGroup().quit();
            event.getBot().getFriend(1680839).sendMessage("[Mute] 检测到机器人被禁言一天以上（已自动退群）" +
                    "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
            SendMsgNumber ++;
        }
    }
}
