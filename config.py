"""Configuration constants for Billy Discord Bot"""

# Bot Configuration
STARTING_BALANCE = 1000
HANGMAN_ATTEMPTS = 4
SLOTS_COOLDOWN = 5.0
SCRAMBLE_TIMEOUT = 60
SCRAMBLE_TRIES = 3

# Slot Machine Configuration
SLOT_MULTIPLIERS = {
    '🐾': 10,
    '🐀': 5,
    '🧶': 5,
    '🐟': 3,
    '💰': 2
}

SLOT_EMOJIS = ['💰', '🧶', '🐀', '🐟', '🐾']
SLOT_WEIGHTS = [73, 10, 10, 3, 2]

# File paths
CURRENCY_FILE = "currency.json"
WORDS_FILE = "words.txt"
COMMON_WORDS_FILE = "common_words.txt"
LOG_FILE = "discord.log"

# Logging Configuration
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 5
