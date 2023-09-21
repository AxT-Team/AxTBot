package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.NewFriendRequestEvent;
import org.xiaoxian.data.Config;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.SendMsgNumber;

public class NewFriendAdd implements Consumer<NewFriendRequestEvent> {
    @Override
    public void accept(NewFriendRequestEvent event) {
        if (Config.getAutoNewFriendAdd()) {
            event.accept();
            switch (Config.getNotify("NewFriendAdd")) {
                case 0:
                    break;
                case 1:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[FriendAdd] 收到一个好友申请（已自动同意）" +
                            "\nQQ: " + event.getFromId() + "" +
                            "\n附言: " + event.getMessage() +
                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
                    SendMsgNumber ++;
                case 2:
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[FriendAdd] 收到一个好友申请（已自动同意）" +
                            "\nQQ: " + event.getFromId() + "" +
                            "\n附言: " + event.getMessage() +
                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
                    SendMsgNumber ++;
                case 3:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[FriendAdd] 收到一个好友申请（已自动同意）" +
                            "\nQQ: " + event.getFromId() + "" +
                            "\n附言: " + event.getMessage() +
                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
                    SendMsgNumber ++;
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[FriendAdd] 收到一个好友申请（已自动同意）" +
                            "\nQQ: " + event.getFromId() + "" +
                            "\n附言: " + event.getMessage() +
                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
                    SendMsgNumber ++;
            }
            switch (Config.getNotify("NewFriendAdd")) {
                case 0:
                    break;
                case 1:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[FriendAdd] 收到一个好友申请" +
                            "\nQQ: " + event.getFromId() + "" +
                            "\n附言: " + event.getMessage() +
                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
                    SendMsgNumber ++;
                case 2:
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[FriendAdd] 收到一个好友申请" +
                            "\nQQ: " + event.getFromId() + "" +
                            "\n附言: " + event.getMessage() +
                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
                    SendMsgNumber ++;
                case 3:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[FriendAdd] 收到一个好友申请" +
                            "\nQQ: " + event.getFromId() + "" +
                            "\n附言: " + event.getMessage() +
                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
                    SendMsgNumber ++;
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[FriendAdd] 收到一个好友申请" +
                            "\nQQ: " + event.getFromId() + "" +
                            "\n附言: " + event.getMessage() +
                            "\n来自群: " + event.getFromGroup().getName() + "(" + event.getFromGroupId() + ")");
                    SendMsgNumber ++;
            }
        }
    }
}
