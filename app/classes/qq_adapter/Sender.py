"""
Class File for Sending QQ Messages (Request Payload)

Author: Shanshui2024 & DeepSeek V4
Organization: AxT-Team

参考文档：
  https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_groups_group_openid_messages.post.html

本模块定义发送 QQ 消息所需的全部请求体模型，包括：
  - Sender            → 顶层请求体（群/频道/私聊共用）
  - Markdown          → Markdown 消息
  - Keyboard/Button   → 内嵌键盘及按钮
  - MediaInfo         → 富媒体消息
  - MessageReference  → 引用回复
  - Card              → 卡片消息
"""

from pydantic import BaseModel
from typing import Optional

# ============================================================
#  Markdown
# ============================================================

class Markdown(BaseModel):
    """Markdown 消息内容。msg_type=2 时使用。"""
    template_id: Optional[int] = None       # [已废弃] 平台 Markdown 模板 ID
    content: Optional[str] = None           # Markdown 原始内容
    custom_template_id: Optional[str] = None # [已废弃] 自定义模板 ID


# ============================================================
#  Keyboard — 内嵌键盘
# ============================================================

class Permission(BaseModel):
    """按钮操作权限"""
    type: int = 2                           # 0=指定用户, 1=管理员, 2=所有人
    specify_user_ids: Optional[list[str]] = None  # 有权限的用户 ID 列表
    specify_role_ids: Optional[list[str]] = None  # 有权限的身份组 ID 列表（仅频道）


class Action(BaseModel):
    """按钮点击行为"""
    type: int = 0                           # 0=跳转按钮, 1=回调按钮, 2=指令按钮
    permission: Optional[Permission] = None # 操作权限
    data: Optional[str] = None              # 回调数据（type=1/2 时必填）
    click_limit: Optional[int] = None       # [已废弃] 可点击次数限制
    unsupport_tips: Optional[str] = None    # 版本过低时提示文案
    enter: Optional[bool] = None            # 指令按钮：点击后自动发送 data（仅单聊）
    reply: Optional[bool] = None            # 指令按钮：是否引用回复本消息
    anchor: Optional[int] = None            # 指令按钮：1=唤起选图器（仅手机端单聊）


class RenderData(BaseModel):
    """按钮渲染样式"""
    label: Optional[str] = None             # 按钮文字（最多 10 字符）
    visited_label: Optional[str] = None     # 点击后文字，不传则保持不变
    style: Optional[int] = None             # 0=灰线框, 1=蓝线框, 2=白字, 3=蓝底白字


class Button(BaseModel):
    """键盘按钮"""
    id: Optional[str] = None                # 按钮 ID（同一键盘内唯一）
    render_data: Optional[RenderData] = None # 渲染样式
    action: Optional[Action] = None         # 点击行为


class Row(BaseModel):
    """键盘按钮行"""
    buttons: Optional[list[Button]] = None  # 行内按钮，从左到右排列


class KeyboardContent(BaseModel):
    """自定义键盘布局"""
    rows: Optional[list[Row]] = None        # 按钮行列表


class Keyboard(BaseModel):
    """内嵌键盘（与 msg 同级）"""
    id: Optional[str] = None                # 平台预设键盘模板 ID
    content: Optional[KeyboardContent] = None # 自定义键盘布局（与 id 互斥）


# ============================================================
#  富媒体 & 引用 & 卡片
# ============================================================

class MediaInfo(BaseModel):
    """富媒体消息。msg_type=7 时使用。"""
    file_info: Optional[str] = None         # 文件上传接口返回值


class MessageReference(BaseModel):
    """引用回复信息。填写后以引用形式展示。"""
    message_id: Optional[str] = None        # 被引用消息的 ID


class CardContent(BaseModel):
    """卡片内容"""
    title: Optional[str] = None
    description: Optional[str] = None
    pic_url: Optional[str] = None
    url: Optional[str] = None


class Card(BaseModel):
    """卡片消息。msg_type=8 时使用。"""
    type: Optional[str] = None              # 卡片类型，如 "tuwen"
    content: Optional[CardContent] = None


# ============================================================
#  Sender — 发送消息顶层请求体
# ============================================================

class Sender(BaseModel):
    """
    发送 QQ 消息的完整请求体。

    根据 msg_type 不同，各内容字段互斥：
      msg_type=0 → content（纯文本）
      msg_type=2 → markdown（Markdown 消息）
      msg_type=7 → media（富媒体消息）
      msg_type=8 → card（卡片消息）

    被动回复需填写 msg_id 或 event_id。
    """
    msg_type: int = 0                       # 0=文本, 2=Markdown, 7=富媒体, 8=卡片
    content: Optional[str] = None           # 文本内容（msg_type=0）
    markdown: Optional[Markdown] = None     # Markdown 消息（msg_type=2）
    keyboard: Optional[Keyboard] = None     # 内嵌键盘
    msg_id: Optional[str] = None            # 被动回复：原消息 ID（5 分钟内有效）
    event_id: Optional[str] = None          # 被动回复：原事件 ID（与 msg_id 二选一）
    msg_seq: Optional[int] = None           # 回复序号（与 msg_id 联合去重，默认 1）
    media: Optional[MediaInfo] = None       # 富媒体信息（msg_type=7）
    message_reference: Optional[MessageReference] = None  # 引用回复
    is_wakeup: Optional[bool] = None        # 是否为互动召回消息（与 msg_id/event_id 互斥）
    card: Optional[Card] = None             # 卡片消息（msg_type=8）
