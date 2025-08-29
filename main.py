import os
import json
import random
import logging
import asyncio
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import app_commands

# -------------------------
# Boot / Logging / Intents
# -------------------------
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.members = True  # needed for member join, kick/ban, role mgmt

# Command prefix is irrelevant for slash commands, but Bot still needs one
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")  # optional: you can implement a custom /help later

# -------------------------
# Config & Files
# -------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

currency_file = "currency.json"
currency = {}

# Load word lists
with open("words.txt", "r", encoding="utf-8") as r:
    words1 = [line.strip() for line in r if 3 <= len(line.strip()) <= 8]

with open("common_words.txt", "r", encoding="utf-8") as g:
    hwords = [word.strip() for word in g.readlines()]

# -------------------------
# Currency helpers
# -------------------------
def load_currency():
    global currency
    if os.path.exists(currency_file):
        try:
            with open(currency_file, "r", encoding="utf-8") as f:
                currency = json.load(f)
        except json.JSONDecodeError:
            print("currency.json corrupted, resetting currency data.")
            currency = {}
    else:
        currency = {}

def save_currency():
    with open(currency_file, "w", encoding="utf-8") as f:
        json.dump(currency, f, indent=4)

def get_balance(user_id: int) -> int:
    user_id = str(user_id)
    if user_id not in currency:
        currency[user_id] = 1000  # starting balance
        save_currency()
    return currency[user_id]

def update_balance(user_id: int, amount: int):
    user_id = str(user_id)
    if user_id not in currency:
        currency[user_id] = 1000
    currency[user_id] += amount
    save_currency()

def get_formatted_balance(user_id: int) -> str:
    return f"{get_balance(user_id):,}"

# -------------------------
# Game state
# -------------------------
games = {}  # per-user hangman state
# { user_id: {word:str, guessed:list[str], attempts:int, guessedletters:list[str]} }

slotemojis = ['💰', '🧶', '🐀', '🐟', '🐾']

# Pre-load currency
load_currency()

# -------------------------
# Ready / Sync
# -------------------------
@bot.event
async def on_ready():
    # Sync global slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Failed to sync: {e}")
    print(f"We are ready to go in, {bot.user.name}")

# -------------------------
# Member join (DM welcome)
# -------------------------
@bot.event
async def on_member_join(member: discord.Member):
    try:
        await member.send(f"Welcome to the server {member.name}")
    except discord.Forbidden:
        # DM closed; ignore
        pass

# =========================
# Moderation & Management
# =========================
@app_commands.default_permissions(manage_messages=True)
@bot.tree.command(name="purge", description="Delete the last N messages in this channel (default 5).")
@app_commands.describe(amount="Number of messages to delete (1-100)")
async def purge(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100] = 5):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount+1)  # includes the command message
    await interaction.followup.send(f"🧹 Deleted {len(deleted)-1} messages.", ephemeral=True)

@app_commands.default_permissions(kick_members=True)
@bot.tree.command(name="kick", description="Kick a member.")
@app_commands.describe(member="Member to kick", reason="Reason for the kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member.mention} was kicked. Reason: {reason}")

@app_commands.default_permissions(ban_members=True)
@bot.tree.command(name="ban", description="Ban a member.")
@app_commands.describe(member="Member to ban", reason="Reason for the ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)  # fixed correct usage
    await interaction.response.send_message(f"🔨 {member.mention} was banned. Reason: {reason}")

@app_commands.default_permissions(manage_roles=True)
@bot.tree.command(name="assign", description="Assign a role to a member.")
@app_commands.describe(member="Member to assign the role to", role_name="Exact name of the role")
async def assign(interaction: discord.Interaction, member: discord.Member, role_name: str):
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role:
        await member.add_roles(role, reason=f"Assigned by {interaction.user}")
        await interaction.response.send_message(f"{member.mention} is now assigned to **{role_name}**")
    else:
        await interaction.response.send_message(f"❌ The role '**{role_name}**' does not exist.", ephemeral=True)

@app_commands.default_permissions(manage_roles=True)
@bot.tree.command(name="remove", description="Remove a role from a member.")
@app_commands.describe(member="Member to remove the role from", role_name="Exact name of the role")
async def remove(interaction: discord.Interaction, member: discord.Member, role_name: str):
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role:
        await member.remove_roles(role, reason=f"Removed by {interaction.user}")
        await interaction.response.send_message(f"{member.mention} has had **{role_name}** removed")
    else:
        await interaction.response.send_message(f"❌ The role '**{role_name}**' does not exist.", ephemeral=True)

@bot.tree.command(name="dm", description="Send a DM to a member.")
@app_commands.describe(member="Member to DM", message="Message to send")
async def dm(interaction: discord.Interaction, member: discord.Member, message: str):
    try:
        await member.send(message)
        await interaction.response.send_message(f"📩 DM sent to {member.mention}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ Cannot DM this user (privacy settings).", ephemeral=True)

@bot.tree.command(name="poll", description="Create a thumbs up/down poll.")
@app_commands.describe(question="Question to ask")
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="🗳️ Poll", description=question)
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

# =========================
# Utility / Fun
# =========================
@bot.tree.command(name="hello", description="Say hello.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention}, hope you're having a good day!")

@bot.tree.command(name="eightball", description="Ask the magic 8-ball a question.")
@app_commands.describe(question="Your question")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain!", "It is decidedly so!", "Without a doubt!", "Yes – definitely!",
        "You may rely on it!", "As I see it, yes!", "Most likely!", "Outlook good!",
        "Yes!", "Signs point to yes!", "Reply hazy, try again…", "Ask again later…",
        "Better not tell you now…", "Cannot predict now…", "Concentrate and ask again…",
        "Don't count on it!", "My reply is no!", "My sources say no!", "Outlook not so good!",
        "Very doubtful!"
    ]
    await interaction.response.send_message(f"🔮 **Question:** {question}\n🎱 **Answer:** {random.choice(responses)}")

@bot.tree.command(name="flip", description="Flip a coin.")
async def flip(interaction: discord.Interaction):
    result = random.choice(["🪙 Heads!", "🪙 Tails!"])
    await interaction.response.send_message("🪙 Flipping the coin...")
    await interaction.followup.send(f"🎲 **Result:** {result}")

@bot.tree.command(name="roll", description="Roll a six-sided die.")
async def roll(interaction: discord.Interaction):
    result = random.choice(range(1, 7))
    await interaction.response.send_message("Rolling the dice...")
    await interaction.followup.send(f"🎲 You rolled a **{result}**!")

@bot.tree.command(name="tod", description="Truth or Dare intro.")
async def tod(interaction: discord.Interaction):
    await interaction.response.send_message("Welcome to the game! Would you like to pick 🟦 Truth or 🟥 Dare?\nUse `/truth` or `/dare`.")

@bot.tree.command(name="truth", description="Get a Truth prompt.")
async def truth(interaction: discord.Interaction):
    truths = [
        "What's your most embarrassing moment?",
        "Have you ever had a secret crush on someone in this chat?",
        "What's your weirdest habit?",
        "Have you ever stolen something?",
        "What's something you’ve done that you still regret?",
        "Have you ever cheated on a test?",
        "What’s your guilty pleasure?",
        "What’s your most irrational fear?",
        "Who was your first crush?",
        "Have you ever broken something and blamed someone else?",
        "What’s the most awkward thing that ever happened to you?",
        "What’s a song you secretly love but would never admit?",
        "Have you ever tried to flirt and failed badly?",
        "What’s your most awkward crush story?",
        "What’s a strange talent you have?",
        "Have you ever cried during a movie? Which one?",
        "What’s the meanest thing you’ve ever said to someone?",
        "Have you ever lied to a friend to avoid hanging out?",
        "Have you ever been caught lying?",
        "What’s your biggest insecurity?"
    ]
    await interaction.response.send_message(f"🟦 **Truth:** {random.choice(truths)}")

@bot.tree.command(name="dare", description="Get a Dare prompt.")
async def dare(interaction: discord.Interaction):
    dares = [
        "Send a funny GIF that describes your mood right now.",
        "Change your chat nickname to something silly for the next hour.",
        "Send a message using only emojis for the next 5 messages.",
        "Write a short poem about someone in this chat.",
        "Use an exaggerated compliment on the next person who messages.",
        "Pretend you’re a celebrity and introduce yourself in the chat.",
        "Describe your dream vacation in 3 sentences.",
        "Invent a new dance move and describe it in the chat.",
        "Tag someone and say something nice about them.",
        "Send a message pretending you’re a robot.",
        "Describe your perfect pizza topping combo.",
        "Share your weirdest food craving in the chat.",
        "Pretend you’re a detective and ask a mystery question.",
        "Make a short story using only three sentences.",
        "Describe how you’d survive a zombie apocalypse.",
        "Type the alphabet backward as fast as you can (in chat).",
        "Send a message acting like you just won a lottery.",
        "Pretend you’re an alien visiting Earth and ask a question.",
        "Pretend you’re a chef and describe your signature dish in detail.",
        "Make up a ridiculous excuse for being late to something."
    ]
    await interaction.response.send_message(f"🟥 **Dare:** {random.choice(dares)}")

# =========================
# Economy / Casino
# =========================
@bot.tree.command(name="balance", description="Check your billy bucks balance.")
async def balance(interaction: discord.Interaction):
    bal = get_formatted_balance(interaction.user.id)
    await interaction.response.send_message(f"🐾 **| {interaction.user.mention}**, you currently have **__{bal}__** 🪙 billy bucks")

# A light cooldown for slots
slots_cooldown = commands.CooldownMapping.from_cooldown(1, 5.0, commands.BucketType.user)

@bot.tree.command(name="slots", description="Spin the slot machine with a bet.")
@app_commands.describe(amount="Bet amount (must be > 0)")
async def slots(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 1_000_000]):
    # manual cooldown check for app_commands
    bucket = slots_cooldown.get_bucket(interaction)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        await interaction.response.send_message(f"⏳ Slow down! Try again in {retry_after:.1f}s.", ephemeral=True)
        return

    user_id = interaction.user.id
    bal = get_balance(user_id)

    if amount > bal:
        await interaction.response.send_message(f"{interaction.user.mention} Insufficient billy bucks to bet that amount!", ephemeral=True)
        return

    update_balance(user_id, -amount)
    weights = [73, 10, 10, 3, 2]
    rolls = random.choices(slotemojis, weights=weights, k=3)
    result = " | ".join(rolls)

    embed = discord.Embed(title="🎰 Slot Machine 🎰", color=discord.Color.gold())
    embed.add_field(name="Spinning...", value=result, inline=False)

    if rolls[0] == rolls[1] == rolls[2]:
        emoji = rolls[0]
        multipliers = {'🐾': 10, '🐀': 5, '💰': 2, '🧶': 5, '🐟': 3}
        multiplier = multipliers.get(emoji, 1)
        winnings = amount * multiplier
        update_balance(user_id, winnings)
        embed.description = f"🎉 {interaction.user.mention}, you hit 3 {emoji} and won **{winnings}** billy bucks 🪙! 🎉\n"
        embed.color = discord.Color.green()
    else:
        embed.description = f"Better luck next time, {interaction.user.mention}!\nYou lost **{amount}** billy bucks.\n"
        embed.color = discord.Color.red()

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="send", description="Send billy bucks to another member.")
@app_commands.describe(amount="Amount to send (>0)", member="Recipient")
async def send(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 1_000_000], member: discord.Member):
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't send coins to yourself.", ephemeral=True)
        return

    sender_id = interaction.user.id
    receiver_id = member.id
    sender_balance = get_balance(sender_id)

    if amount > sender_balance:
        await interaction.response.send_message("❌ You don't have enough billy bucks to send!", ephemeral=True)
        return

    update_balance(sender_id, -amount)
    update_balance(receiver_id, amount)
    await interaction.response.send_message(f"💸 {interaction.user.mention} sent **{amount}** 🪙 billy bucks to {member.mention}!")

# =========================
# Hangman (Slash-based)
# =========================
@bot.tree.command(name="hangman", description="Start a game of Hangman.")
async def hangman(interaction: discord.Interaction):
    valid_words = [w for w in hwords if 4 <= len(w) <= 8]
    hmanword = random.choice(valid_words).lower()
    hmanpword = list('-' * len(hmanword))
    # reveal first and last letters as per your original design
    hmanpword[0] = hmanword[0]
    hmanpword[-1] = hmanword[-1]

    games[interaction.user.id] = {
        "word": hmanword,
        "guessed": hmanpword,
        "attempts": 4,
        "guessedletters": []
    }

    await interaction.response.send_message(
        "🎮 **Hangman Game Started!** 🎮\n"
        f"✨ The word to guess: `{' '.join(hmanpword).upper()}`\n"
        "❤️ You have **4 attempts**.\n"
        "Use `/guess <letter>`, `/hint`, `/restart`, or `/quit`."
    )

@bot.tree.command(name="guess", description="Guess a letter for your current Hangman game.")
@app_commands.describe(letter="A single letter to guess")
async def guess(interaction: discord.Interaction, letter: str):
    game = games.get(interaction.user.id)
    if not game:
        await interaction.response.send_message("❌ You are not currently playing hangman. Use `/hangman` to start!", ephemeral=True)
        return

    if len(letter) != 1 or not letter.isalpha():
        await interaction.response.send_message("⚠️ Please guess a **single alphabetical letter**.", ephemeral=True)
        return

    letter = letter.lower()
    word = game["word"]
    guessed = game["guessed"]
    attempts = game["attempts"]
    guessed_letters = game["guessedletters"]

    if letter in guessed_letters:
        await interaction.response.send_message(
            f"⚠️ You already guessed `{letter}`!\n🔡 Guessed letters so far: `{', '.join(sorted(l.upper() for l in guessed_letters))}`",
            ephemeral=True
        )
        return
    else:
        guessed_letters.append(letter)

    found_new = False
    for i, ch in enumerate(word):
        if letter == ch and guessed[i] == '-':
            guessed[i] = letter
            found_new = True

    if found_new:
        msg = "✅ Correct letter!"
    else:
        attempts -= 1
        msg = "❌ Incorrect letter!"
    game["attempts"] = attempts

    display = ' '.join(guessed).upper()
    status = (
        f"{msg}\n"
        f"{display}\n"
        f"🔡 Guessed letters: `{', '.join(sorted(l.upper() for l in guessed_letters))}`\n"
        f"⏳ Attempts remaining: **{attempts}**"
    )

    # Check win/lose
    if '-' not in guessed:
        games.pop(interaction.user.id, None)
        await interaction.response.send_message(f"🎉 You guessed the word: **{word.title()}**")
    elif attempts == 0:
        games.pop(interaction.user.id, None)
        await interaction.response.send_message(f"💀 Game Over! The correct word was **{word.title()}**")
    else:
        await interaction.response.send_message(status)

@bot.tree.command(name="hint", description="Reveal a letter in your Hangman game.")
async def hint(interaction: discord.Interaction):
    game = games.get(interaction.user.id)
    if not game:
        await interaction.response.send_message("❌ You are not currently playing hangman. Use `/hangman` to start!", ephemeral=True)
        return

    guessed = game["guessed"]
    word = game["word"]

    hidden_indices = [i for i, ch in enumerate(guessed) if ch == '-']
    if not hidden_indices:
        await interaction.response.send_message("✅ All letters are already revealed!")
        return

    idx = random.choice(hidden_indices)
    guessed[idx] = word[idx]
    game["guessed"] = guessed

    await interaction.response.send_message(
        "🔎 Here's a hint! One letter has been revealed:\n" + ' '.join(guessed).upper()
    )

@bot.tree.command(name="restart", description="Restart your Hangman game.")
async def restart(interaction: discord.Interaction):
    # Remove old game (if any) then start a new one
    games.pop(interaction.user.id, None)
    await hangman.callback(interaction)  # reuse the hangman command's logic

@bot.tree.command(name="quit", description="Quit your Hangman game.")
async def quit_game(interaction: discord.Interaction):
    if interaction.user.id in games:
        games.pop(interaction.user.id, None)
        await interaction.response.send_message("🛑 Your Hangman game has been ended. Use `/hangman` to start a new game anytime.")
    else:
        await interaction.response.send_message("❌ You are not currently playing hangman. Use `/hangman` to start!", ephemeral=True)

# =========================
# Word Scramble (Slash)
# =========================
@bot.tree.command(name="scramble", description="Start a word scramble (reply with your guesses in chat).")
async def scramble(interaction: discord.Interaction):
    word1 = random.choice(words1)
    scrambled = ''.join(random.sample(word1, len(word1)))
    while scrambled == word1:
        scrambled = ''.join(random.sample(word1, len(word1)))

    await interaction.response.send_message(
        f"**🔤 Word Scramble!**\nUnscramble this word: `{scrambled}`\n"
        "You have 3 tries. Just type your guess in this channel."
    )

    def check(m: discord.Message):
        return (
            m.author == interaction.user and
            m.channel == interaction.channel
        )

    tries = 3
    while tries > 0:
        try:
            guess_msg = await bot.wait_for('message', check=check, timeout=60)
            guess = guess_msg.content.strip()

            if guess.lower() == word1.lower():
                await interaction.followup.send(f"🎉 Correct! Well done, {interaction.user.mention}!")
                return
            else:
                tries -= 1
                if tries > 0:
                    await interaction.followup.send(f"❌ Nope! {tries} {'tries' if tries>1 else 'try'} left.")
                else:
                    await interaction.followup.send(f"❌ Out of tries! The word was `{word1.title()}`.")
        except asyncio.TimeoutError:
            await interaction.followup.send(f"⌛ Time's up! The word was `{word1.title()}`.")
            return

# =========================
# Run
# =========================
# If you're hosting somewhere like Replit and have a keep-alive webserver, import and start it here:
try:
    import webserver
    webserver.keep_alive()
except Exception:
    pass

bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
