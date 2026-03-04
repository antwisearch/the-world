"""
Name Generator - Dwarf Fortress style names
"""

import random

FIRST_NAMES = [
    "Bogrin", "Krag", "Urist", "Thorin", "Balin", "Dwalin", "Gimor", "Dain",
    "Frerin", "Dis", "Nori", "Dori", "Ori", "Bifur", "Bofur", "Bombur",
    "Glor", "Lind", "Celon", "Nar", "Beleg", "Mith", "Huan", "Luth",
    "Thran", "Grar", "Kron", "Dorn", "Thrain", "Gimlet", "Brim",
    "Ston", "Grim", "Durin", "Mardin", "Rurik", "Thork", "Grimm",
    "Dorin", "Balor", "Gurdis", "Helga", "Astrid", "Ingrid", "Brunhild",
    "Ragnhild", "Sigrid", "Thyra", "Gudrun", "Solveig", "Eira", "Nanna"
]

LAST_NAMES = [
    "Stonefoot", "Ironhand", "Deepdelve", "Stormhammer", "Firebeard",
    "Goldvein", "Coalminer", "Stonegrip", "Anvilborn", "Hammerfall",
    "Broadbelt", "Longbeard", "Battlehammer", "Doomforge", "Starwatch",
    "Darkmine", "Earthshaker", "Thundersmith", "Flameheart", "Frostbeard",
    "the Quick", "the Bold", "the Wise", "the Strong", "the Silent",
    "of the Mountain", "of the Deep", "of the Forge", "of the Stone",
    "Stonebreaker", "Ironblood", "Coalheart", "Goldsinger", "Diamondseeker"
]

MIDDLE_NAMES = [
    "son", "daughter", " Mc", "von", "ap"
]

def generate_name(gender=None):
    """Generate a Dwarf Fortress style name"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    
    # 30% chance of middle name
    if random.random() < 0.3:
        middle = random.choice(MIDDLE_NAMES)
        if middle in ["son", "daughter"]:
            return f"{first} {middle} {last}"
        else:
            return f"{first}{middle} {last}"
    
    return f"{first} {last}"

def generate_full_name():
    """Generate name with nickname possibility"""
    name = generate_name()
    
    # 20% chance to have a nickname
    if random.random() < 0.2:
        nicknames = [
            "the Flies-I-Do-Not-Know", "the Confused", "the Drunk",
            "the Brave", "the Coward", "the Great", "the Terrible",
            "the Lucky", "the Unlucky", "of Many Children",
            "Slayer-of-Goblins", "Finder-of-Gems", "Breaker-of-Chains"
        ]
        name += f" {random.choice(nicknames)}"
    
    return name
