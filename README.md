# 澳門樓宇滲漏水簡易自查

一個單頁、純靜態的公益網站，幫助澳門居民在遇到樓宇滲漏水問題時，
先按「幾時出現」判斷方向，再做 3 個簡單自測初步收窄滲漏源頭；
仍未能解決時，指引官方諮詢、必要仲裁及協助途徑。

🔗 **網站：** https://ronlam1981.github.io/water_leakage/

---

## 網站結構（單頁）

| 區塊 | 內容 |
| --- | --- |
| 首屏 | 天花滴水、牆身發霉，點判斷原因？＋ 自測限制聲明 ＋ 主按鈕「開始簡單自測」 |
| 第一步 | 看出現時間 —— 6 種時間線索與可能原因 |
| 第二步 | 做 3 個簡單自測 —— 拍照做記號、水錶測試、分位置放水測試 |
| 第三步 | 按結果處理 —— 大概找到源頭／仍然不肯定／對方不配合 |
| 第二部分 | 需要幫手？—— 樓宇滲漏水聯合處理中心、必要仲裁、宇見顧問 |
| 頁尾 | 簡短聲明與製作單位 |

全站四個主要按鈕：**開始簡單自測**、**查看官方手冊**、**了解必要仲裁**、**WhatsApp 宇見諮詢**。

## 內容與版權

- 網站文字為自行撰寫，內容參考澳門特別行政區政府公開資料，並以連結指回官方網頁。
- **網站不使用任何官方刊物的圖片或圖表**，亦無轉載原文段落。
- 頁尾載明：只供一般資訊及初步自查，不構成工程檢測結論或法律意見。

官方連結：

- 《處理樓宇滲漏常識》 https://www.ihm.gov.mo/zh/node-1173
- 樓宇滲漏水聯合處理中心 https://www.ihm.gov.mo/zh/node-82
- 法務局 · 滲漏水爭議的必要仲裁 https://www.dsaj.gov.mo/service/ranlriae.aspx

## 技術

純靜態 HTML + CSS，**沒有 JavaScript、沒有框架、沒有追蹤程式、不收集任何資料**。
響應式設計，手機至桌面均可使用。

```
index.html                      單頁網站（直接編輯）
assets/css/style.css            樣式
assets/img/flowchart-redraw.svg 自製流程圖（現時未使用，保留備用）
tools/make_flowchart.py         產生上述流程圖
docs/圖片替換清單.md             舊版圖片資料（現時未使用，保留備用）
.github/workflows/pages.yml     推送即自動部署到 GitHub Pages
```

## 本地預覽

```bash
python3 -m http.server 8000     # 然後開啟 http://localhost:8000
```

## 更新方法

直接改 `index.html`，然後：

```bash
git add -A && git commit -m "更新內容" && git push
```

GitHub Actions 會自動重新部署。

> 舊版（11 頁、含 20 節點互動自檢、官方刊物圖片與詳細章節）保留在 git 歷史中，
> 見 commit `6c6aeef` 及之前。

---

## 聯絡

**宇見顧問有限公司 U Vision Consulting**

- WhatsApp／電話：[+853 6679 8555](https://wa.me/85366798555)
- 電郵：[uvisionconsulting@gmail.com](mailto:uvisionconsulting@gmail.com)
- 地址：澳門桔仔街 65 號一樓（到訪請提前預約）
