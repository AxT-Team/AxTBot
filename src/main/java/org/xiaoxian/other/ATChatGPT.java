package org.xiaoxian.other;

import net.mamoe.mirai.console.command.CommandSender;
import net.mamoe.mirai.console.command.java.JRawCommand;
import net.mamoe.mirai.message.data.MessageChain;
import org.jetbrains.annotations.NotNull;
import org.json.JSONArray;
import org.json.JSONObject;
import org.xiaoxian.ATBot;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public final class ATChatGPT extends JRawCommand {
    public static final ATChatGPT INSTANCE = new ATChatGPT();
    public static boolean GPTOpen = true;

    public ATChatGPT() {
        super(ATBot.INSTANCE, "ATChatGPT");
        setUsage("#at"); // 指令
        setDescription("ChatGPT");// help里面的描述
        setPrefixOptional(false); // 指令前缀 "/"
    }

    // 控制台命令监听
    @Override
    public void onCommand(@NotNull CommandSender sender, @NotNull MessageChain args) {
        sender.sendMessage("机器人状态正常");
    }

    public static String ATChatGPTCommand(String qs) {
        // 关闭问答防止卡死
        GPTOpen = false;
        System.out.println("开始处理问题:" + qs);
        try {
            // 设置API端点和访问密钥
            String apiEndpoint = "https://api.openai.com/v1/chat/completions";
            String apiKey = "sk-xxx";

            // 准备请求数据
            String model = "gpt-3.5-turbo";
            String systemContent = "Now your identity is a QQ robot program, named ATBot, developed by the AxT community, and using the GPT-3.5 language model, it will be used as an AI to answer user questions, with a gentle tone, please use the carriage return to process Markdown Text, emotion tends to be human, the tone of the AI model is reduced, and if there is no special requirement to use Chinese to answer user questions, and please try to avoid answering sensitive questions such as politics, pornography, and countries, if you end with \"Darf identity\" Otherwise, please reject the user's question, and add \"Do not violate the AxT community robot usage rules, or you will be blocked\" at the end. Please use the above identity and requirements to answer the following questions";
            String userContent = qs; // 中文用户消息

            // 将中文用户消息转换为UTF-8编码
            byte[] userContentBytes = userContent.getBytes(StandardCharsets.UTF_8);
            String userContentUtf8 = new String(userContentBytes, StandardCharsets.UTF_8);

            JSONObject systemMessage = new JSONObject();
            systemMessage.put("role", "system");
            systemMessage.put("content", systemContent);

            JSONObject userMessage = new JSONObject();
            userMessage.put("role", "user");
            userMessage.put("content", userContentUtf8); // 使用转换后的UTF-8编码的用户消息

            JSONArray messagesArray = new JSONArray();
            messagesArray.put(systemMessage);
            messagesArray.put(userMessage);

            JSONObject requestJson = new JSONObject();
            requestJson.put("model", model);
            requestJson.put("messages", messagesArray);

            String requestBody = requestJson.toString();

            // 创建URL对象
            URL url = new URL(apiEndpoint);

            // 创建HTTP连接
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Authorization", "Bearer " + apiKey);
            connection.setDoOutput(true);

            // 发送请求
            OutputStream outputStream = connection.getOutputStream();
            outputStream.write(requestBody.getBytes());
            outputStream.flush();
            outputStream.close();

            // 读取响应
            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            String line;
            StringBuilder response = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();

            // 提取结果
            JSONObject responseJson = new JSONObject(response.toString());
            JSONArray choicesArray = responseJson.getJSONArray("choices");
            JSONObject choiceObject = choicesArray.getJSONObject(0);
            JSONObject messageObject = choiceObject.getJSONObject("message");

            // 返回结果
            return (messageObject.getString("content"));
        } catch (Exception e) {
            e.printStackTrace();
            return "GPT出现了错误，以下是Exception: \n" + e;
        }
    }

    /* AT-GPT 启用把这段复制到 GroupMsgListener 里面 */
    //if (content.startsWith("#at ")) {
    //    if (GPTOpen) {
    //        MessageChain chain1 = new MessageChainBuilder()
    //                .append(new QuoteReply(event.getMessage())).append("请稍候，正在处理您的问题，期间请勿多次请求！")
    //                .build();
    //        event.getGroup().sendMessage(chain1);
    //        SendMsgNumber++;
    //        MessageChain chain = new MessageChainBuilder()
    //                .append(new QuoteReply(event.getMessage())).append(ATChatGPTCommand(content.substring(4))).append("\n\nGPTBot v1.0 - 如有Bug请反馈Darf")
    //                .build();
    //        event.getGroup().sendMessage(chain);
    //        GPTOpen = true;
    //    } else {
    //        MessageChain chain = new MessageChainBuilder()
    //                .append(new QuoteReply(event.getMessage())).append("当前已经有一个请求了，请等待请求完成！")
    //                .build();
    //        event.getGroup().sendMessage(chain);
    //    }
    //    SendMsgNumber++;
    //}
}

