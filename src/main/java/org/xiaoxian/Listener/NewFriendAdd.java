package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.NewFriendRequestEvent;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.SendMsgNumber;

public class NewFriendAdd implements Consumer<NewFriendRequestEvent> {
    @Override
    public void accept(NewFriendRequestEvent event) {
        event.accept();
        event.getBot().getFriend(1680839).sendMessage("[FriendAdd] 收到一个好友申请（已自动同意）" +
                                                            "\nQQ: " + event.getFromId() + "" +
                                                            "\n附言: " + event.getMessage() +
                                                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
        SendMsgNumber ++;
    }
}
