package org.xiaoxian.AxT.Listener;

import net.mamoe.mirai.event.events.FriendMessageEvent;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.BackMsgNumber;
import static org.xiaoxian.ATBot.SendMsgNumber;

public class AxTFriendMsgListener implements Consumer<FriendMessageEvent> {
    @Override
    public void accept(FriendMessageEvent event) {
        BackMsgNumber++;

        // ATBot内部使用，与机器人源码无关，可删除
        if (event.getMessage().contentToString().charAt(0) == '/') {
            SendMsgNumber++;
        }
        if (event.getMessage().contentToString().charAt(0) == '摸') {
            SendMsgNumber++;
        }
        if (event.getMessage().contentToString().equals("jrrp")) {
            SendMsgNumber++;
        }
    }
}
