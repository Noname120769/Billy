import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
import webserver
import json
import asyncio

currency_file = "currency.json"
currency={}
with open("words.txt","r") as r:
    words1=[line.strip() for line in r if 3<=len(line.strip())<=8]

def load_currency():
    global currency
    if os.path.exists(currency_file):
        try:
            with open(currency_file, "r") as f:
                currency = json.load(f)
        except json.JSONDecodeError:
            print("currency.json corrupted, resetting currency data.")
            currency = {}
    else:
        currency = {}

def save_currency():
    with open(currency_file, "w") as f:
        json.dump(currency, f, indent=4)

def get_balance(user_id):
    user_id = str(user_id)
    if user_id not in currency:
        currency[user_id] = 1000  # starting balance
        save_currency()
    return currency[user_id]

def update_balance(user_id, amount):
    user_id = str(user_id)
    if user_id not in currency:
        currency[user_id] = 1000
    currency[user_id] += amount
    save_currency()

def get_formatted_balance(user_id):
    return f"{get_balance(user_id):,}"


load_currency()
games={}
slotemojis=  ['💰',  '🧶', '🐀','🐟','🐾']

with open('common_words.txt','r') as g:
    hwords=[word.strip() for word in g.readlines()]

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents,case_insensitive=True)

@bot.event
async def on_ready():
    print(f'We are ready to go in, {bot.user.name}')

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    message_content = message.content.lower()
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention},Hope you're having a Good day!")
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx,amount=5):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f'{amount} messages have been purged')
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx,member:discord.Member):
    await member.kick(reason="The user was rude")
    await ctx.send(f'{member.name} has been kicked from the server')
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx,member:discord.Member,*,reason:str=None):
    await member.ban(f"{reason}")
    await ctx.send(f'{member.name} has been banned from the server')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def assign(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await member.add_roles(role)
        await ctx.send(f"{member.mention} is now assigned to {role_name}")
    else:
        await ctx.send(f"The role '{role_name}' does not exist")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def remove(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} is now removed from {role_name}")
    else:
        await ctx.send(f"The role '{role_name}' does not exist")
@assign.error
async def assign_error(ctx,error):
    if isinstance(error,commands.MissingPermissions):
        await ctx.send("Access Denied:You do not have the required permissions to assign roles")
    else:
        await ctx.send("An error occurred")
@remove.error
async def remove_error(ctx,error):
    if isinstance(error,commands.MissingPermissions):
        await ctx.send("Access Denied:You do not have the required permissions to remove roles")
    else:
        await ctx.send("An error occurred")

@bot.command()
async def dm(ctx,member:discord.Member,*,message):
    await member.send(f'{message}')
    await ctx.send(f'{member.name} has been dmed')
@bot.command()
async def poll(ctx,*,question):
    embed=discord.Embed(title="Polling",description=question)
    poll_message=await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")
@bot.command(aliases=["hm"])
async def hangman(ctx):
    valid_words=[word for word in hwords if len(word)>=4 and len(word)<=8]
    hmanword = random.choice(valid_words)
    hmanpword = list('-' * len(hmanword))
    hmanpword[0] = hmanword[0].title()
    hmanpword[-1] = hmanword[-1].title()
    games[ctx.author.id] = {
        "word": hmanword,
        "guessed": hmanpword,
        "attempts": 4,
        "guessedletters":[]
    }
    await ctx.send("🎮 **Hangman Game Started!** 🎮")
    await ctx.send("🔠 Guess the word by typing letters one at a time using `!guess`.")
    await ctx.send("🔎 Use `!hint` to reveal a letter if you get stuck.")
    await ctx.send(f"✨ The word to guess: `{''.join(hmanpword)}`")
    await ctx.send(f"❤️ You have **4 attempts** remaining. Good luck!")



@bot.command(aliases=["g"])
async def guess(ctx, letter):
    game = games.get(ctx.author.id)
    if not game:
        await ctx.send("You are not currently playing hangman, Please start a new game using the command `!hangman` to play hangman.")
        return
    if len(letter)!= 1 or not letter.isalpha():
        await ctx.send("⚠️ Please guess a single alphabetical letter only.")
        return
    word = game["word"]
    guessed = game["guessed"]
    attempts = game["attempts"]
    letter = letter.lower()
    guessed_letters = game["guessedletters"]

    if letter in guessed_letters:
        await ctx.send(f"⚠️ You already guessed `{letter}`! Please try guessing another letter.")
        await ctx.send(f"🔡 Guessed letters so far: `{', '.join(sorted(letter.upper() for letter in guessed_letters))}`")
        return
    else:
        guessed_letters.append(letter)

    found_new = False
    for i in range(len(word)):
        if letter == word[i] and guessed[i] == '-':
            guessed[i] = letter
            found_new = True

    if found_new:
        await ctx.send("✅ Congrats! You guessed the letter correctly!")
    else:
        await ctx.send("❌ Sorry! You guessed the letter incorrectly!")
        attempts -= 1

    hmanpword = ' '.join(guessed).upper()
    await ctx.send(hmanpword)

    game["guessed"] = guessed
    game["attempts"] = attempts
    games[ctx.author.id] = game

    if '-' not in guessed:
        await ctx.send(f"🎉 Congratulations! You guessed the word: **{word.title()}**")
        games.pop(ctx.author.id)
    elif attempts == 0:
        await ctx.send(f"💀 Game Over! The correct word was **{word.title()}**")
        games.pop(ctx.author.id)
    else:
        await ctx.send(f"🔡 Guessed letters so far: `{', '.join(sorted(letter.upper() for letter in guessed_letters))}`")
        await ctx.send(f"⏳ You have {attempts} attempts remaining")

@bot.command(aliases=["ht"])
async def hint(ctx):
    game = games.get(ctx.author.id)
    if not game:
        await ctx.send("You are not currently playing hangman! Use `!hangman` to start.")
        return
    guessed = game["guessed"]
    word = game["word"]

    hidden_indices = []
    for i in range(len(guessed)):
        if guessed[i] == '-':
            hidden_indices.append(i)

    if len(hidden_indices) == 0:
        await ctx.send("All letters are already revealed!")
        return

    index = random.choice(hidden_indices)
    guessed[index] = word[index]

    game["guessed"] = guessed
    games[ctx.author.id] = game

    await ctx.send("🔎 Here's a hint! One of the letters has been revealed:")
    await ctx.send(''.join(guessed).upper())

@bot.command(aliases=["rs"])
async def restart(ctx):
    if ctx.author.id in games:
        games.pop(ctx.author.id)
    await hangman(ctx)

@bot.command(aliases=["q"])
async def quit(ctx):
    if ctx.author.id in games:
        games.pop(ctx.author.id)
        await ctx.send("🛑 Your Hangman game has been ended. Use `!hangman` to start a new game anytime.")
    else:
        await ctx.send("You are not currently playing hangman! Use `!hangman` to start a new game.")

@bot.command(name='8b')
async def eight_ball(ctx, *, question):
    responses = [
        "🎱 It is certain!",
        "🎱 It is decidedly so!",
        "🎱 Without a doubt!",
        "🎱 Yes – definitely!",
        "🎱 You may rely on it!",
        "🎱 As I see it, yes!",
        "🎱 Most likely!",
        "🎱 Outlook good!",
        "🎱 Yes!",
        "🎱 Signs point to yes!",
        "🎱 Reply hazy, try again…",
        "🎱 Ask again later…",
        "🎱 Better not tell you now…",
        "🎱 Cannot predict now…",
        "🎱 Concentrate and ask again…",
        "🎱 Don't count on it!",
        "🎱 My reply is no!",
        "🎱 My sources say no!",
        "🎱 Outlook not so good!",
        "🎱 Very doubtful!"
    ]
    response = random.choice(responses)
    await ctx.send(f"🔮 **Question:** {question}\n🎱 **Answer:** {response}")

@bot.command(aliases=["f"])
async def flip(ctx):
    result = random.choice(["🪙 Heads!", "🪙 Tails!"])
    await ctx.send("🪙 Flipping the coin...")
    await ctx.send(f"🎲 **Result:** {result}")

@bot.command(aliases=["r"])
async def roll(ctx):
    result=random.choice(range(1,7))
    await ctx.send("Rolling the dice...")
    await ctx.send(f"🎲 You rolled a **{result}**!")

@bot.command()
async def tod(ctx):
    await ctx.send("Welcome to the Game! Would you like to pick 🟦 Truth or 🟥 Dare?\n ")

@bot.command()
async def truth(ctx):
   truth=[
"What's your most embarrassing moment?",
    "Have you ever had a secret crush on someone in this chat?",
    "What's your weirdest habit?",
    "Have you ever stolen something?",
    "What's something you’ve done that you still regret?",
    "What's the biggest mistake you've made in a relationship?",
    "Have you ever cheated on a test?",
    "What's the strangest dream you’ve had?",
    "What’s your guilty pleasure?",
    "What's your most childish habit?",
    "Have you ever lied to get out of trouble?",
    "What's your most irrational fear?",
    "Who was your first crush?",
    "What's a rumor you heard about yourself?",
    "Have you ever broken something and blamed someone else?",
    "What's a secret you've never told anyone?",
    "What’s the most awkward thing that ever happened to you?",
    "What's the last lie you told?",
    "Have you ever faked being sick to get out of something?",
    "What's your worst date experience?",
    "Have you ever ghosted someone?",
    "What’s the longest you've gone without showering?",
    "What’s the most childish thing you still do?",
    "Have you ever been rejected by someone you liked?",
    "What's your biggest insecurity?",
    "Have you ever read someone else’s messages without them knowing?",
    "Have you ever stalked someone's social media?",
    "What's the biggest secret you’ve kept from your parents?",
    "What's the most awkward message you've ever sent?",
    "Have you ever pretended to like something just to fit in?",
    "What’s your most embarrassing social media post?",
    "What’s something you’re really bad at but pretend you’re good at?",
    "What’s a silly thing you’re afraid of?",
    "What’s the last thing you searched on your phone?",
    "What was your last lie?",
    "What's a secret you found out and never told?",
    "What's a habit you're ashamed of?",
    "Have you ever lied in a truth or dare game?",
    "Have you ever pretended to like someone?",
    "What's a memory you wish you could erase?",
    "What’s a song you secretly love but would never admit?",
    "Have you ever tried to flirt and failed badly?",
    "What’s your most awkward crush story?",
    "What’s a strange talent you have?",
    "What’s something you’ve Googled that you're embarrassed about?",
    "Have you ever cried during a movie? Which one?",
    "What's a childish thing you still enjoy?",
    "What’s the meanest thing you’ve ever said to someone?",
    "What’s the most useless fact you know?",
       "Have you ever embarrassed yourself in public?",
       "Have you ever been jealous of a friend?",
       "Have you ever cheated in a game?",
       "What’s something you’re glad your parents don’t know?",
       "Have you ever had a crush on someone taken?",
       "What's a bad thing you did in school?",
       "Have you ever cried in public?",
       "What's your most embarrassing childhood memory?",
       "What’s a dream you’ve never told anyone?",
       "Have you ever been caught lying?",
       "Have you ever said “I love you” and didn’t mean it?",
       "What’s a rumor you started or helped spread?",
       "Have you ever laughed at the wrong moment?",
       "What’s your worst fashion choice ever?",
       "What’s something weird you believed as a kid?",
       "Have you ever lied to a friend to avoid hanging out?",
       "Have you ever ignored someone on purpose?",
       "What’s something you’d never admit in public?",
       "Have you ever secretly recorded someone?",
       "Have you ever lied in a job or school application?",
       "What’s your worst online chat experience?",
       "Have you ever kept a major secret from a friend?",
       "What’s your cringiest moment in school?",
       "What’s your weirdest crush?",
       "Have you ever pretended not to see someone to avoid talking?",
       "What’s the dumbest lie you’ve ever told?",
       "What’s something about yourself that people would never guess?"
       "If you could switch lives with one person for a day, who would it be?",
       "What’s a secret talent no one knows you have?",
       "Have you ever pretended to understand something when you didn’t?",
       "What’s the most childish thing you still enjoy doing?",
       "If you had to delete one app from your phone forever, which one would it be?",
       "What’s a bad habit you wish you could quit?",
       "What’s the weirdest thing you’ve ever eaten?",
       "What’s something you’ve done just to impress someone?",
       "Have you ever accidentally sent a text to the wrong person?",
       "What’s your biggest pet peeve about your friends?",
       "What’s something you wish you were better at?",
       "Have you ever gotten away with something you probably shouldn’t have?",
       "What’s the weirdest thing you believed as a child?",
       "If you could erase one memory, what would it be?",
       "What’s the worst lie you’ve ever told your parents?",
       "What’s the most embarrassing thing your parents have caught you doing?",
       "What’s a fashion trend you secretly love but are embarrassed to admit?",
       "If you had to live in a movie universe for a week, which would it be?",
       "What’s a song you blast when no one’s watching?",
       "What’s the strangest compliment you’ve ever received?",
       "Have you ever laughed so hard you cried at a totally inappropriate time?",
       "What’s a nickname you hate but everyone calls you anyway?",
       "What’s the last thing you searched for on your phone or computer?",
       "If you had to eat one food for the rest of your life, what would it be?",
       "What’s the worst haircut you’ve ever had?",
       "What’s a bad decision you look back on and laugh about now?",
       "Have you ever been caught talking to yourself?",
       "What’s the most embarrassing thing in your browser history?",
       "If you could only wear one outfit forever, what would it be?",
       "What’s the weirdest thing you’ve done when you were alone?",
       "What’s the most rebellious thing you’ve ever done?",
       "Have you ever pretended to be someone else online?",
       "What’s a secret talent no one knows about?",
       "If you could change one thing about your past, what would it be?",
       "Have you ever accidentally hurt someone’s feelings?",
       "What’s the weirdest thing you’ve ever eaten?",
       "Have you ever broken a promise?",
       "What’s the most embarrassing thing your parents have caught you doing?",
       "What’s a habit you want to quit but can’t?",
       "Have you ever kept a crush secret for a long time?",
       "What’s the biggest risk you’ve ever taken?",
       "What’s something you’ve done that you’d never admit to your best friend?",
       "What’s the worst advice you’ve ever followed?",
       "Have you ever gotten into trouble because of a dare?",
       "What’s a guilty pleasure you have that surprises people?",
       "Have you ever been caught doing something you shouldn’t?",
       "What’s something you wish you were better at?",
       "Have you ever said something about someone behind their back that you regret?",
       "What’s your biggest fear about the future?"
]
   result=random.choice(truth)
   await ctx.send(f"🟦 **Truth**:{result}")

@bot.command()
async def dare(ctx):
   dare=[
 "Send a funny GIF that describes your mood right now.",
    "Change your chat nickname to something silly for the next hour.",
    "Text the last person you messaged something random and weird.",
    "Send a message using only emojis for the next 5 messages.",
    "Write a short poem about someone in this chat.",
    "Send a voice note singing a song (without recording, type the lyrics).",
    "Send a funny or embarrassing story about yourself in the chat.",
    "Use an exaggerated compliment on the next person who messages.",
    "Pretend you’re a celebrity and introduce yourself in the chat.",
    "Type your messages with one finger only for the next 3 turns.",
    "Describe your dream vacation in 3 sentences.",
    "Send a screenshot of your current background (or describe it).",
    "Invent a new dance move and describe it in the chat.",
    "Tag someone and say something nice about them.",
    "Send a message pretending you’re a robot.",
    "Write a funny nickname for everyone in the chat.",
    "Describe your perfect pizza topping combo.",
    "Send a message using only capital letters for the next 2 turns.",
    "Share your weirdest food craving in the chat.",
    "Pretend you’re a detective and ask a mystery question.",
    "Send a joke and wait for everyone’s reactions.",
    "Make a short story using only three sentences.",
    "Send a message as if you just woke up from a nap.",
    "Describe how you’d survive a zombie apocalypse.",
    "Send a message using only one word per sentence for 5 messages.",
    "Type the alphabet backward as fast as you can (in chat).",
    "Send a funny nickname for the last person who messaged.",
    "Describe your weirdest dream you remember.",
    "Send a message acting like you just won a lottery.",
    "Share a weird fact you recently learned.",
    "Pretend you’re an alien visiting Earth and ask a question.",
    "Send a message saying you’re a secret agent on a mission."
    "Pretend you’re a chef and describe your signature dish in detail.",
       "Send a message pretending you’re stuck in an elevator.",
       "Make up a ridiculous excuse for being late to something.",
       "Describe your pet (real or imaginary) like a movie star.",
       "Send a message as if you’re an old-timey storyteller.",
       "Act like you just discovered a new planet and explain it.",
       "Type your next message like you’re speaking in rhymes.",
       "Pretend you’re a superhero and explain your powers.",
       "Describe how you’d survive a day without your phone.",
       "Send a message as if you’re a pirate looking for treasure.",
       "Invent a silly nickname for yourself and use it for 5 messages.",
       "Describe your favorite outfit as if it’s a magical costume.",
       "Send a message confessing you’re secretly a time traveler.",
       "Pretend you’re a spy sending a secret code in the chat.",
       "Type your next message like a dramatic soap opera character.",
       "Make up a funny story about how you met the last person who messaged.",
       "Send a message pretending you’re a talking animal.",
       "Describe your dream house, but it has to be completely weird.",
       "Send a message as if you’re narrating a nature documentary.",
       "Pretend you’re a DJ and announce your next big event.",
       "Type your next message like you just woke up from a long nap.",
       "Make up a funny commercial for a ridiculous product.",
       "Send a message acting like you’re lost in a maze.",
       "Pretend you’re a fortune teller and predict something funny.",
       "Describe your favorite food as if it’s a treasure from space.",
       "Send a message like you just won a bizarre contest.",
       "Type your next message as if you’re a robot learning human emotions.",
       "Pretend you’re a fashion designer and describe your latest creation.",
       "Send a message as if you’re a ghost trying to communicate.",
       "Make up a silly poem about the last person who messaged."
       "Describe your perfect day without using the letter 'e'.",
       "Send a message with a silly accent spelled out.",
       "Make up a funny conspiracy theory about something random.",
       "Send a message confessing a fake secret to the group.",
       "Type your next message as if you’re a pirate.",
       "Send a message using only questions for your next 3 turns.",
       "Describe your favorite movie plot in a funny way.",
       "Send a message like you’re a news reporter covering something boring.",
       "Describe how you’d spend a day if you were invisible.",
       "Send a message acting like you’re a movie director giving instructions.",
       "Pretend you’re a comedian and tell a short joke.",
       "Type your next message like you’re in a dramatic movie scene.",
       "Make up a funny rule for the group chat and enforce it for 3 messages.",
       "Send a message pretending you’re a famous explorer on a new mission.",
       "Describe your most embarrassing moment as a news headline.",
       "Pretend you’re an astronaut describing Earth to aliens.",
       "Send a message acting like you’re stuck in slow motion.",
       "Type your next message like you’re a secret agent on a mission."
]
   result=random.choice(dare)
   await ctx.send(f"**🟥Dare**:{result}")

@bot.command(aliases=["bal","b"])
async def balance(ctx):
    balance=get_formatted_balance(ctx.author.id)
    await ctx.send(f"🐾**|{ctx.author}**, you currently have **__{balance}__**🪙 billy bucks ")
@bot.command(aliases=["s"])
async def slots(ctx, amount: int):
    user_id = ctx.author.id
    balance = get_balance(user_id)

    if amount <= 0:
        await ctx.send(f"{ctx.author.mention} Please enter an amount greater than 0.")
        return

    if amount > balance:
        await ctx.send(f"{ctx.author.mention} Insufficient billy bucks to bet that amount!")
        return

    update_balance(user_id, -amount)
    weights = [73, 10, 10, 3, 2]
    rolls = random.choices(slotemojis, weights=weights, k=3)
    result = " | ".join(rolls)

    embed = discord.Embed(title="🎰 Slot Machine 🎰", color=discord.Color.gold())
    embed.add_field(name="Spinning...", value=result, inline=False)

    if rolls[0] == rolls[1] == rolls[2]:
        emoji = rolls[0]
        multipliers = {
            '🐾': 10,
            '🐀': 5,
            '💰': 2,
            '🧶': 5,
            '🐟': 3
        }
        multiplier = multipliers.get(emoji, 1)
        winnings = amount * multiplier
        update_balance(user_id, winnings)
        embed.description = (
            f"🎉 {ctx.author.mention}, you hit 3 {emoji} and won **{winnings}** billy bucks 🪙! 🎉\n"
        )
        embed.color = discord.Color.green()
    else:
        embed.description = (
            f"Better luck next time, {ctx.author.mention}!\n"
            f"You lost **{amount}** billy bucks.\n"
        )
        embed.color = discord.Color.red()

    await ctx.send(embed=embed)



@bot.command()
async def send(ctx, amount:int, member: discord.Member):
    sender_id = ctx.author.id
    receiver_id = member.id

    if amount <= 0:
        await ctx.send(f"{ctx.author.mention} Please enter an amount greater than 0.")
        return

    sender_balance = get_balance(sender_id)
    if amount > sender_balance:
        await ctx.send(f"{ctx.author.mention} You don't have enough billy bucks to send!")
        return

    # Deduct from sender
    update_balance(sender_id, -amount)
    # Add to receiver
    update_balance(receiver_id, amount)

    await ctx.send(
        f"💸 {ctx.author.mention} sent **{amount}**🪙 billy bucks to {member.mention}!\n"
    )

@bot.command()
async def scramble(ctx):
    word1 = random.choice(words1)
    scrambled = ''.join(random.sample(word1, len(word1)))
    while scrambled == word1:
        scrambled = ''.join(random.sample(word1, len(word1)))

    await ctx.send(
        f"**🔤 Word Scramble!**\nUnscramble this word: `{scrambled}`\n"
        "You have 3 tries. Please use `!your_guess` to make a guess!"
    )

    def check(m):
        return (
            m.author == ctx.author and
            m.channel == ctx.channel and
            m.content.startswith("!")
        )

    tries = 3
    while tries > 0:
        try:
            guess_msg = await bot.wait_for('message', check=check, timeout=60)
            guess = guess_msg.content[1:]

            if guess.lower() == word1.lower():
                await ctx.send(f"🎉 Correct! Well done, {ctx.author.mention}!")
                return
            else:
                tries -= 1
                if tries > 0:
                    await ctx.send(f"❌ Nope! {tries} tries left.")
                else:
                    await ctx.send(f"❌ Out of tries! The word was `{word1.title()}`.")
        except asyncio.TimeoutError:
            await ctx.send(f"⌛ Time's up! The word was `{word1.title()}`.")
            return



webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)