import html
import re
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="韓文歌詞生詞卡：結合斷詞技術的語言學習工具",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

POS_MAP = {"Noun": "名詞", "Verb": "動詞", "Adjective": "形容詞"}
HANGUL_RE = re.compile(r"[가-힣]")

BASIC_WORDS = {
    "하다", "있다", "없다", "되다", "이다", "않다",
    "같다", "그렇다", "이렇다", "어떻다", "아니다",
}

COL_WORD = "韓文單字(原形)"
COL_TRANS = "中文翻譯"
COL_POS = "詞性"
COL_FREQ = "出現次數"
COL_EXAMPLE = "例句"

SAMPLE_TEXT = (
    "오늘은 친구랑 같이 카페에 갔어요\n"
    "커피가 정말 맛있어서 기분이 좋았어요\n"
    "내일은 비가 올 것 같아서 우산을 챙길 거예요\n"
    "요즘 한국어 공부가 재미있어요"
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&family=Noto+Serif+KR:wght@700&family=Noto+Sans+TC:wght@400;500&family=Noto+Sans+KR:wght@400;500&display=swap');
:root{--paper:#F6F2EA;--card:#FFFDF8;--ink:#1F1B16;--muted:#8A8173;--line:#DDD5C6;--accent:#C2412D;}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--paper)!important;color:var(--ink);font-family:'Noto Sans TC','Noto Sans KR',sans-serif;}
#MainMenu,footer,header,[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stSidebar"]{display:none!important;}
:root,.stApp{color-scheme:light!important;}
.stApp p,.stApp label,.stApp li{color:var(--ink);}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted)!important;}
.block-container,[data-testid="stMainBlockContainer"]{max-width:860px;padding:4rem 1.4rem 5rem;}
.hero{display:flex;align-items:center;gap:1.1rem;margin-bottom:.4rem;}
.seal{width:46px;height:46px;flex:none;background:var(--accent);color:var(--paper);border-radius:4px;display:flex;align-items:center;justify-content:center;text-align:center;font-family:'Noto Serif KR',serif;font-weight:700;font-size:16px;line-height:1.05;transform:rotate(-4deg);}
.hero h1{font-family:'Noto Serif TC',serif;font-weight:700;font-size:2.3rem;letter-spacing:.06em;margin:0;padding:0;line-height:1.2;color:var(--ink);}
.sub{color:var(--muted);letter-spacing:.14em;font-size:.9rem;margin:.2rem 0 2.2rem 0;padding-left:calc(46px + 1.1rem);}
div[data-baseweb="textarea"]{background:var(--card)!important;border:1px solid var(--line)!important;border-radius:6px!important;}
div[data-baseweb="textarea"]:focus-within{border-color:var(--ink)!important;}
div[data-baseweb="base-input"]{background:var(--card)!important;}
div[data-baseweb="textarea"] textarea,[data-testid="stTextArea"] textarea{background-color:var(--card)!important;color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;caret-color:var(--ink);font-family:'Noto Sans KR','Noto Sans TC',sans-serif;font-size:1.05rem;line-height:1.9;padding:1rem 1.1rem;}
textarea::placeholder{color:#B5AC9B!important;}
div[data-baseweb="select"]>div{background:var(--card)!important;border-color:var(--line)!important;border-radius:4px!important;}
div[data-baseweb="select"] *{color:var(--ink)!important;}
div[data-baseweb="popover"] ul,div[data-baseweb="popover"] li,div[data-baseweb="menu"]{background:var(--card)!important;color:var(--ink)!important;}
[data-testid="stToggle"] p{color:var(--ink)!important;}
[data-testid="stWidgetLabel"] p,[data-testid="stCheckbox"] p{font-size:.88rem;color:var(--ink);}
[class*="st-key-"] button *{color:inherit!important;}
.st-key-run button{background:var(--ink);color:var(--paper);border:1px solid var(--ink);border-radius:4px;padding:.55rem 1.8rem;font-weight:500;letter-spacing:.12em;}
.st-key-run button:hover{background:var(--accent);border-color:var(--accent);color:var(--paper);}
.st-key-sample button{background:transparent;border:none;color:var(--muted);text-decoration:underline;text-underline-offset:5px;padding:.55rem 0;}
.st-key-sample button:hover{background:transparent;color:var(--accent);}
.st-key-dl_full button,.st-key-dl_anki button{background:transparent;color:var(--ink);border:1px solid var(--ink);border-radius:4px;padding:.45rem 1.2rem;}
.st-key-dl_full button:hover,.st-key-dl_anki button:hover{background:var(--ink);color:var(--paper);}
[data-testid="stExpander"] details{border:none!important;border-top:1px solid var(--line)!important;border-radius:0!important;background:transparent!important;}
[data-testid="stExpander"] summary{padding-left:0;color:var(--muted);font-size:.88rem;}
.stats{display:flex;border-top:1px solid var(--ink);border-bottom:1px solid var(--line);margin:2.4rem 0 1.4rem;}
.stat{flex:1;padding:1rem 0 .9rem;}
.stat b{display:block;font-family:'Noto Serif TC',serif;font-size:2rem;font-weight:700;line-height:1.1;}
.stat span{font-size:.78rem;color:var(--muted);letter-spacing:.16em;}
.tbl-wrap{overflow-x:auto;margin-bottom:1.6rem;}
table.vocab{width:100%;min-width:640px;border-collapse:collapse;font-size:.95rem;}
.vocab th{font-size:.72rem;font-weight:500;color:var(--muted);letter-spacing:.16em;text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--ink);}
.vocab td{padding:.8rem .6rem;border-bottom:1px solid var(--line);vertical-align:top;}
.vocab td.n{color:var(--muted);font-size:.8rem;width:2rem;}
.vocab td.w{font-family:'Noto Sans KR',sans-serif;font-weight:500;font-size:1.1rem;white-space:nowrap;}
.vocab td.c{white-space:nowrap;}
.vocab td.f{text-align:center;color:var(--muted);}
.vocab td.e{font-family:'Noto Sans KR','Noto Sans TC',sans-serif;font-size:.88rem;line-height:1.7;color:#4A443B;}
.pos{font-size:.72rem;border:1px solid var(--line);border-radius:99px;padding:.1rem .55rem;color:var(--muted);white-space:nowrap;}
.vocab mark{background:rgba(194,65,45,.14);color:inherit;padding:0 .1rem;border-radius:2px;}
.foot{font-size:.78rem;color:var(--muted);margin:1.4rem 0 .8rem;}
@media (max-width:640px){.hero h1{font-size:1.7rem;}.sub{padding-left:0;}.stat b{font-size:1.5rem;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_resource(show_spinner="正在載入 JVM 與 KoNLPy Okt 分析器...")
def init_okt():
    from konlpy.tag import Okt
    return Okt()

@st.cache_resource
def get_trans_cache():
    return {}

def fetch_translation(word: str) -> tuple[str, str]:
    err_msg = ""
    try:
        from deep_translator import GoogleTranslator
        res = GoogleTranslator(source="ko", target="zh-TW").translate(word)
        return res or "", ""
    except Exception as e:
        err_msg = repr(e)

    try:
        from deep_translator import MyMemoryTranslator
        res = MyMemoryTranslator(source="ko-KR", target="zh-TW").translate(word)
        return res or "", ""
    except Exception as e:
        return "", f"{err_msg} | Fallback Error: {repr(e)}"

def batch_translate(words: list[str]) -> tuple[list[str], str]:
    cache = get_trans_cache()
    missing_words = [w for w in words if w not in cache]
    last_err = ""
    
    if missing_words:
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(fetch_translation, missing_words)
            for word, (trans, err) in zip(missing_words, results):
                if trans:
                    cache[word] = trans
                elif err:
                    last_err = err
                    
    return [cache.get(w, "") for w in words], last_err

def parse_korean_text(text: str, okt, skip_basic: bool = False) -> pd.DataFrame:
    vocab_dict = OrderedDict()

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        tokens = okt.pos(line, stem=True)
        for word, tag in tokens:
            if tag not in POS_MAP:
                continue
            if len(word) < 2 or not HANGUL_RE.search(word):
                continue
            if skip_basic and word in BASIC_WORDS:
                continue

            if word not in vocab_dict:
                vocab_dict[word] = {
                    "pos": POS_MAP[tag],
                    "count": 0,
                    "example": line
                }
            vocab_dict[word]["count"] += 1

    records = [
        {
            COL_WORD: w,
            COL_POS: info["pos"],
            COL_FREQ: info["count"],
            COL_EXAMPLE: info["example"]
        }
        for w, info in vocab_dict.items()
    ]
    
    return pd.DataFrame(records, columns=[COL_WORD, COL_POS, COL_FREQ, COL_EXAMPLE])

def highlight_keyword(sentence: str, word: str, pos: str) -> str:
    stem = word[:-1] if pos != "名詞" and word.endswith("다") else word
    escaped_sentence = html.escape(sentence)
    escaped_stem = html.escape(stem)
    
    if escaped_stem and escaped_stem in escaped_sentence:
        return escaped_sentence.replace(escaped_stem, f"<mark>{escaped_stem}</mark>", 1)
    return escaped_sentence

def render_html_table(df: pd.DataFrame) -> str:
    has_trans = COL_TRANS in df.columns
    headers = ["#", "單字"] + (["中文"] if has_trans else []) + ["詞性", "次數", "例句"]
    th_html = "".join(f"<th>{h}</th>" for h in headers)

    rows = []
    for idx, row in enumerate(df.to_dict("records"), start=1):
        cell_data = f'<td class="n">{idx}</td><td class="w">{html.escape(row[COL_WORD])}</td>'
        if has_trans:
            cell_data += f'<td class="c">{html.escape(row[COL_TRANS])}</td>'
        cell_data += (
            f'<td><span class="pos">{row[COL_POS]}</span></td>'
            f'<td class="f">{row[COL_FREQ]}</td>'
            f'<td class="e">{highlight_keyword(row[COL_EXAMPLE], row[COL_WORD], row[COL_POS])}</td>'
        )
        rows.append(f"<tr>{cell_data}</tr>")

    return f'<div class="tbl-wrap"><table class="vocab"><thead><tr>{th_html}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

def render_summary_stats(df: pd.DataFrame) -> str:
    counts = df[COL_POS].value_counts()
    metrics = [
        ("生詞總數", len(df)),
        ("名詞", int(counts.get("名詞", 0))),
        ("動詞", int(counts.get("動詞", 0))),
        ("形容詞", int(counts.get("形容詞", 0))),
    ]
    stat_boxes = "".join(f'<div class="stat"><b>{num}</b><span>{label}</span></div>' for label, num in metrics)
    return f'<div class="stats">{stat_boxes}</div>'

def export_full_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")

def export_anki_csv(df: pd.DataFrame) -> bytes:
    anki_rows = []
    for r in df.to_dict("records"):
        trans = r.get(COL_TRANS, "")
        back_text = f"{trans}（{r[COL_POS]}）\n{r[COL_EXAMPLE]}" if trans else f"（{r[COL_POS]}）\n{r[COL_EXAMPLE]}"
        anki_rows.append(back_text)
        
    anki_df = pd.DataFrame({"front": df[COL_WORD], "back": anki_rows})
    return anki_df.to_csv(index=False, header=False).encode("utf-8-sig")

st.markdown(
    '<div class="hero"><div class="seal">단<br>어</div><h1>韓文歌詞生詞卡</h1></div>'
    '<div class="sub">結合斷詞與語幹還原技術的語言學習工具</div>',
    unsafe_allow_html=True,
)

user_text = st.text_area(
    "韓文內容",
    key="text",
    height=420,
    label_visibility="collapsed",
    placeholder="請貼上韓文歌詞、劇本台詞或短文文章...",
)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    add_trans = st.toggle("附上中文翻譯", value=True)
with col2:
    skip_basic = st.toggle("略過高頻基本詞", value=False)
with col3:
    sort_mode = st.selectbox("排序方式", ["出現順序", "出現次數"])

btn_col1, btn_col2, _ = st.columns([1.1, 1, 2])
with btn_col1:
    run_btn = st.button("開始解析生詞", key="run", type="primary")
with btn_col2:
    st.button("載入範例文本", key="sample", on_click=lambda: st.session_state.update({"text": SAMPLE_TEXT}))

if run_btn:
    if not user_text.strip():
        st.warning("請先輸入韓文文本。")
    else:
        try:
            okt = init_okt()
        except Exception as e:
            st.error("KoNLPy/JVM 環境初始化失敗，請確認部署環境（如 packages.txt）是否安裝 Java Runtime (default-jre)。")
            st.code(str(e))
            st.stop()

        with st.spinner("正在進行自然語言斷詞與語幹分析..."):
            df = parse_korean_text(user_text, okt, skip_basic)
            st.session_state["trans_error"] = ""

            if add_trans and not df.empty:
                translations, err_log = batch_translate(list(df[COL_WORD]))
                df.insert(1, COL_TRANS, translations)
                st.session_state["trans_error"] = err_log

            st.session_state["vocab_df"] = df

if "vocab_df" in st.session_state:
    df = st.session_state["vocab_df"].copy()

    if df.empty:
        st.info("未檢測到可提煉之生詞，請確認輸入文本包含韓文。")
    else:
        if sort_mode == "出現次數":
            df = df.sort_values(COL_FREQ, ascending=False, kind="stable")
        df = df.reset_index(drop=True)

        st.markdown(render_summary_stats(df), unsafe_allow_html=True)

        if COL_TRANS not in df.columns:
            st.caption("未啟用翻譯模式。開啟「附上中文翻譯」切換關可獲得自動翻譯。")
        elif (df[COL_TRANS] == "").all():
            st.warning("網路翻譯服務回應異常，已保留原始詞條。")
            if st.session_state.get("trans_error"):
                st.code(st.session_state["trans_error"])

        st.markdown(render_html_table(df), unsafe_allow_html=True)

        dl1, dl2, _ = st.columns([1.3, 1.3, 1])
        with dl1:
            st.download_button(
                "下載完整數據 CSV",
                data=export_full_csv(df),
                file_name="korean_vocab_full.csv",
                mime="text/csv",
                key="dl_full",
            )
        with dl2:
            st.download_button(
                "下載 Anki 記憶卡 CSV",
                data=export_anki_csv(df),
                file_name="korean_vocab_anki.csv",
                mime="text/csv",
                key="dl_anki",
            )

        st.markdown('<div class="foot">註：翻譯數據採用機翻服務 API，特定語境下可能存在差異。</div>', unsafe_allow_html=True)

        with st.expander("Anki 卡片匯入說明"):
            st.markdown(
                "1. 下載「Anki 記憶卡 CSV」檔案。\n"
                "2. 打開 Anki，選擇「檔案 → 匯入」，分隔符號設定為 `逗號`。\n"
                "3. 欄位映射設定：第 1 欄指定為「正面 (Front)」，第 2 欄指定為「背面 (Back)」。"
            )
