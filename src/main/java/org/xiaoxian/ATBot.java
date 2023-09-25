package org.xiaoxian;

import net.mamoe.mirai.Bot;
import net.mamoe.mirai.console.MiraiConsole;
import net.mamoe.mirai.console.command.CommandManager;
import net.mamoe.mirai.console.plugin.jvm.JavaPlugin;
import net.mamoe.mirai.console.plugin.jvm.JvmPluginDescriptionBuilder;
import net.mamoe.mirai.event.GlobalEventChannel;
import net.mamoe.mirai.event.events.*;
import org.xiaoxian.AxT.Listener.AxTFriendMsgListener;
import org.xiaoxian.AxT.Listener.AxTGroupMsgListener;
import org.xiaoxian.AxT.atbind.WhiteListGroup;
import org.xiaoxian.Listener.*;
import org.xiaoxian.commands.BotInfo;
import org.xiaoxian.AxT.Listener.AxTGroupInvited;
import org.xiaoxian.data.Config;
import org.xiaoxian.data.ConfigManager;

import java.io.File;
import java.io.IOException;

import static org.xiaoxian.commands.BotInfo.onGetOneQQNumber;
import static org.xiaoxian.AxT.atbind.unBindQQ.quitAllBindGroup;
import static org.xiaoxian.AxT.atbind.unBindQQ.unBindAllGroup;

public final class ATBot extends JavaPlugin {

    public static final ATBot INSTANCE = new ATBot();

    static String configPath;
    static String dataPath;

    public static int BackMsgNumber = 0;
    public static int SendMsgNumber = 0;

    public static long startTime = 0;
    public static String atVer = "2.1";

    private ATBot() {
        super(new JvmPluginDescriptionBuilder("org.xiaoxian.ATBot", "2.1")
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

        CommandManager.INSTANCE.registerCommand(new BotInfo(),true);

        // 获取配置目录
        String configDir = MiraiConsole.INSTANCE.getPluginManager().getPluginsConfigPath().toString();
        File configDirPath = new File(configDir, "org.xiaoxian.atbot");
        if (!configDirPath.exists()) {
            configDirPath.mkdirs();
        }
        configPath = configDirPath.getAbsolutePath();
        getLogger().info("AxTBot配置存储目录: " + configPath);

        // 获取数据目录
        String dataDir = MiraiConsole.INSTANCE.getPluginManager().getPluginsDataPath().toString();
        File dataDirPath = new File(dataDir, "org.xiaoxian.atbot");
        if (!dataDirPath.exists()) {
            dataDirPath.mkdirs();
        }
        dataPath = dataDirPath.getAbsolutePath();
        getLogger().info("AxTBot数据存储目录: " + dataPath);
        getLogger().info("———————————————————————————");

        // 加载配置文件
        try {
            getLogger().info("[配置] 加载Config配置文件");
            ConfigManager.loadConfig();
            getLogger().info("[配置] 成功加载配置");
        } catch (IOException e) {
            getLogger().info("[配置] 加载失败: " + e);
        }
        getLogger().info("[配置] 主人Q号: " + Config.getAdminQQ());
        getLogger().info("[配置] 管理群号: " + Config.getAdminGroupQQ());
        getLogger().info("———————————————————————————");

        // 加载数据
        if (Config.getDataType() == 1) {
            getLogger().info("[数据] 当前数据存储方式: MySQL");
        } else if (Config.getDataType() == 0) {
            getLogger().info("[数据] 当前数据存储方式: File");
        }
        getLogger().info("———————————————————————————");

        // 消息监听处理
        GlobalEventChannel.INSTANCE.subscribeAlways(FriendMessageEvent.class,new FriendsMsgListener());
        getLogger().info("[事件] 注册好友消息监听Event（FriendMessageEvent.class）");
        GlobalEventChannel.INSTANCE.subscribeAlways(GroupMessageEvent.class,new GroupMsgListener());
        getLogger().info("[事件] 注册群聊消息监听Event（GroupMessageEvent.class）");

        // 好友添加监听处理
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

        // AxT相关注册，可删除
        GlobalEventChannel.INSTANCE.subscribeAlways(BotInvitedJoinGroupRequestEvent.class,new AxTGroupInvited());
        getLogger().info("[ATBind] 注册授权群聊邀请监听Event（BotInvitedJoinGroupRequestEvent.class）");
        WhiteListGroup.loadWhiteList();
        getLogger().info("[ATBind] 加载白名单群号列表");
        GlobalEventChannel.INSTANCE.subscribeAlways(GroupMessageEvent.class,new AxTGroupMsgListener());
        getLogger().info("[AxTGroup] 注册授权群聊消息监听Event（GroupMessageEvent.class）");
        GlobalEventChannel.INSTANCE.subscribeAlways(FriendMessageEvent.class,new AxTFriendMsgListener());
        getLogger().info("[AxTGroup] 注册授权好友消息监听Event（FriendMessageEvent.class）");
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
        try {
            getLogger().info("[配置] 保存配置文件...");
            Config.saveAllConfig();
            getLogger().info("[配置] 保存完毕");
        } catch (IOException e) {
            e.printStackTrace();
        }
        getLogger().info("AxTBot v" + atVer + " Disable");
        getLogger().info("Thanks for using!");
    }

    public static String getConfigPath() {
        return configPath;
    }

    public static String getDataPath() {
        return dataPath;
    }
}