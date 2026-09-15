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


# =========================
# 页面样式
# =========================
st.markdown(
    """
    <style>
    /* 隐藏顶部 Streamlit 装饰区域 */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* 隐藏顶部状态加载区域 */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* 隐藏 Streamlit 默认菜单 */
    #MainMenu {
        visibility: hidden;
    }

    /* 隐藏底部页脚 */
    footer {
        visibility: hidden;
    }

    /* 隐藏顶部 Header */
    header {
        visibility: hidden;
    }

    /* 缩小页面顶部和底部空白 */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }

    /* 自定义标题 */
    .custom-title {
        font-size: 27px;
        line-height: 1.35;
        font-weight: 700;
        margin-bottom: 8px;
        color: #202124;
    }

    /* 自定义副标题 */
    .custom-caption {
        font-size: 15px;
        color: #777777;
        margin-bottom: 20px;
    }

    /* 常见问题标题 */
    .question-title {
        font-size: 18px;
        font-weight: 600;
        margin-top: 12px;
        margin-bottom: 10px;
    }

    /* 手机页面适配 */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
        }

        .custom-title {
            font-size: 24px;
        }

        .custom-caption {
            font-size: 14px;
        }

        .question-title {
            font-size: 17px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# 页面标题
# =========================
st.markdown(
    '<div class="custom-title">🚁 翀舟无人机培训在线咨询</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="custom-caption">欢迎咨询无人机培训课程、费用、报名条件及培训安排</div>',
    unsafe_allow_html=True
)


# =========================
# 读取 Markdown 知识库
# =========================
try:
    with open("无人机培训招生知识库.md", "r", encoding="utf-8") as f:
        knowledge = f.read()

except FileNotFoundError:
    st.error(
        "没有找到《无人机培训招生知识库.md》，"
        "请检查它是否和 app.py 在同一个文件夹。"
    )
    st.stop()


# =========================
# 读取 Streamlit Secrets
# =========================
try:
    api_key = st.secrets["ZHIPUAI_API_KEY"]

except Exception:
    st.error(
        "没有读取到 ZHIPUAI_API_KEY。"
        "请在 Streamlit Cloud 的 Settings → Secrets 中配置 API Key。"
    )
    st.stop()


# =========================
# 创建大模型客户端
# =========================
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
9. 不要编造优惠、班次、考试安排、住宿条件或其他知识库没有的信息。
10. 回答要简洁、自然，适合直接回复招生咨询客户。

【知识库】
{knowledge}
"""


# =========================
# 初始化聊天记录
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_question" not in st.session_state:
    st.session_state.selected_question = None


# =========================
# 快捷问题选择函数
# =========================
def select_question(question):
    st.session_state.selected_question = question


# =========================
# 常见问题快捷按钮
# =========================
st.markdown(
    '<div class="question-title">常见问题</div>',
    unsafe_allow_html=True
)

quick_questions = [
    "培训费用是多少？",
    "培训地点在哪里？",
    "零基础可以学吗？",
    "培训周期多久？",
    "提供住宿吗？",
    "怎么联系招生处？"
]

# 两列布局，手机上比较适合
cols = st.columns(2)

for i, item in enumerate(quick_questions):
    with cols[i % 2]:
        st.button(
            item,
            key=f"quick_question_{i}",
            use_container_width=True,
            on_click=select_question,
            args=(item,)
        )


# =========================
# 显示历史聊天记录
# =========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================
# 获取用户输入
# =========================
typed_question = st.chat_input(
    "请输入你想咨询的问题，例如：培训费用是多少？"
)


# 如果用户点击快捷问题，就使用快捷问题
if st.session_state.selected_question:
    question = st.session_state.selected_question
    st.session_state.selected_question = None

else:
    question = typed_question


# =========================
# 调用 AI 回答
# =========================
if question:

    # 保存并显示用户问题
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # 调用大模型
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

                # 显示 AI 回答
                st.markdown(answer)

                # 保存 AI 回答
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

    st.divider()

    st.subheader("使用说明")

    st.write("你可以点击上方常见问题，也可以直接在下方输入问题。")

    if st.button("清空聊天记录", use_container_width=True):
        st.session_state.messages = []
        st.session_state.selected_question = None
        st.rerun()
