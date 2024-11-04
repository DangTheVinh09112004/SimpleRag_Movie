import streamlit as st
import requests
import uuid

# URL API và session_id duy nhất cho mỗi phiên trò chuyện
FLASK_API_URL = "http://localhost:5000/api/vinh_dep_trai/chat"
session_id = str(uuid.uuid4())

# CSS tùy chỉnh để trang trí
st.markdown("""
    <style>
        .main { background-color: #01579b; font-family: Arial, sans-serif; } /* Nền xanh lớp biển nhạt */
        .stButton>button { background-color: #ff5e57; color: white; border-radius: 8px; }
        .stButton>button:hover { background-color: #ff7b72; }
        .chat-container { max-width: 700px; margin: auto; padding: 10px; border-radius: 15px; }
        .user-chat { background-color: #4fc3f7; color: white; padding: 10px; border-radius: 8px; margin: 5px; } /* Nền xanh lớp biển đậm */
        .assistant-chat { background-color: #0097a7; color: white; padding: 10px; border-radius: 8px; margin: 5px; } /* Nền xanh lớp biển đậm */
        .logo-container img { border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# Hiển thị logo và tiêu đề
logo = "—Pngtree—popcorn movie film_2704218.png"
st.sidebar.image(logo, width=227)
st.title("🍿 Movie Film Chat Assistant")

# Khởi tạo lịch sử trò chuyện nếu chưa có
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Hiển thị lịch sử trò chuyện
for message in st.session_state.chat_history:
    with st.container():
        role_class = "user-chat" if message["role"] == "user" else "assistant-chat"
        st.markdown(f"<div class='{role_class}'>{message['content']}</div>", unsafe_allow_html=True)

# Nhập và gửi tin nhắn của người dùng
if prompt := st.chat_input("Bạn có cần tư vấn bộ phim gì hôm nay không?"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.markdown(f"<div class='user-chat'>{prompt}</div>", unsafe_allow_html=True)

    # Hiển thị thanh trạng thái khi chờ phản hồi từ API
    with st.spinner("Đang tìm kiếm phim phù hợp..."):
        payload = {
            "query": prompt,
            "session_id": session_id
        }
        response = requests.post(FLASK_API_URL, json=payload)

    # Xử lý phản hồi từ API
    if response.status_code == 200:
        api_response = response.json()
        assistant_response = api_response.get("response", "Không có phản hồi từ API.")
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        st.markdown(f"<div class='assistant-chat'>{assistant_response}</div>", unsafe_allow_html=True)
    else:
        st.error(f"Đã xảy ra lỗi: {response.status_code}")