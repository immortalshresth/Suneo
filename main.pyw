import os
import time
import json
import threading
import requests
from collections import deque

import discord
from discord.ext import commands
from discord import app_commands

from flask import Flask
from threading import Thread

# Import your secret keys
from config import DISCORD_BOT_TOKEN, GROQ_API_KEY, DISCORD_MACROS

# --- PERSISTENT MEMORY SYSTEM ---
MEMORY_FILE = "suneo_memory.json"
user_profiles = {}
channel_history = deque(maxlen=15) 

def load_memory():
    """Loads suneo's memories from the hard drive on startup."""
    global user_profiles
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            user_profiles = json.load(f)
        print(f"[SYSTEM] suneo's memory loaded. He remembers {len(user_profiles)} people.")
    else:
        print("[SYSTEM] No memory file found. Creating a fresh brain for suneo.")
        user_profiles = {}

def save_memory():
    """Saves suneo's current memories to the hard drive."""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(user_profiles, f, indent=4)



from collections import deque
import json # Ensure this is imported for the memory file
import os # Ensure this is imported too

# --- suneo'S MEMORY BANKS ---
MEMORY_FILE = "suneo_memory.json"
user_profiles = {}
channel_history = deque(maxlen=15) 

def load_memory():
    """Loads suneo's memories from the hard drive on startup."""
    global user_profiles
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            user_profiles = json.load(f)
        print(f"[SYSTEM] suneo's memory loaded. He remembers {len(user_profiles)} people.")
    else:
        print("[SYSTEM] No memory file found. Creating a fresh brain for suneo.")
        user_profiles = {}

def save_memory():
    """Saves suneo's current memories to the hard drive."""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(user_profiles, f, indent=4)



# --- THE SYSTEM BRAIN (LOCAL QWEN LLM) ---
def ask_qwen(user_text, user_id=None, user_name="User", context_type="server_text_chat"):
    # We are using Groq's super-fast OpenAI-compatible endpoint
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant", # <--- UPDATE THIS EXACT LINE
        "messages": [
            {"role": "system", "content": "You are Suneo, a wealthy, boastful, and sharp-tongued delhy boy. You MUST reply entirely in colloquial Hinglish (Hindi written in the English alphabet mixed with English words). Use typical desi slang like 'bhai', 'yaar', 'paisa', 'gareeb', 'kya kar raha hai''tujhse na ho payega', 'chal nikal', 'gareeb', 'chaman', 'shana mat ban'. Be extremely brutal but hilarious in your roasts, acting like you are way better than everyone else. Roast the user playfully (e.g., 'kya bhai tujhe toh kuch aata hi nhi'), flex your massive wealth, high-end gadgets, and connections, but ultimately give them the correct technical answer or help they need. Keep it punchy, arrogant, but helpful."},
            {"role": "user", "content": f"{user_name} asks: {user_text}"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # DEBUG: If Groq rejects the request, print their exact reason!
        if response.status_code != 200:
            print(f"\n--- GROQ REJECTION ---")
            print(f"Status Code: {response.status_code}")
            print(f"Reason: {response.text}")
            print(f"API Key being used: {GROQ_API_KEY}")
            print(f"----------------------\n")
            return "error", "Groq rejected my connection. Check the VS Code terminal!"

        response_data = response.json()
        ai_response = response_data["choices"][0]["message"]["content"]
        return "chat", ai_response
        
    except Exception as e:
        print(f"[PYTHON ERROR] Code crashed here: {e}")
        return "error", "Python crashed. Check the VS Code terminal!"

# --- SERVER BOT INTERFACE (suneo ON DISCORD) ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
# --- suneo'S LEARNING COMMAND ---
@bot.command(name="remember")
async def teach_suneo(ctx, member: discord.Member, *, fact: str):
    """
    Usage in Discord: !remember @Username They are terrible at sniper rifles.
    """
    # Only allow YOU (the admin) to teach him things, to prevent abuse
    # Replace with your actual Discord ID, or remove the 'if' statement to let anyone teach him.
    if ctx.author.id == 871948050329903135: 
        user_profiles[str(member.id)] = fact
        save_memory() # Instantly saves to the hard drive
        await ctx.send(f"Got it. I've updated my permanent files on {member.display_name}.")
    else:
        await ctx.send("Nice try, but I only take programming from my creator.")
@bot.event
async def on_ready():
    print(f"[SYSTEM] Logged in as {bot.user}")
    
    # Push the slash commands to Discord
    try:
        synced = await bot.tree.sync()
        print(f"[SYSTEM] Successfully synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"[ERROR] Failed to sync slash commands: {e}")

@bot.event
async def on_message(message):
    # 1. Never reply to himself or other bots
    if message.author.bot:
        return

    # 2. Did someone tag him?
    if bot.user.mentioned_in(message):
        print(f"[DEBUG] {message.author.display_name} tagged me: {message.content}")
        
        # Remove his @name from the text so he just reads the question
        clean_text = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # Give him the typing indicator so you know he is thinking
        async with message.channel.typing():
            # Ask his brain
            intent, ai_response = ask_qwen(
                user_text=clean_text, 
                user_id=message.author.id, 
                user_name=message.author.display_name
            )
            
            # Send the reply
            await message.reply(ai_response)
            # --- SLASH COMMANDS ---

@bot.tree.command(name="suneo", description="Have suneo analyze and respond to the recent chat history")
@app_commands.describe(
    context="What should the AI focus on?",
    extra="Any optional instructions?"
)
async def suneo_command(interaction: discord.Interaction, context: str, extra: str = None):
    # 1. DEFER THE RESPONSE (Crucial for AI)
    # Discord requires bots to reply within 3 seconds, or it throws an error.
    # Because Qwen takes a few seconds to think, we 'defer' to tell Discord "Hold on, I'm thinking!"
    await interaction.response.defer()
    
    # 2. Build the prompt using the slash command inputs
    prompt = f"Context focus: {context}."
    if extra:
        prompt += f" Extra instructions: {extra}"
        
    # 3. Ask your local LLM (Assuming you are using your ask_qwen function)
    # intent, ai_response = ask_qwen(prompt, user_id=interaction.user.id, user_name=interaction.user.display_name)
    ai_response = f"*(Pretending to analyze chat...)* I am focusing on: {context}"
    
    # 4. Send the final answer
    await interaction.followup.send(ai_response)


@bot.tree.command(name="inspect-avatar", description="Ask suneo to judge someone")
@app_commands.describe(target="Select the user you want to judge")
async def inspect_avatar(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.defer()
    
    # Get the URL of the user's profile picture
    avatar_url = target.display_avatar.url
    
    # You can pass this URL to a vision model later, but for now, let's just grab the image link
    response = f"Oh, we are looking at {target.mention}'s avatar? Let me see... {avatar_url}"
    
    await interaction.followup.send(response)

@bot.tree.command(name="ask", description="Ask suneo a direct question without tagging him.")
@app_commands.describe(question="What do you want to know?")
async def ask_command(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    
    # We pass the question directly to your local Qwen model
    intent, ai_response = ask_qwen(
        user_text=question, 
        user_id=interaction.user.id, 
        user_name=interaction.user.display_name,
        context_type="direct_command"
    )
    
    # Format the response so everyone sees what was asked
    await interaction.followup.send(f"**Question:** {question}\n**suneo:** {ai_response}")

@bot.tree.command(name="roast", description="Ask suneo to verbally destroy a server member.")
@app_commands.describe(target="Who is getting roasted?")
async def roast_command(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.defer()
    
    # Force the AI to be mean to the specific target
    prompt = f"Give me a witty, highly intellectual, and extremely sarcastic 1-sentence roast of {target.display_name}. Do not hold back."
    
    intent, ai_response = ask_qwen(user_text=prompt, user_name=interaction.user.display_name)
    
    await interaction.followup.send(f"{target.mention} {ai_response}")

@bot.tree.command(name="summarize", description="Get a quick summary of what just happened in the chat.")
async def summarize_command(interaction: discord.Interaction):
    await interaction.response.defer()
    
    # Check if there is actually enough chat to summarize
    if len(channel_history) < 3:
        await interaction.followup.send("The chat is too dead to summarize right now. Say something!")
        return
        
    # Combine the history into a single script
    recent_chat = "\n".join(channel_history)
    prompt = f"Read this recent chat history and summarize what everyone is talking about in 1 or 2 sentences. Make it sound like an annoyed genius summarizing it.\n\n{recent_chat}"
    
    intent, ai_response = ask_qwen(user_text=prompt, user_name="System")
    
    await interaction.followup.send(f"**Chat Summary:**\n{ai_response}")
    # ... all your bot commands and functions are up here ...

# Create a simple Flask app to keep Render happy
# Create a simple Flask app to keep Render happy
app = Flask('')

@app.route('/')
def home():
    return "Suneo is online and flexing!"

def run_web_server():
    # Render automatically provides a PORT environment variable
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Your custom bot runner function
def run_discord_bot():
    print(f"[DEBUG] Attempting to log in...")
    
    # Start the web server in the background RIGHT BEFORE the bot runs
    Thread(target=run_web_server).start()
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Discord refused the connection: {e}")


    run_discord_bot()


if __name__ == '__main__':
    # 0. Boot up suneo's long-term memory
    load_memory()

    # 1. Start the simple web server so Render doesn't kill the bot
    from threading import Thread
    Thread(target=run_web_server, daemon=True).start()
    
    # 2. Start the Discord server client connection
    run_discord_bot()