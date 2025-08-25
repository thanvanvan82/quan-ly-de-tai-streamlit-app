import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

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
    except KeyError as e:
        st.error(f"Lỗi kết nối Supabase: Không tìm thấy {e} trong st.secrets. Vui lòng cấu hình file .streamlit/secrets.toml")
        st.stop()
    except Exception as e:
        st.error(f"Lỗi kết nối Supabase: {str(e)}")
        st.stop()

supabase = init_connection()

# ====== Lấy dữ liệu từ bảng ======
@st.cache_data(ttl=60)  # Cache trong 60 giây để tăng hiệu suất
def fetch_data():
    """
    Lấy dữ liệu từ bảng san_pham_de_tai
    """
    try:
        response = supabase.table("san_pham_de_tai").select("*").order("created_at", desc=True).execute()
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Lỗi khi lấy dữ liệu: {str(e)}")
        return pd.DataFrame()

# ====== Thêm dữ liệu mới ======
def insert_data(ten_san_pham, chu_tri, can_bo_phoi_hop, linh_vuc,
                thoi_gian_bat_dau, thoi_gian_ket_thuc, noi_dung, tu_khoa, link_luu_tru):
    """
    Thêm sản phẩm đề tài mới vào database
    """
    try:
        data = {
            "ten_san_pham": ten_san_pham,
            "chu_tri": chu_tri,
            "can_bo_phoi_hop": can_bo_phoi_hop,
            "linh_vuc": linh_vuc,
            "thoi_gian_bat_dau": thoi_gian_bat_dau.isoformat(),
            "thoi_gian_ket_thuc": thoi_gian_ket_thuc.isoformat(),
            "noi_dung": noi_dung,
            "tu_khoa": tu_khoa,
            "link_luu_tru": link_luu_tru
        }
        
        response = supabase.table("san_pham_de_tai").insert(data).execute()
        
        if response.data:
            st.cache_data.clear()  # Xóa cache để cập nhật danh sách
            return True
        else:
            return False
            
    except Exception as e:
        st.error(f"Lỗi khi thêm dữ liệu: {str(e)}")
        return False

# ====== Xóa dữ liệu ======
def delete_data(record_id):
    """
    Xóa sản phẩm đề tài theo ID
    """
    try:
        response = supabase.table("san_pham_de_tai").delete().eq("id", record_id).execute()
        if response.data:
            st.cache_data.clear()  # Xóa cache để cập nhật danh sách
            return True
        return False
    except Exception as e:
        st.error(f"Lỗi khi xóa dữ liệu: {str(e)}")
        return False

# ====== Cập nhật dữ liệu ======
def update_data(record_id, ten_san_pham, chu_tri, can_bo_phoi_hop, linh_vuc,
                thoi_gian_bat_dau, thoi_gian_ket_thuc, noi_dung, tu_khoa, link_luu_tru):
    """
    Cập nhật sản phẩm đề tài theo ID
    """
    try:
        data = {
            "ten_san_pham": ten_san_pham,
            "chu_tri": chu_tri,
            "can_bo_phoi_hop": can_bo_phoi_hop,
            "linh_vuc": linh_vuc,
            "thoi_gian_bat_dau": thoi_gian_bat_dau.isoformat(),
            "thoi_gian_ket_thuc": thoi_gian_ket_thuc.isoformat(),
            "noi_dung": noi_dung,
            "tu_khoa": tu_khoa,
            "link_luu_tru": link_luu_tru
        }
        
        response = supabase.table("san_pham_de_tai").update(data).eq("id", record_id).execute()
        
        if response.data:
            st.cache_data.clear()  # Xóa cache để cập nhật danh sách
            return True
        return False
            
    except Exception as e:
        st.error(f"Lỗi khi cập nhật dữ liệu: {str(e)}")
        return False

# ====== Validation functions ======
def validate_input(ten_san_pham, chu_tri, linh_vuc, thoi_gian_bat_dau, thoi_gian_ket_thuc):
    """
    Kiểm tra tính hợp lệ của dữ liệu đầu vào
    """
    errors = []
    
    if not ten_san_pham.strip():
        errors.append("Tên sản phẩm không được để trống")
    
    if not chu_tri.strip():
        errors.append("Chủ trì không được để trống")
    
    if not linh_vuc.strip():
        errors.append("Lĩnh vực không được để trống")
    
    if thoi_gian_ket_thuc < thoi_gian_bat_dau:
        errors.append("Thời gian kết thúc phải sau thời gian bắt đầu")
    
    return errors

# ====== Giao diện Streamlit ======
st.set_page_config(
    page_title="Quản lý sản phẩm đề tài", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📑 Quản lý sản phẩm đề tài")
st.markdown("---")

# Sidebar menu
menu = st.sidebar.radio(
    "🔧 Chọn chức năng", 
    ["📋 Danh sách", "➕ Thêm mới", "✏️ Chỉnh sửa"],
    index=0
)

# ====== TAB DANH SÁCH ======
if menu == "📋 Danh sách":
    st.subheader("📋 Danh sách sản phẩm đề tài")
    
    # Thêm nút refresh
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Làm mới", type="secondary"):
            st.cache_data.clear()
            st.rerun()
    
    df = fetch_data()
    
    if not df.empty:
        # Thêm tính năng tìm kiếm
        search_term = st.text_input("🔍 Tìm kiếm theo tên sản phẩm:", "")
        
        if search_term:
            df_filtered = df[df['ten_san_pham'].str.contains(search_term, case=False, na=False)]
        else:
            df_filtered = df
        
        st.info(f"Tổng số: {len(df_filtered)} sản phẩm")
        
        # Hiển thị bảng với định dạng đẹp hơn
        if not df_filtered.empty:
            # Định dạng lại các cột date nếu có
            for col in ['thoi_gian_bat_dau', 'thoi_gian_ket_thuc']:
                if col in df_filtered.columns:
                    df_filtered[col] = pd.to_datetime(df_filtered[col]).dt.strftime('%d/%m/%Y')
            
            st.dataframe(
                df_filtered,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ten_san_pham": st.column_config.TextColumn("Tên sản phẩm", width="medium"),
                    "chu_tri": st.column_config.TextColumn("Chủ trì", width="medium"),
                    "linh_vuc": st.column_config.TextColumn("Lĩnh vực", width="medium"),
                    "thoi_gian_bat_dau": st.column_config.TextColumn("Ngày bắt đầu", width="small"),
                    "thoi_gian_ket_thuc": st.column_config.TextColumn("Ngày kết thúc", width="small"),
                    "link_luu_tru": st.column_config.LinkColumn("Link lưu trữ", width="medium")
                }
            )
        else:
            st.warning("Không tìm thấy kết quả phù hợp.")
    else:
        st.info("📝 Chưa có dữ liệu. Hãy thêm sản phẩm đề tài đầu tiên!")

# ====== TAB THÊM MỚI ======
elif menu == "➕ Thêm mới":
    st.subheader("➕ Thêm sản phẩm đề tài mới")
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            ten_san_pham = st.text_input("📝 Tên sản phẩm *", placeholder="Nhập tên sản phẩm...")
            chu_tri = st.text_input("👤 Chủ trì *", placeholder="Nhập tên chủ trì...")
            can_bo_phoi_hop = st.text_input("🤝 Cán bộ phối hợp", placeholder="Nhập tên cán bộ phối hợp...")
            linh_vuc = st.text_input("🎯 Lĩnh vực *", placeholder="Nhập lĩnh vực...")
        
        with col2:
            thoi_gian_bat_dau = st.date_input(
                "📅 Thời gian bắt đầu *", 
                value=date.today(),
                help="Chọn ngày bắt đầu dự án"
            )
            thoi_gian_ket_thuc = st.date_input(
                "📅 Thời gian kết thúc *", 
                value=date.today(),
                help="Chọn ngày kết thúc dự án"
            )
            tu_khoa = st.text_input("🏷️ Từ khóa", placeholder="Nhập từ khóa, phân cách bằng dấu phẩy...")
            link_luu_tru = st.text_input("🔗 Link lưu trữ", placeholder="https://...")
        
        noi_dung = st.text_area(
            "📄 Nội dung", 
            placeholder="Mô tả chi tiết về sản phẩm đề tài...",
            height=100
        )
        
        st.markdown("**Các trường có dấu * là bắt buộc*")
        
        submitted = st.form_submit_button("💾 Lưu sản phẩm", type="primary")
        
        if submitted:
            # Validate input
            errors = validate_input(ten_san_pham, chu_tri, linh_vuc, thoi_gian_bat_dau, thoi_gian_ket_thuc)
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Insert data
                if insert_data(ten_san_pham, chu_tri, can_bo_phoi_hop, linh_vuc,
                             thoi_gian_bat_dau, thoi_gian_ket_thuc, noi_dung, tu_khoa, link_luu_tru):
                    st.success("✅ Đã thêm sản phẩm đề tài thành công!")
                    st.balloons()
                else:
                    st.error("❌ Có lỗi xảy ra khi thêm dữ liệu. Vui lòng thử lại.")

# ====== TAB CHỈNH SỬA ======
elif menu == "✏️ Chỉnh sửa":
    st.subheader("✏️ Chỉnh sửa sản phẩm đề tài")
    
    df = fetch_data()
    
    if not df.empty:
        # Chọn sản phẩm để chỉnh sửa
        product_options = {f"{row['ten_san_pham']} (ID: {row['id']})": row['id'] 
                          for _, row in df.iterrows()}
        
        selected_product = st.selectbox(
            "🎯 Chọn sản phẩm cần chỉnh sửa:",
            options=list(product_options.keys()),
            index=None,
            placeholder="Chọn một sản phẩm..."
        )
        
        if selected_product:
            record_id = product_options[selected_product]
            current_data = df[df['id'] == record_id].iloc[0]
            
            # Hiển thị form chỉnh sửa
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    ten_san_pham = st.text_input("📝 Tên sản phẩm *", value=current_data['ten_san_pham'])
                    chu_tri = st.text_input("👤 Chủ trì *", value=current_data['chu_tri'])
                    can_bo_phoi_hop = st.text_input("🤝 Cán bộ phối hợp", value=current_data.get('can_bo_phoi_hop', ''))
                    linh_vuc = st.text_input("🎯 Lĩnh vực *", value=current_data['linh_vuc'])
                
                with col2:
                    thoi_gian_bat_dau = st.date_input(
                        "📅 Thời gian bắt đầu *",
                        value=pd.to_datetime(current_data['thoi_gian_bat_dau']).date()
                    )
                    thoi_gian_ket_thuc = st.date_input(
                        "📅 Thời gian kết thúc *",
                        value=pd.to_datetime(current_data['thoi_gian_ket_thuc']).date()
                    )
                    tu_khoa = st.text_input("🏷️ Từ khóa", value=current_data.get('tu_khoa', ''))
                    link_luu_tru = st.text_input("🔗 Link lưu trữ", value=current_data.get('link_luu_tru', ''))
                
                noi_dung = st.text_area(
                    "📄 Nội dung",
                    value=current_data.get('noi_dung', ''),
                    height=100
                )
                
                col_update, col_delete = st.columns([1, 1])
                
                with col_update:
                    update_submitted = st.form_submit_button("✏️ Cập nhật", type="primary")
                
                with col_delete:
                    delete_submitted = st.form_submit_button("🗑️ Xóa", type="secondary")
                
                if update_submitted:
                    errors = validate_input(ten_san_pham, chu_tri, linh_vuc, thoi_gian_bat_dau, thoi_gian_ket_thuc)
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        if update_data(record_id, ten_san_pham, chu_tri, can_bo_phoi_hop, linh_vuc,
                                     thoi_gian_bat_dau, thoi_gian_ket_thuc, noi_dung, tu_khoa, link_luu_tru):
                            st.success("✅ Đã cập nhật sản phẩm đề tài thành công!")
                            st.rerun()
                        else:
                            st.error("❌ Có lỗi xảy ra khi cập nhật dữ liệu.")
                
                if delete_submitted:
                    if st.session_state.get('confirm_delete') == record_id:
                        if delete_data(record_id):
                            st.success("✅ Đã xóa sản phẩm đề tài thành công!")
                            st.rerun()
                        else:
                            st.error("❌ Có lỗi xảy ra khi xóa dữ liệu.")
                    else:
                        st.session_state['confirm_delete'] = record_id
                        st.warning("⚠️ Nhấn lại nút Xóa để xác nhận xóa sản phẩm này!")
    else:
        st.info("📝 Chưa có dữ liệu để chỉnh sửa.")

# ====== FOOTER ======
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>📑 Hệ thống quản lý sản phẩm đề tài | Phiên bản 2.0</small>
    </div>
    """, 
    unsafe_allow_html=True
)