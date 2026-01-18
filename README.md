##🌿 PurePath
PurePath is a truth-checker that helps you spot "greenwashing"—when companies lie about being eco-friendly to trick you. We turn hours of tedious research into a simple 5-second Truth Score so you can shop with confidence.
<img width="1024" height="1024" alt="Gemini_Generated_Image_xeb7q2xeb7q2xeb7" src="https://github.com/user-attachments/assets/8fe53d61-c513-4401-89a2-5573f9d93974" />

##💡 Inspiration
We were tired of the "marketing fog". Every brand has a leaf on its box now, but 80% of those claims are exaggerated or just plain fake. We built this because if the pros can't tell what's real, the rest of us don't stand a chance.

##🛠️ How it Works
Scrape: We use Yellowcake API to "read" corporate sites and pull out specific promises (like "Net Zero by 2030").

Verify: Gemini 2.5 Flash acts as our brain, scanning news and legal reports to see if the company is actually keeping those promises.

Score: You get a 0-100 score. High score = leader. Low score = greenwasher.

##Tech Stack
Brain: Gemini 2.5 Flash (via google-genai)

Hands: Yellowcake API (for structured scraping)

Logic: Python + Pydantic (for clean data)

Face: Streamlit (for the live dashboard)
