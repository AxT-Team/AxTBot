package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.FriendMessageEvent;
import org.xiaoxian.atcore.ATinfo;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.BackMsgNumber;
import static org.xiaoxian.ATBot.SendMsgNumber;
import static org.xiaoxian.atcore.ATinfo.onGetWinSystemInfo;

public class FriendsMsgListener implements Consumer<FriendMessageEvent> {
    @Override
    public void accept(FriendMessageEvent event) {
        BackMsgNumber ++;

        if (event.getMessage().contentToString().equals(ATinfo.INSTANCE.getUsage())) {
            event.getSender().sendMessage(onGetWinSystemInfo());
            SendMsgNumber ++;
        }

        // ATBot内部使用，与机器人源码无关，可删除
        if (event.getMessage().contentToString().charAt(0) == '/') {
            SendMsgNumber ++;
        }
        if (event.getMessage().contentToString().charAt(0) == '摸') {
            SendMsgNumber ++;
        }
        if (event.getMessage().contentToString().equals("jrrp")) {
            SendMsgNumber ++;
        }
    }
}
