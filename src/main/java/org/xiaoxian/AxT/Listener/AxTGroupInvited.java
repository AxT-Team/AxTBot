package org.xiaoxian.AxT.Listener;

import net.mamoe.mirai.event.events.BotInvitedJoinGroupRequestEvent;

import java.util.function.Consumer;

import static org.xiaoxian.AxT.atbind.GetBindQQ.isGroupBindByQQ;

public class AxTGroupInvited implements Consumer<BotInvitedJoinGroupRequestEvent> {
    @Override
    public void accept(BotInvitedJoinGroupRequestEvent event) {
        if (event.getBot().getGroup(832275338).getMembers().get(event.getInvitorId()) == null && event.getBot().getGroup(660408793).getMembers().get(event.getInvitorId()) == null) {
            event.getInvitor().sendMessage("检测到您未加入AxT社区群聊\n请加群:832275338或660408793\n并根据提示发送 /atbind bind [群号] 即可邀请");
            event.getBot().getFriend(1680839).sendMessage("[GroupInvite] 收到一个群邀请（未加群，已忽略）" +
                    "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                    "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
        } else {
            if (!isGroupBindByQQ(event.getInvitorId(), String.valueOf(event.getGroupId()))) {
                event.getInvitor().sendMessage("检测到您未绑定相关群号\n请在群里发送 /atbind bind [群号] 才可邀请");
                event.getBot().getFriend(1680839).sendMessage("[GroupInvite] 收到一个群邀请（已加群，未绑定）" +
                        "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                        "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");

            } else {
                event.accept();
                event.getInvitor().sendMessage("已检测到绑定的群号\n已自动同意您的邀请申请");
                event.getBot().getFriend(1680839).sendMessage("[GroupInvite] 收到一个群邀请（已绑定，自动通过）" +
                        "\nQQ: " + event.getInvitorNick() +  "(" + event.getInvitorId() + ")" +
                        "\n受邀请群: " + event.getGroupName() + "(" + event.getGroupId() + ")");
            }
        }
    }
}
