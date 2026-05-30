#  Suneo Discord Bot (The Ultimate Cloud-Native Edition)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11.9-green.svg)
![Deployment](https://img.shields.io/badge/deployment-Render-purple.svg)
![Framework](https://img.shields.io/badge/discord.py-slash__commands-red.svg)

An AI-powered, highly opinionated Discord bot built with Python. Suneo is designed to live 24/7 in the cloud, utilizing the Groq API for lightning-fast responses, advanced Slash Commands, and a local JSON-based memory system to remember conversational context. 

##  Inspiration & Origin
**Inspired by the classic character Suneo Honekawa (from Doraemon).** This bot was built to bring a sassy, flexing, "rich-kid" persona to Discord servers, specializing in Hinglish roasts and witty banter. 

The architecture was specifically engineered to overcome the limitations of local desktop hosting. We stripped away heavy GUI libraries (PyQt) and local hardware dependencies (keyboard hotkeys, local audio) to create a **Headless Cloud-Native** application that runs infinitely on Render's free tier.

---

##  Core Features
* **AI-Powered Brain:** Integrates with the Groq API (LLaMA/Mixtral models) for fast and highly capable conversational AI responses.
* **Slash Commands:** Fully utilizes Discord's Application Commands API for a professional, interactive UI directly in the chat box.
* **Persistent Memory:** Uses a local JSON-based file system (`suneo_memory.json`) to keep track of users, profiles, and past channel history.
* **24/7 Cloud Ready:** Includes a lightweight Flask web server running on a background thread to satisfy Render's port-binding requirements, keeping the bot alive around the clock.
* **Headless Design:** Completely stripped of desktop-bound libraries (no `pyttsx3`, `pyautogui`, or `PyQt`) to prevent server crashes in headless Linux environments.

---

## Tech Stack & Requirements
* **Language:** Python 3.11.9 *(Strictly enforced via `.python-version`)*
* **Libraries:** `discord.py` (API), `Flask` (Dummy Server), `requests`
* **Infrastructure:** Render (Web Service), GitHub (CI/CD)

---

##  Local Development & Setup Commands
If you want to run or test Suneo locally on your Windows machine before pushing to the cloud, follow these exact steps:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/suneo-bot.git
cd suneo-bot
```

### 2. Set Up a Virtual Environment (Recommended)
Isolate your Python dependencies so they don't interfere with your system:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secret Keys
Create a file named `.env` in the root folder. **(Never commit this to GitHub!)**
```ini
DISCORD_BOT_TOKEN=your_discord_token_here
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the Bot
```bash
python main.pyw
```

---

##  Advanced Slash Commands Guide
Suneo utilizes modern Discord Application Commands (`/commands`). 

### The 3-Second Rule (Deferring)
Discord requires bots to respond to slash commands within 3 seconds. Because the Groq AI takes time to generate roasts, Suneo uses `await interaction.response.defer()` to tell Discord "Suneo is thinking...". This buys the AI up to 15 minutes to reply using `followup.send()`.

### Code Reference for Suneo's Commands:
```python
# 1. Syncing commands on boot
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'[SYSTEM] Suneo is online and synced!')

# 2. Instant Reply Command (No AI)
@bot.tree.command(name="flex", description="See Suneo's bank balance.")
async def flex(interaction: discord.Interaction):
    await interaction.response.send_message("Bhai, my dad just bought me a new yacht. 🤑")

# 3. AI Deferred Command
@bot.tree.command(name="roast", description="Brutally roast someone in Hinglish!")
@app_commands.describe(target="Tag the poor guy you want to roast")
async def roast(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.defer() # Buy time!
    
    # Generate AI roast here...
    ai_response = f"Arre {target.mention}, tera poora khandaan jitna kamata hai, utna toh main..."
    
    await interaction.followup.send(ai_response) # Send final result
```

---

##  Cloud Deployment Guide (Render)
Suneo is optimized to run on Render's free tier. 

1. Create a **New Web Service** on Render and link your GitHub repository.
2. Configure the following settings:
   * **Language:** Python
   * **Start Command:** `python main.pyw`
3. Add the following **Environment Variables** in the Render dashboard:
   * `DISCORD_BOT_TOKEN` : *(Your raw Discord Token)*
   * `GROQ_API_KEY` : *(Your raw Groq API Key)*
   * `PYTHON_VERSION` : `3.11.9` *(Crucial for audioop compatibility)*
4. Ensure you have a `.python-version` file in your repository containing exactly `3.11.9` to force Render to bypass newer, broken Python versions.
5. Deploy the service. The built-in Flask app will bind to Render's required port, and the Discord bot will initialize simultaneously.

---

## Versioning and Tagging (Git)
To keep track of different versions of Suneo (e.g., v1.0.0 for launch, v2.0.0 for future updates), we use Git Tags. 

### Create a Release Tag:
```bash
git tag -a v1.0.0 -m "First stable cloud launch with Slash Commands"
git push origin v1.0.0
```
*(You can now go to your GitHub repository, click on "Releases/Tags", and you will see a snapshot of the code at this exact moment!)*

### Pushing Normal Updates:
When you add new commands to `main.pyw`:
```bash
git add .
git commit -m "Added a new flex slash command"
git push
```
*(Render will automatically detect this push and redeploy the bot in ~2 minutes. Note: You may need to restart your Discord app to clear the slash command cache).*

---
## 🤝 Contributing
Built with ❤️ by Shresth Panigrahi. 
Feel free to fork, add more savage Hinglish roasts to the prompt, and submit a pull request!
