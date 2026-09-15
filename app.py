import os
import streamlit as st
from openai import OpenAI

# =========================
# 页面设置
# =========================
st.set_page_config(
    page_title="翀舟无人机培训在线咨询",
    page_icon="🚁",
    layout="centered"
)

st.title("🚁 翀舟无人机培训在线咨询")
st.caption("欢迎咨询无人机培训课程、费用、报名条件及培训安排")

# =========================
# 读取知识库
# =========================
try:
    with open("无人机培训招生知识库.md", "r", encoding="utf-8") as f:
        knowledge = f.read()
except FileNotFoundError:
    st.error("没有找到《无人机培训招生知识库.md》，请检查文件是否和 app.py 在同一个文件夹。")
    st.stop()

# =========================
# 创建大模型客户端
# =========================
# 本地测试时，可以直接填写你的 API Key
# 正式部署时，建议使用环境变量或 Streamlit Secrets
api_key = st.secrets["ZHIPUAI_API_KEY"]

client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

# =========================
# 系统提示词
# =========================
system_prompt = f"""
你是一个专业的无人机培训招生顾问。

请严格根据下面的知识库回答用户问题。

【回答规则】
1. 只能使用知识库中明确提供的信息。
2. 不确定的信息不要自行编造。
3. 如果用户询问联系电话、微信号或联系人，必须直接从知识库中提取并回答。
4. 联系方式必须原样输出，不得修改、隐藏、替换或编造。
5. 如果知识库中有明确答案，就直接回答。
6. 如果知识库没有明确答案，或者你无法确定答案，请先说明：
   “这个问题需要进一步确认。”
   然后从知识库的【联系方式】部分原样提供联系电话、微信号和联系人。
7. 涉及价格、报名条件、考试政策、法律法规等问题时，
   如果知识库资料不足，也要提供招生处联系方式。
8. 不要输出“转人工”“转人工通知”等字样。
9. 回答要简洁、自然，适合直接回复招生咨询客户。

【知识库】
{knowledge}
"""

# =========================
# 保存聊天记录
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# 用户输入
# =========================
question = st.chat_input("请输入你想咨询的问题，例如：培训费用是多少？")

if question:
    # 显示用户问题
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # 调用 AI
    with st.chat_message("assistant"):
        with st.spinner("正在查询资料，请稍候……"):
            try:
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ] + st.session_state.messages
                )

                answer = response.choices[0].message.content

                st.markdown(answer)

                # 保存 AI 回复
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error("暂时无法连接咨询系统，请稍后再试。")
                st.caption(f"错误信息：{e}")

# =========================
# 侧边栏
# =========================
with st.sidebar:
    st.subheader("招生处联系方式")
    st.write("📞 联系电话：13702945420")
    st.write("💬 微信号：zjj86685588")
    st.write("👤 联系人：郑先生")

    if st.button("清空聊天记录"):
        st.session_state.messages = []
        st.rerun()
