package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.FriendAddEvent;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.SendMsgNumber;

public class FriendAdded implements Consumer<FriendAddEvent> {
    @Override
    public void accept(FriendAddEvent event) {
        if (event.getBot().getGroup(832275338).getMembers().get(event.getFriend().getId()) == null) {
            event.getFriend().sendMessage("检测到您未加入AxT社区群聊\n请加群:832275338或660408793\n加入群聊后在群里发送 /atbind bind [群号] 可邀请机器人至群聊进行使用");
            SendMsgNumber ++;
        }
    }
}
