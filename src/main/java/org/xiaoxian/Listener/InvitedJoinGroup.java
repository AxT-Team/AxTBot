package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.BotInvitedJoinGroupRequestEvent;
import org.xiaoxian.data.Config;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.SendMsgNumber;

public class InvitedJoinGroup implements Consumer<BotInvitedJoinGroupRequestEvent> {
    @Override
    public void accept(BotInvitedJoinGroupRequestEvent event) {
        if (Config.getAutoGroupInvited()) {
            event.accept();
            switch (Config.getNotify("GroupInvited")) {
                case 0:
                    break;
                case 1:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[GroupInvite] 收到一个群邀请（已自动同意）" +
                            "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                            "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                case 2:
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[GroupInvite] 收到一个群邀请（已自动同意）" +
                            "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                            "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                case 3:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[GroupInvite] 收到一个群邀请（已自动同意）" +
                            "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                            "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[GroupInvite] 收到一个群邀请（已自动同意）" +
                            "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                            "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
            }
        } else {
            switch (Config.getNotify("GroupInvited")) {
                case 0:
                    break;
                case 1:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[GroupInvite] 收到一个群邀请" +
                            "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                            "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                case 2:
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[GroupInvite] 收到一个群邀请" +
                            "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                            "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                case 3:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[GroupInvite] 收到一个群邀请" +
                            "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                            "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[GroupInvite] 收到一个群邀请" +
                            "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                            "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
            }
        }
    }
}
