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

    static boolean MuteLeave;
    static int MuteTime;

    static boolean AutoNewFriendAdd;
    static boolean AutoGroupInvited;

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
    public static long getAdminQQ() {
        return AdminQQ;
    }

    /**
     * 设置管理群聊
     */
    public static void setAdminGroupQQ(long GroupNumber) {
        AdminGroupQQ = GroupNumber;
    }
    public static long getAdminGroupQQ() {
        return AdminGroupQQ;
    }

    /**
     * 设置存储方式<br>
     * 0 = File<br>
     * 1 = MySQL<br>
     */
    public static void setDataType(int TypeNum) {
        DataType = TypeNum;
    }
    public static int getDataType() {
        return DataType;
    }

    /**
     * 禁言后自动退出群聊
     */
    public static void setMuteLeave(boolean value) {
        MuteLeave = value;
    }
    public static boolean getMuteLeave() {
        return MuteLeave;
    }

    /**
     * 禁言多久退出群聊（秒）
     */
    public static void setMuteTime(int s) {
        MuteTime = s;
    }
    public static int getMuteTime() {
        return MuteTime;
    }

    /**
     * 自动同意好友申请
     */
    public static void setAutoNewFriendAdd(boolean value) {
        AutoNewFriendAdd = value;
    }
    public static boolean getAutoNewFriendAdd() {
        return AutoNewFriendAdd;
    }

    /**
     * 自动同意群聊邀请
     */
    public static void setAutoGroupInvited(boolean value) {
        AutoGroupInvited = value;
    }
    public static boolean getAutoGroupInvited() {
        return AutoGroupInvited;
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
    public static void setNotify(String Type, int value) {
         switch (Type) {
             case "NewFriendAdd":
                 NewFriendAddNotify = value;
                 break;
             case "Mute":
                 MuteNotify = value;
                 break;
             case "GroupInvited":
                 GroupInvitedNotify = value;
                 break;
             case "LeaveGroup":
                 LeaveGroupNotify = value;
                 break;
         }
    }
    public static int getNotify(String Type) {
        switch (Type) {
            case "NewFriendAdd":
                return NewFriendAddNotify;
            case "Mute":
                return MuteNotify;
            case "GroupInvited":
                return GroupInvitedNotify;
            case "LeaveGroup":
                return LeaveGroupNotify;
        }
        return 0;
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

    public static void saveAllConfig() throws IOException {
        ConfigManager.setConfig("AdminQQ" , AdminQQ);
        ConfigManager.setConfig("AdminGroupQQ", AdminGroupQQ);
        ConfigManager.setConfig("DataType", DataType);
    }
}
