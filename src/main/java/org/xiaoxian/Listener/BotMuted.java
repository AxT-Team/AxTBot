package org.xiaoxian.Listener;

import net.mamoe.mirai.event.events.BotMuteEvent;
import org.xiaoxian.data.Config;

import java.util.function.Consumer;

import static org.xiaoxian.ATBot.SendMsgNumber;

public class BotMuted implements Consumer<BotMuteEvent> {
    @Override
    public void accept(BotMuteEvent event) {
        if (Config.getMuteLeave()) {
            if (event.getGroup().getBotMuteRemaining() == Config.getMuteTime()) {
                event.getGroup().quit();
                switch (Config.getNotify("Mute")) {
                    case 0:
                        break;
                    case 1:
                        event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[Mute] 检测到机器人被禁言 " + event.getGroup().getBotMuteRemaining() + "s（已自动退群）" +
                                "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                        SendMsgNumber ++;
                    case 2:
                        event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[Mute] 检测到机器人被禁言 " + event.getGroup().getBotMuteRemaining() + "s（已自动退群）" +
                                "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                        SendMsgNumber ++;
                    case 3:
                        event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[Mute] 检测到机器人被禁言 " + event.getGroup().getBotMuteRemaining() + "s（已自动退群）" +
                                "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                        SendMsgNumber ++;
                        event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[Mute] 检测到机器人被禁言 " + event.getGroup().getBotMuteRemaining() + "s（已自动退群）" +
                                "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                        SendMsgNumber ++;
                }
            }
        } else {
            switch (Config.getNotify("Mute")) {
                case 0:
                    break;
                case 1:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[Mute] 检测到机器人被禁言 " + event.getGroup().getBotMuteRemaining() + "秒" +
                            "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                case 2:
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[Mute] 检测到机器人被禁言 " + event.getGroup().getBotMuteRemaining() + "秒" +
                            "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                case 3:
                    event.getBot().getFriend(Config.getAdminQQ()).sendMessage("[Mute] 检测到机器人被禁言 " + event.getGroup().getBotMuteRemaining() + "秒" +
                            "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
                    event.getBot().getGroup(Config.getAdminGroupQQ()).sendMessage("[Mute] 检测到机器人被禁言 " + event.getGroup().getBotMuteRemaining() + "秒" +
                            "\n群: " + event.getGroup().getName() +  "(" + event.getGroupId() + ")");
                    SendMsgNumber ++;
            }
        }
    }
}
