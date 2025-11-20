import streamlit as st
import duckdb
import pandas as pd

# -------------------------------------------------
# 0. 🖥 페이지 설정 (항상 첫 Streamlit 명령어!)
# -------------------------------------------------
st.set_page_config(
    page_title="DuckDB 마당 매니저",
    layout="wide"
)

# -------------------------------------------------
# 1. 💾 DuckDB 연결 함수
# -------------------------------------------------
DB_FILE = "madang.db"

@st.cache_resource
def get_db_connection():
    try:
        conn = duckdb.connect(database=DB_FILE, read_only=False)
        return conn
    except Exception as e:
        st.error(f"❌ DB 연결 실패: {e}")
        st.stop()

conn = get_db_connection()

# -------------------------------------------------
# 2. 🖥 메인 UI
# -------------------------------------------------
st.title("📚 DuckDB 마당 매니저")
st.caption("Madang DB 데이터를 DuckDB 기반으로 조회하는 간단한 웹 애플리케이션입니다.")

# -------------------------------------------------
# 3. 📝 고객 주문 조회
# -------------------------------------------------
st.header("🔍 고객 주문 내역 조회")

input_name = st.text_input(
    "조회할 고객 이름을 입력하세요:",
    value=""
)

if st.button("조회 시작") or len(input_name) > 0:

    if len(input_name) == 0:
        st.warning("⚠️ 고객 이름을 입력해주세요.")
        st.stop()

    # 주문 내역 조회 SQL
    query_sql = f"""
        SELECT 
            T1.name AS 고객명, 
            T3.bookname AS 서적명, 
            T2.saleprice AS 판매가, 
            T2.orderdate AS 주문일
        FROM Customer AS T1
        INNER JOIN Orders AS T2 ON T1.custid = T2.custid
        INNER JOIN Book AS T3 ON T2.bookid = T3.bookid
        WHERE T1.name = '{input_name}';
    """

    try:
        df = conn.execute(query_sql).df()

        # 주문 내역 없는 경우
        if df.empty:
            check_sql = f"SELECT * FROM Customer WHERE name = '{input_name}';"
            customer_found = conn.execute(check_sql).df()

            if not customer_found.empty:
                st.success(f"🟢 고객 '{input_name}'님은 등록되어 있으나 주문 기록이 없습니다.")
            else:
                st.error(f"🔴 고객 '{input_name}'님은 데이터베이스에 존재하지 않습니다.")

        else:
            st.subheader(f"📦 '{input_name}'님의 주문 내역")
            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ 쿼리 실행 오류: {e}")

# -------------------------------------------------
# 4. 📊 전체 테이블 확인 (사이드바)
# -------------------------------------------------
st.sidebar.header("📁 전체 테이블 보기")

if st.sidebar.checkbox("Customer 테이블 보기"):
    try:
        st.sidebar.dataframe(conn.execute("SELECT * FROM Customer").df())
    except Exception as e:
        st.sidebar.error(f"Customer 조회 오류: {e}")

if st.sidebar.checkbox("Book 테이블 보기"):
    try:
        st.sidebar.dataframe(conn.execute("SELECT * FROM Book").df())
    except Exception as e:
        st.sidebar.error(f"Book 조회 오류: {e}")

if st.sidebar.checkbox("Orders 테이블 보기"):
    try:
        st.sidebar.dataframe(conn.execute("SELECT * FROM Orders").df())
    except Exception as e:
        st.sidebar.error(f"Orders 조회 오류: {e}")