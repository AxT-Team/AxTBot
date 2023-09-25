package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.GroupMessageEvent;
import net.mamoe.mirai.message.data.MessageChain;
import net.mamoe.mirai.message.data.MessageChainBuilder;
import net.mamoe.mirai.message.data.QuoteReply;
import org.xiaoxian.commands.BotInfo;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.BackMsgNumber;
import static org.xiaoxian.ATBot.SendMsgNumber;
import static org.xiaoxian.commands.BotInfo.onGetBotInfo;
import static org.xiaoxian.commands.network.PingCommand.ATPingCommand;

public class GroupMsgListener implements Consumer<GroupMessageEvent> {
    @Override
    public void accept(GroupMessageEvent event) {
        BackMsgNumber++;
        // 提取消息内容
        MessageChain messageChain = event.getMessage();
        String content = messageChain.contentToString();

        // AT info
        if (event.getMessage().contentToString().equals(BotInfo.INSTANCE.getUsage())) {
            MessageChain chain = new MessageChainBuilder()
                    .append(new QuoteReply(event.getMessage())).append(onGetBotInfo())
                    .build();
            event.getGroup().sendMessage(chain);
            SendMsgNumber++;
        }

        // Ping
        if (content.startsWith("/PingCommand ")) {
            MessageChain chain = new MessageChainBuilder()
                    .append(new QuoteReply(event.getMessage())).append("====ATPing====\n").append(ATPingCommand(content.substring(6))).append("\n==Power By UApi&AxT==")
                    .build();
            event.getGroup().sendMessage(chain);
            SendMsgNumber++;
        }
    }
}
