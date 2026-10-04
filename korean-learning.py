import pandas as pd
import streamlit as st
from konlpy.tag import Okt

st.title("韓文歌詞生詞卡工具")
user_text = st.text_area("請貼上韓文文本：")

if st.button("開始解析"):
    if user_text:
        okt = Okt()
        tokens = okt.pos(user_text, stem=True)
        words = [w for w, tag in tokens if tag in ["Noun", "Verb", "Adjective"]]
        df = pd.DataFrame({"韓文單字": words})
        st.dataframe(df)
