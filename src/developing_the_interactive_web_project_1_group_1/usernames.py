import random
from developing_the_interactive_web_project_1_group_1 import database

ADJECTIVES = [
    "Amber", "Ancient", "Autumn", "Bold", "Brave", "Breezy", "Bright", "Brisk",
    "Bubbly", "Calm", "Candid", "Cheerful", "Chilly", "Clever", "Cloudy", "Cobalt",
    "Cosmic", "Cozy", "Crimson", "Crisp", "Crystal", "Curious", "Daring", "Dapper",
    "Dashing", "Dusty", "Eager", "Electric", "Fancy", "Fearless", "Fluffy", "Friendly",
    "Frosty", "Fuzzy", "Gentle", "Giant", "Glowing", "Golden", "Graceful", "Grand",
    "Happy", "Hidden", "Honest", "Humble", "Icy", "Jazzy", "Jolly", "Kind",
    "Lively", "Lucky", "Lunar", "Magic", "Mellow", "Merry", "Mighty", "Misty",
    "Modern", "Mossy", "Nimble", "Noble", "Patient", "Peaceful", "Playful", "Polite",
    "Proud", "Quick", "Quiet", "Rapid", "Rosy", "Rustic", "Scarlet", "Shiny",
    "Silent", "Silver", "Simple", "Sleepy", "Smooth", "Snowy", "Solar", "Sparkly",
    "Speedy", "Steady", "Stormy", "Sturdy", "Sunny", "Swift", "Teal", "Tidy",
    "Tiny", "Tranquil", "Trusty", "Velvet", "Vivid", "Wandering", "Warm", "Whimsical",
    "Windy", "Wise", "Witty", "Zesty",
]

NOUNS = [
    "Acorn", "Anchor", "Badger", "Bagel", "Basil", "Beacon", "Bison", "Blossom",
    "Breeze", "Brook", "Button", "Cactus", "Canoe", "Canyon", "Cedar", "Comet",
    "Compass", "Cookie", "Coral", "Cricket", "Daisy", "Dolphin", "Dragon", "Falcon",
    "Feather", "Fern", "Firefly", "Fox", "Gecko", "Glacier", "Gopher", "Harbor",
    "Hawk", "Hedgehog", "Heron", "Island", "Jaguar", "Kettle", "Kite", "Koala",
    "Lamp", "Lantern", "Lemon", "Lighthouse", "Llama", "Lobster", "Log", "Loon",
    "Lynx", "Maple", "Marble", "Meadow", "Meteor", "Mitten", "Moose", "Moth",
    "Mountain", "Narwhal", "Nebula", "Oak", "Ocean", "Octopus", "Orchid", "Otter",
    "Owl", "Panda", "Parrot", "Pebble", "Pelican", "Penguin", "Pepper", "Pinecone",
    "Planet", "Pretzel", "Puffin", "Quokka", "Rabbit", "Raccoon", "Raven", "River",
    "Robin", "Rocket", "Saturn", "Seal", "Sparrow", "Sprout", "Squirrel", "Star",
    "Sunflower", "Teapot", "Thunder", "Tiger", "Toaster", "Tortoise", "Tulip", "Turtle",
    "Volcano", "Waffle", "Walrus", "Whale", "Willow", "Wombat", "Yeti", "Zebra",
]

def random_username():
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"

def unique_username():
    name = random_username()
    while database.display_name_taken(name):
        name = random_username()
    return name
