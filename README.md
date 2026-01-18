# 🌿 PurePath

**PurePath** is a real-time "truth-checker" for sustainability. We use AI to cut through the "marketing fog" and spot greenwashing—the practice of companies pretending to be eco-friendly to trick consumers. 

Instead of taking a brand's word for it, PurePath gives you a data-backed **Truth Score** in seconds.

---

## 💡 Inspiration
We were tired of seeing leaves and "eco-friendly" labels on everything when nearly **80% of corporate sustainability claims** are actually exaggerated or lack verifiable evidence. We built PurePath because if professional investors are confused by greenwashing, regular shoppers don't stand a chance.

## 🛠️ What it Does
* **Scrape Promises**: Uses the **Yellowcake API** to "read" corporate sites and extract specific commitments like "Net Zero by 2030" or "Plastic-Free".
* **Verify Reality**: **Gemini 2.5 Flash** scans news reports, legal filings, and environmental studies for contradictions (e.g., hidden emissions or climate lobbying).
* **Truth Score**: Generates an intuitive 0–100 score to help you identify true environmental leaders.

## 🚀 Tech Stack
*  [Gemini 2.5 Flash](https://aistudio.google.com/) (Reasoning & Conflict Analysis)
* [Yellowcake API](https://docs.yellowcake.dev/) (Intelligent Structured Scraping)
* Python + Pydantic (Data Integrity & Schemas)
* *Streamlit (Real-time SSE Data Streaming)
