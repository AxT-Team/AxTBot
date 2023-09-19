package org.xiaoxian.data;

import java.io.IOException;

public class Config {

    static long AdminQQ;
    static long AdminGroupQQ;

    static int DataType;

    static int NewFriendAddNotify;
    static int MuteNotify;
    static int GroupInvitedNotify;
    static int LeaveGroupNotify;

    static String MySQLHost;
    static int MySQLPort;
    static String MySQLDatabase;
    static String MySQLUser;
    static String MySQLPass;

    /**
     * 设置主人QQ
     */
    public static void setAdminQQ(long QQ) {
        AdminQQ = QQ;
    }

    /**
     * 设置管理群聊
     */
    public static void setAdminGroupQQ(long GroupNumber) {
        AdminGroupQQ = GroupNumber;
    }

    /**
     * 设置存储方式<br>
     * 0 = File<br>
     * 1 = MySQL<br>
     */
    public static void setDataType(int TypeNum) {
        DataType = TypeNum;
    }

    /**
     * 设置MySQL存储信息
     */
    public static void setMySQL(String Host, int Port, String Database, String User, String Pass) {
        MySQLHost = Host;
        MySQLPort = Port;
        MySQLDatabase = Database;
        MySQLUser = User;
        MySQLPass = Pass;
    }

    /**
     * Bot消息通知<br><br>
     * Type类型<br>
     * NewFriendAdd = 好友添加请求<br>
     * Mute = Bot禁言事件<br>
     * GroupInvited = 被邀请进群<br>
     * LeaveGroup = 退出群聊<br>
     * <br>
     * 对应数值<br>
     * 0 = 不通知<br>
     * 1 = 仅通知主人<br>
     * 2 = 仅通知主管理群<br>
     * 3 = 通知主人和主管理群
     */
    public static void setNotify(String Type, int valve) {
         switch (Type) {
             case "NewFriendAdd":
                 NewFriendAddNotify = valve;
                 break;
             case "Mute":
                 MuteNotify = valve;
                 break;
             case "GroupInvited":
                 GroupInvitedNotify = valve;
                 break;
             case "LeaveGroup":
                 LeaveGroupNotify = valve;
                 break;
         }
    }


    /**
     * 获取主人QQ号
     */
    public static long getAdminQQ() {
        return AdminQQ;
    }

    /**
     * 获取管理群聊QQ号
     */
    public static long getAdminGroupQQ() {
        return AdminGroupQQ;
    }

    /**
     * 获取存储方式<br>
     * 0 = File<br>
     * 1 = MySQL<br>
     */
    public static int getDataType() {
        return DataType;
    }

    public static void saveAllConfig() throws IOException {
        ConfigManager.setConfig("AdminQQ" , AdminQQ);
        ConfigManager.setConfig("AdminGroupQQ", AdminGroupQQ);
        ConfigManager.setConfig("DataType", DataType);
    }
}
