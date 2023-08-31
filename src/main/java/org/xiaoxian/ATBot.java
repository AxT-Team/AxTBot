package org.xiaoxian;

import net.mamoe.mirai.Bot;
import net.mamoe.mirai.console.MiraiConsole;
import net.mamoe.mirai.console.command.CommandManager;
import net.mamoe.mirai.console.plugin.jvm.JavaPlugin;
import net.mamoe.mirai.console.plugin.jvm.JvmPluginDescriptionBuilder;
import net.mamoe.mirai.event.GlobalEventChannel;
import net.mamoe.mirai.event.events.*;
import org.xiaoxian.Listener.*;
import org.xiaoxian.atcore.ATinfo;
import org.xiaoxian.other.ATChatGPT;
import org.xiaoxian.other.jrrp;

import java.io.File;

import static org.xiaoxian.atbind.unBindQQ.*;
import static org.xiaoxian.atcore.ATinfo.onGetOneQQNumber;
import static org.xiaoxian.other.jrrp.jrrpFilePath;
import static org.xiaoxian.other.jrrp.loadJrrpFile;

public final class ATBot extends JavaPlugin {
    public static final ATBot INSTANCE = new ATBot();
    public static String dataPath;
    public static String jrrpDirPath;
    public static int BackMsgNumber = 0;
    public static int SendMsgNumber = 0;
    public static long startTime = 0;
    public static String atVer = "2.0";

    private ATBot() {
        super(new JvmPluginDescriptionBuilder("org.xiaoxian.ATBot", "2.0")
                .name("AxTBot")
                .author("XiaoXian")
                .build());
    }

    @Override
    public void onEnable() {
        getLogger().info("———————————————————————————");
        getLogger().info("AxTBot v" + atVer + " Loading...");
        getLogger().info("Author: XiaoXian");
        getLogger().info("Email: xiaoxian@axtn.net");
        getLogger().info("———————————————————————————");

        CommandManager.INSTANCE.registerCommand(new ATinfo(),true);
        CommandManager.INSTANCE.registerCommand(new jrrp(),true);
        CommandManager.INSTANCE.registerCommand(new ATChatGPT(),true);

        // 获取数据目录
        String dataDir = MiraiConsole.INSTANCE.getPluginManager().getPluginsDataPath().toString();
        File folder = new File(dataDir, "org.xiaoxian.atbot");
        if (!folder.exists()) {
            folder.mkdirs();
        }
        dataPath = folder.getAbsolutePath();
        getLogger().info("AxTBot数据存储目录: " + dataPath);

        // 人品值数据目录
        File folder2 = new File(dataPath, "jrrp");
        if (!folder2.exists()) {
            folder2.mkdirs();
        }
        jrrpDirPath = folder.getAbsolutePath();
        getLogger().info("人品值数据存储目录: " + jrrpDirPath);

        // 每日人品值加载
        loadJrrpFile();
        getLogger().info("今日人品值存储路径: " + jrrpFilePath);
        getLogger().info("———————————————————————————");

        // 消息监听处理
        GlobalEventChannel.INSTANCE.subscribeAlways(FriendMessageEvent.class,new FriendsMsgListener());
        getLogger().info("[事件] 注册好友消息监听Event（FriendMessageEvent.class）");
        GlobalEventChannel.INSTANCE.subscribeAlways(GroupMessageEvent.class,new GroupMsgListener());
        getLogger().info("[事件] 注册群聊消息监听Event（GroupMessageEvent.class）");

        // 好友添加监听处理
        GlobalEventChannel.INSTANCE.subscribeAlways(FriendAddEvent.class,new FriendAdded());
        getLogger().info("[事件] 注册好友添加监听Event（FriendAddEvent.class）");
        GlobalEventChannel.INSTANCE.subscribeAlways(NewFriendRequestEvent.class,new NewFriendAdd());
        getLogger().info("[事件] 注册好友请求监听Event（NewFriendRequestEvent.class）");

        // 群邀请监听处理
        GlobalEventChannel.INSTANCE.subscribeAlways(BotInvitedJoinGroupRequestEvent.class,new InvitedJoinGroup());
        getLogger().info("[事件] 注册群聊邀请监听Event（BotInvitedJoinGroupRequestEvent.class）");

        // 机器人被禁言监听处理
        GlobalEventChannel.INSTANCE.subscribeAlways(BotMuteEvent.class,new BotMuted());
        getLogger().info("[事件] 注册群聊禁言监听Event（BotMuteEvent.class）");

        // 机器人退群监听处理
        GlobalEventChannel.INSTANCE.subscribeAlways(BotLeaveEvent.class,new BotLeaveByKick());
        getLogger().info("[事件] 注册群聊退群监听Event（BotLeaveEvent.class）");
        getLogger().info("———————————————————————————");

        // 授权事件
        GlobalEventChannel.INSTANCE.subscribeAlways(MemberLeaveEvent.class, event -> {
            if (event instanceof MemberLeaveEvent.Kick || event instanceof MemberLeaveEvent.Quit) {
                if (event.getGroup().getId() == 832275338 || event.getGroup().getId() == 660408793) {
                    unBindAllGroup(event.getMember().getId());
                    quitAllBindGroup(Bot.getInstance(onGetOneQQNumber()), event.getMember().getId());
                }
            }
        });

        startTime = System.currentTimeMillis();
    }

    @Override
    public void onDisable() {
        CommandManager.INSTANCE.unregisterAllCommands(ATBot.INSTANCE);
        getLogger().info("AxTBot v" + atVer + " Disable");
        getLogger().info("Thanks for using!");
    }
}