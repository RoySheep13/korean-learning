import pandas as pd
import streamlit as st
from konlpy.tag import Okt

st.title("韓文歌詞生詞卡工具")

@st.cache_resource(show_spinner="正在載入 JVM 與 KoNLPy 分析器...")
def init_okt():
    return Okt()

user_text = st.text_area("請貼上韓文文本：")

if st.button("開始解析"):
    if user_text:
        okt = init_okt()
        tokens = okt.pos(user_text, stem=True)
        words = [w for w, tag in tokens if tag in ["Noun", "Verb", "Adjective"]]
        df = pd.DataFrame({"韓文單字(原形)": words})
        st.dataframe(df)
        
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="下載生詞表 CSV",
            data=csv_bytes,
            file_name="korean_vocab.csv",
            mime="text/csv"
        )
