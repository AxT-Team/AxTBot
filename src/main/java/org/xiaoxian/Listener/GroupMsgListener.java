package org.xiaoxian.Listener;

import net.mamoe.mirai.Bot;
import net.mamoe.mirai.event.events.GroupMessageEvent;
import net.mamoe.mirai.message.data.MessageChain;
import net.mamoe.mirai.message.data.MessageChainBuilder;
import net.mamoe.mirai.message.data.QuoteReply;
import org.xiaoxian.commands.BotInfo;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.BackMsgNumber;
import static org.xiaoxian.ATBot.SendMsgNumber;
import static org.xiaoxian.commands.atbind.BindQQ.bindQQAndGroup;
import static org.xiaoxian.commands.atbind.GetBindQQ.getBindGroup;
import static org.xiaoxian.commands.atbind.WhiteListGroup.addWhiteListGroup;
import static org.xiaoxian.commands.atbind.unBindQQ.*;
import static org.xiaoxian.commands.BotInfo.*;
import static org.xiaoxian.commands.network.ping.ATPingCommand;

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
        if (content.startsWith("/ping ")) {
            MessageChain chain = new MessageChainBuilder()
                    .append(new QuoteReply(event.getMessage())).append("====ATPing====\n").append(ATPingCommand(content.substring(6))).append("\n==Power By UApi&AxT==")
                    .build();
            event.getGroup().sendMessage(chain);
            SendMsgNumber++;
        }

        // ATBot内部使用，与机器人源码无关，可删除
        if (event.getGroup().getId() == 198921528 || event.getGroup().getId() == 832275338 || event.getGroup().getId() == 660408793 || event.getGroup().getId() == 434756847){
            // 用户绑定
            if (content.startsWith("/atbind bind ")) {
                if (content.substring(13).matches("\\d{5,10}")) {
                    if (bindQQAndGroup(event.getSender().getId(), content.substring(13))) {
                        MessageChain chain = new MessageChainBuilder()
                                .append(new QuoteReply(event.getMessage())).append("[AxT绑定] 成功绑定群号: ").append(content.substring(13))
                                .build();
                        event.getGroup().sendMessage(chain);
                    } else {
                        MessageChain chain = new MessageChainBuilder()
                                .append(new QuoteReply(event.getMessage())).append("[AxT绑定] 绑定失败（当前群号已被绑定或在白名单中）")
                                .build();
                        event.getGroup().sendMessage(chain);
                    }
                } else {
                    MessageChain chain = new MessageChainBuilder()
                            .append(new QuoteReply(event.getMessage())).append("[AxT绑定] 绑定失败（提供的内容并非群号）")
                            .build();
                    event.getGroup().sendMessage(chain);
                }
                SendMsgNumber++;
            }

            // 用户解绑
            if (content.startsWith("/atbind unbind ")) {
                if (unBindGroup(event.getSender().getId(),content.substring(15))) {
                    MessageChain chain = new MessageChainBuilder()
                            .append(new QuoteReply(event.getMessage())).append("[AxT绑定] 成功解除绑定 ").append(content.substring(15))
                            .build();
                    event.getGroup().sendMessage(chain);
                    SendMsgNumber++;
                    quitGroup(Bot.getInstance(onGetOneQQNumber()), content.substring(15));
                    MessageChain chain2 = new MessageChainBuilder()
                            .append(new QuoteReply(event.getMessage())).append("[AxT绑定] 成功退出 ").append(content.substring(15))
                            .build();
                    event.getGroup().sendMessage(chain2);
                } else {
                    MessageChain chain = new MessageChainBuilder()
                            .append(new QuoteReply(event.getMessage())).append("[AxT绑定] 当前群号未绑定")
                            .build();
                    event.getGroup().sendMessage(chain);
                }
                SendMsgNumber++;
            }

            // 用户获取绑定列表
            if (content.startsWith("/atbind get ")) {
                MessageChain chain = new MessageChainBuilder()
                            .append(new QuoteReply(event.getMessage())).append("[AxT绑定] 以下是 ").append(content.substring(12)).append(" 所绑定的所有QQ群\n")
                            .append(getBindGroup(Long.parseLong(content.substring(12))).toString())
                            .build();
                event.getGroup().sendMessage(chain);
            }

            // 管理删除所有绑定
            if (content.startsWith("/atbind rmall ")) {
                if (event.getSender().getId() == 1680839) {
                    quitAllBindGroup(Bot.getInstance(onGetOneQQNumber()), event.getSender().getId());
                    if (unBindAllGroup(event.getSender().getId())) {
                        MessageChain chain = new MessageChainBuilder()
                                .append(new QuoteReply(event.getMessage())).append("[AxT绑定系统] 成功删除并退出 ").append(content.substring(14)).append(" 所绑定的所有QQ群")
                                .build();
                        event.getGroup().sendMessage(chain);
                    } else {
                        MessageChain chain = new MessageChainBuilder()
                                .append(new QuoteReply(event.getMessage())).append("[AxT绑定系统] 删除失败(未绑定群号/系统错误)")
                                .build();
                        event.getGroup().sendMessage(chain);
                    }
                } else {
                    MessageChain chain = new MessageChainBuilder()
                            .append(new QuoteReply(event.getMessage())).append("[AxT绑定系统] 您没有权限")
                            .build();
                    event.getGroup().sendMessage(chain);
                }
                SendMsgNumber++;
            }

            // 管理添加白名单
            if (content.startsWith("/atbind addWhiteList ")) {
                if (event.getSender().getId() == 1680839) {
                    if (addWhiteListGroup(content.substring(21))) {
                        MessageChain chain = new MessageChainBuilder()
                                .append(new QuoteReply(event.getMessage())).append("[AxT绑定系统] 成功添加 ").append(content.substring(21)).append(" 至群聊白名单")
                                .build();
                        event.getGroup().sendMessage(chain);
                    } else {
                        MessageChain chain = new MessageChainBuilder()
                                .append(new QuoteReply(event.getMessage())).append("[AxT绑定系统] 当前群号已在白名单")
                                .build();
                        event.getGroup().sendMessage(chain);
                    }
                } else {
                    MessageChain chain = new MessageChainBuilder()
                            .append(new QuoteReply(event.getMessage())).append("[AxT绑定系统] 您没有权限")
                            .build();
                    event.getGroup().sendMessage(chain);
                }
                SendMsgNumber++;
            }
        }

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
