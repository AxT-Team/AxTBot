package org.xiaoxian.commands.network;

import net.mamoe.mirai.console.command.CommandSender;
import net.mamoe.mirai.console.command.java.JRawCommand;
import net.mamoe.mirai.message.data.MessageChain;
import org.jetbrains.annotations.NotNull;
import org.json.JSONObject;
import org.xiaoxian.ATBot;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public final class ping extends JRawCommand {

    public ping() {
        super(ATBot.INSTANCE, "ping");
        setUsage("/ping"); // 指令
        setDescription("查询Ping信息");// help里面的描述
        setPrefixOptional(true); // 指令前缀 "/"
    }

    // 控制台命令监听
    @Override
    public void onCommand(@NotNull CommandSender sender, @NotNull MessageChain args) {
        sender.sendMessage("机器人状态正常");
    }

    public static String ATPingCommand(String ping_ip) {
        try {
            String apiUrl = "https://api.axtn.net/api/ping?host=" + ping_ip;

            // 创建URL对象
            URL url = new URL(apiUrl);

            // 创建HTTP连接对象
            HttpURLConnection con = (HttpURLConnection) url.openConnection();

            // 设置请求方法为GET
            con.setRequestMethod("GET");

            // 获取响应状态码
            int responseCode = con.getResponseCode();

            // 如果响应状态码为200，则读取响应数据
            if (responseCode == 200) {
                BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream(),"UTF-8"));
                String inputLine;
                StringBuffer response = new StringBuffer();

                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
                in.close();

                // 将响应数据转换为JSONObject对象
                JSONObject jsonResponse = new JSONObject(response.toString());

                // 获取Ping结果数据
                int code = jsonResponse.getInt("code");
                String host = jsonResponse.getString("host");
                String ip = jsonResponse.getString("ip");
                double max = jsonResponse.getDouble("max");
                double avg = jsonResponse.getDouble("avg");
                double min = jsonResponse.getDouble("min");
                String location = jsonResponse.getString("location");

                // 判断返回码
                if (code == 200) {
                    return ("主机名: " + host +
                            "\nIP: " + ip +
                            "\n最大延迟: " + max + "ms" +
                            "\n平均延迟: " + avg + "ms" +
                            "\n最小延迟: " + min + "ms" +
                            "\n归属地: " + location +
                            "\n检测点: " + "中国香港");
                } else if (code == 422) {
                    return ("Ping出现错误（IP错误或无法Ping）");
                }
            } else {
                return ("Ping出现错误（IP错误或无法Ping）");
            }
        } catch (Exception e) {
            return ("ERROR：" + e.getMessage() + "\n请通过/反馈 " + e.getMessage() + "反馈此问题");
        }
        return "org.xiaoxian.atnetwork.ping调用异常，请通知管理员进行修复";
    }
}
