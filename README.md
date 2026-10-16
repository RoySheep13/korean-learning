# 韓文歌詞生詞卡：結合 NLP 斷詞與多執行緒翻譯之 Web 應用

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://korean-vocab.streamlit.app/)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red)
![NLP Tool](https://img.shields.io/badge/NLP-KoNLPy%20%2F%20Okt-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> 🌐 **線上體驗 (Live Web App)**：[https://korean-vocab.streamlit.app/](https://korean-vocab.streamlit.app/)

本專案為一款結合 Python 自然語言處理 (NLP) 與 Web 介面的語言學習輔助工具。專為韓文學習者設計，解決韓文屈折變化（Conjugation）繁複導致傳統字典難以查閱原形的痛點，自動從歌詞、劇本或文章中提煉高價值生詞並生成 Anki 記憶卡。

---

## 📌 專案背景與痛點 (Problem Statement)

韓文屬於**黏著語 (Agglutinative Language)**，動詞與形容詞會根據語氣、時態產生豐富的尾綴變化（例如：`먹었어요` -> 原形 `먹다`）。
- **傳統工具痛點**：直接將文章貼入翻譯軟體往往無法精確還原字典原形，且會混雜大量高頻基本詞（如 `하다`, `있다`）。
- **本專案解決方案**：透過形態素分析器提取實詞並還原語幹（Lemma），輔以自動化翻譯與語境例句高亮，一鍵導出標準 Anki 記憶卡格式。

---

## ✨ 核心功能 (Key Features)

- **語幹還原與詞性過濾**：基於 KoNLPy (Okt) 進行形態素解析，精確提取名詞、動詞、形容詞並還原字典原形。
- **多執行緒平行翻譯**：導入 `ThreadPoolExecutor` 進行 API 併發請求，解決單線程網路請求帶來的 GUI 凍結問題。
- **雙重 API 備援機制 (Fallback Handling)**：預設使用 Google Translator，遭遇 Rate Limit 或網路異常時自動切換至 MyMemory 備援機制。
- **語境例句與動態高亮**：使用 HTML `<mark>` 標籤自動匹配例句中的詞幹，呈現單字真實使用語境。
- **雙格式 CSV 導出**：
  - **完整分析表**：包含 UTF-8-SIG (BOM) 編碼，確保 Microsoft Excel 開啟不亂碼。
  - **Anki 記憶卡表**：符合 2-Column（正面：單字 / 背面：翻譯+詞性+例句）標準格式。

---

## 🛠️ 核心架構與工程瓶頸突破 (Engineering Challenges)

```text
[韓文文本輸入]
      │
      ▼
[KoNLPy / Okt 形態素分析] ──▶ (語幹還原 Lemma & 詞性過濾)
      │
      ▼
[ThreadPoolExecutor 多執行緒 pool] ──▶ (4 Workers 併發發送 HTTP 請求)
      │
      ├─▶ [Google Translator API] ──(失敗)─▶ [MyMemory Fallback]
      │
      ▼
[Streamlit UI 渲染 & UTF-8-SIG CSV 導出]