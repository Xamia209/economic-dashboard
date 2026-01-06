import streamlit as st
import traceback
from collecting_news import collect_news

st.set_page_config(page_title="DEBUG MODE", layout="wide")

# =====================
# SESSION STATE
# =====================
if "debug" not in st.session_state:
    st.session_state.debug = False

if "debug_log" not in st.session_state:
    st.session_state.debug_log = ""

# =====================
# SIDEBAR BUTTON
# =====================
if st.sidebar.button("🚨 DEBUG – Cập nhật tin"):
    st.session_state.debug = True
    st.session_state.debug_log = "👉 BẮT ĐẦU DEBUG...\n"

# =====================
# DEBUG MODE (KILL UI)
# =====================
if st.session_state.debug:
    st.title("🧨 DEBUG MODE (UI ĐÃ BỊ TẮT)")
    placeholder = st.empty()

    try:
        st.session_state.debug_log += "1️⃣ Gọi collect_news()\n"
        placeholder.code(st.session_state.debug_log)

        articles = collect_news()

        st.session_state.debug_log += f"✅ Lấy được {len(articles)} bài\n"
        placeholder.code(st.session_state.debug_log)

        st.session_state.debug_log += "🎉 DEBUG XONG – KHÔNG LỖI\n"
        placeholder.code(st.session_state.debug_log)

    except Exception:
        st.session_state.debug_log += "\n❌ LỖI XẢY RA:\n"
        st.session_state.debug_log += traceback.format_exc()
        placeholder.code(st.session_state.debug_log)

    # ❗ KHÓA HẲN APP – KHÔNG RERUN
    st.stop()

# =====================
# UI BÌNH THƯỜNG (CHƯA DEBUG)
# =====================
st.title("📊 Dashboard Tin tức Kinh tế")
st.info("Bấm nút DEBUG bên sidebar để kiểm tra lỗi.")
