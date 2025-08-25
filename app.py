import streamlit as st
import pandas as pd
from datetime import date

# --- KHỞI TẠO KẾT NỐI VỚI SUPABASE (AN TOÀN) ---
@st.cache_resource
def init_connection():
    """
    Sử dụng st.secrets để lấy credentials một cách an toàn.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Lỗi kết nối Supabase: Không tìm thấy credentials trong st.secrets. Vui lòng cấu hình file .streamlit/secrets.toml")
        st.stop()

supabase = init_connection()

# ====== Lấy dữ liệu từ bảng ======
def fetch_data():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM san_pham_de_tai ORDER BY created_at DESC;")
    rows = cur.fetchall()
    conn.close()
    return pd.DataFrame(rows)

# ====== Thêm dữ liệu mới ======
def insert_data(ten_san_pham, chu_tri, can_bo_phoi_hop, linh_vuc,
                thoi_gian_bat_dau, thoi_gian_ket_thuc, noi_dung, tu_khoa, link_luu_tru):
    conn = get_connection()
    cur = conn.cursor()
    query = """
        INSERT INTO san_pham_de_tai (
            ten_san_pham, chu_tri, can_bo_phoi_hop, linh_vuc,
            thoi_gian_bat_dau, thoi_gian_ket_thuc,
            noi_dung, tu_khoa, link_luu_tru
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """
    cur.execute(query, (ten_san_pham, chu_tri, can_bo_phoi_hop, linh_vuc,
                        thoi_gian_bat_dau, thoi_gian_ket_thuc, noi_dung, tu_khoa, link_luu_tru))
    conn.commit()
    conn.close()

# ====== Giao diện Streamlit ======
st.set_page_config(page_title="Quản lý sản phẩm đề tài", layout="wide")

st.title("📑 Quản lý sản phẩm đề tài")

menu = st.sidebar.radio("Chọn chức năng", ["Danh sách", "Thêm mới"])

if menu == "Danh sách":
    st.subheader("Danh sách sản phẩm đề tài")
    df = fetch_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu.")

elif menu == "Thêm mới":
    st.subheader("Thêm sản phẩm đề tài mới")

    with st.form("add_form", clear_on_submit=True):
        ten_san_pham = st.text_input("Tên sản phẩm")
        chu_tri = st.text_input("Chủ trì")
        can_bo_phoi_hop = st.text_input("Cán bộ phối hợp")
        linh_vuc = st.text_input("Lĩnh vực")
        thoi_gian_bat_dau = st.date_input("Thời gian bắt đầu", value=date.today())
        thoi_gian_ket_thuc = st.date_input("Thời gian kết thúc", value=date.today())
        noi_dung = st.text_area("Nội dung")
        tu_khoa = st.text_input("Từ khóa")
        link_luu_tru = st.text_input("Link lưu trữ")

        submitted = st.form_submit_button("💾 Lưu")
        if submitted:
            insert_data(ten_san_pham, chu_tri, can_bo_phoi_hop, linh_vuc,
                        thoi_gian_bat_dau, thoi_gian_ket_thuc, noi_dung, tu_khoa, link_luu_tru)
            st.success("Đã thêm dữ liệu thành công ✅")
