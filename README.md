<div align="center">
  <h1>🌸 彩葉 (Iroha)</h1>
  <p>您的 Discord 專屬貓娘女僕小幫手 🐾</p>
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://discordpy.readthedocs.io/)
  [![GitHub Profile](https://img.shields.io/badge/GitHub-Natsukawa--Taoyuan-181717?logo=github)](https://github.com/Natsukawa-Taoyuan)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

## 📖 關於專案 (About Iroha)

**「主人歡迎回來喵！今天有什麼彩葉可以幫您的嗎？」**

彩葉 (Iroha) 是一款以「貓娘女僕」為主題的 Discord 娛樂與管理機器人。最初作為非商業 Side Project 誕生，旨在提供自動化管理、減輕伺服器管理員負擔，同時為群組成員帶來溫暖又充滿趣味的互動體驗。

## ✨ 核心特色功能 (Features)

* **💬 日常貼心問候**：感應對話中的「早安」、「午安」、「晚安」，並根據不同時段給予專屬的貓娘語氣回應（具備開發者專屬撒嬌彩蛋）。
* **🎲 機率運算系統 (`/roll`)**：公正的隨機數生成器，彩葉會根據擲出的結果給予趣味點評。
* **🔮 每日運勢預測 (`/luck`)**：連線至貓娘資料庫，測算今日的幸運指數（大吉至大凶）並附上貼心小建議。
* **🔨 制裁壞壞 (`/bonk`)**：匿名敲擊發表不當內容的成員，發送 Bonk 迷因圖以維護頻道純淨。
* **🍔 凌晨三點美味蟹堡**：支援各伺服器獨立排程，凌晨 3:00 準時發送派大星吃蟹堡的經典迷因圖。
* **👀 開發者保護機制**：防擾設計，當特定成員標記開發者時，彩葉會主動出面阻擋。
* **⚙️ 模組化設定中心 (`/iroha_setup`)**：管理員可依據伺服器風氣，自由開關上述所有功能模組。

## 🛠️ 開發與技術環境 (Tech Stack)

* **程式語言**: Python 3
* **核心框架**: [discord.py](https://github.com/Rapptz/discord.py)
* **資料儲存**: 輕量化 JSON 架構 (`iroha_data.json`) 支援動態伺服器設定 (Guild Config)
* **部署環境**: 支援長時間掛載於虛擬機或容器（如 Proxmox VE 私有雲環境）

## 🚀 如何自己架設 (Installation & Setup)

如果您想在自己的環境測試或架設彩葉，請參考以下步驟：

1. **複製專案 (Clone the repository)**
   ```bash
   git clone [https://github.com/Natsukawa-Taoyuan/Iroha-Bot.git](https://github.com/Natsukawa-Taoyuan/Iroha-Bot.git)
   cd Iroha-Bot