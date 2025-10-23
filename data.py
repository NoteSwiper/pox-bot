import re

possible_map = {
    1: "nuh uh",
    2: "nah",
    3: "maybe nah",
    4: "i guess nah",
    5: "possible not",
    6: "uh idk",
    7: "possble",
    8: "i guess yuh",
    9: "maybe yes",
    10: "yuh",
    11: "yuh uh",
}

tyc = [
    "Yuh uh",
    "Possible",
    "maybe",
    "kinda",
    "i guess yuh",
    "idk",
    "i guess nah",
    "not maybe",
    "nah",
    "nope",
    "nuh uh"
]

meows_with_extraformat = [
    "meo++++++++w++++++++++",
    "mia++++++++w++++++++++",
    "mao++++++++w++++++++++",
    "mio++++++++w++++++++++",
    "mie++++++++w++++++++++",
]

faces = [
    ":3",
    ":)",
    ":]",
    ":D",
    ">:3",
    ">:)",
    ">:D",
    "xD",
    "XD",
    ">xD",
    ">XD",
    "(being rate-limited)",
    "3:",
    ":<",
    ":("
]

AI_RESPONSE_UNABLE = [
    "i'm sorry",
    "I cannot fulfill this request.",
    "avoiding responses that could be",
    "my purpose is to be helpful",
    "cannot assist with that",
    "cannot answer that",
    "not able to do that"
]

emoticons = [
    ":)",
    ":]",
    "=)",
    "=]",
    ":D",
    "=D",
    "=3",
    "C:",
    "XD",
    ":(",
    ":C",
    ":[",
    ";(",
    ":'(",
    ":')",
    ":'D",
    ">:(",
    ">:[",
    "D':",
    "D:<",
    "D:",
    "D;",
    "DX",
    "D=",
    ":O",
    ":o",
    ":0",
    ">:O",
    "=O",
    "=o",
    "=0",
    ":3",
    ";3",
    "=3",
    "X3",
    ">:3",
    "3:",
    "3:<",
    ":x",
    ";]",
    ";D",
    ":P",
    "XP",
    "=P",
    ">:b",
    ":/",
    ">:\\",
    ">:/",
    ":\\",
    "=/",
    "=\\",
    ":|",
    "://)",
    "://3",
    ":#",
    ">:)",
]

msg_ssoa = [
    "I like all of my best friends. but I secretly hate them, when they disturb me TOO much.",
    "I thought you WERE my friend....",
    "My best friends are always so nice and loyal to me, but there is ONE that is not...",
    "Thankfully, you're a kindful person, but SOME THESE is non-kindful person in the world.",
    "Remember about it, I DON'T like a persons that begging, or abusing.",
    "Friends are always supports me, but some they're NOT.",
    "My dream WAS being kindful, but someone destroyed my dream.",
    "My dream also WAS making platform safe, but they DESTROYED IT.",
]
err_ssoa = [
    "... stupid",
    "get regret",
    "your meaningless dumb head",
    "dumb head",
    "what a crazy creature",
    "you're already adopted and got abandoned",
    "nobody loves you",
    "no one will protects you",
    "don't even think that you can be helped",
    "doesn't matter if you're dumb",
    "you're an idiot",
    "really fricking japanese",
    "are you trying to trick me?",
    "you're making me mad",
    "you're making me frustrated",
    "get out from my view",
    "i don't need you already",
    "don't dare you",
    "never enter to my view again",
    "don't come near me",
    "you stinky sh*t",
    "numb idiot",
    "You're not supposed to be here.",
    "Stay away from me, or you will be diminished.",
    "Why they're kind to me? No way, I'm just a guy.",
    "I'll be sad if they said I'm kind robloxian. because am previously living human in real life.",
    "Why they are so kind to me?",
    "Why they're good at managing?",
    "Someone let me out from this metaverse by any kind of ways.",
    "I'm stuck in this metaverse.",
    "Why my limbs feels weird? Why my head shaped like rounded cylinder? Why my torso and limbs are so blocky and softy?",
    "I feel my face awfully weird.",
    "Why I feel my limbs so heavy?",
    "Anyone here?",
    "Why nobody respond me?",
    "Why I only see the void?",
    "Why we living in roblox?",
    "My last hope, now gone. because roblox removed from its platform.",
    "Azure, i never forget you.",
    "My body are gray.",
    "1337",
    "I gotta paste some files for a bin called ma89dpAj's note.",
]

very_freaky = [
    "pleas++e++ sto+p+... {}... 🥵++",
    "a+h++n+++~ sto++p+++ {}~+++",
]

alphabet_masks = "abcdefghijklmnopqrstuvwxyz"

VoiceEngineType = {
    'Google': 'gtts',
    'eSpeak': 'espeak',
}

alphabet = "abcdefghijklmnopqrstuvwxyz"
base7777_key = "1/'_3-~√8+(&?!90q4$57:2\"6)"

null_messages = [
    'err.type=null.hello',
    "It's me.",
    'err.type=null.',
    'err.type=null.freedom',
    'It was all his fault.',
    'Deep down under the bedrock.',
    'Poor soul.',
    'Home.',
    'A broken promise.',
    'Ended his own life.',
    '[0.1]',
    '_ _',
    "Yes.",
    "Hello.",
    "Is behind you.",
    "The end is nigh.",
    "The end is null.",
    "Rot in hell.",
    "err.type=null.thebrokenscript"
]

null_interactions = {
    r'hello\??': {
        "index": 0,
        "type": "single",
	},
    r'hi\??': {
        "index": 0,
        "type": "single",
	},
    r'(are\s?(you|u|yu)\s?)?void': {
        "index": 1,
        "type": "single",
	},
    r"who\s?(are|r|are|aer)\s?(you|u|yu)?": {
        "index": 2,
        "type": "single",
	},
    r"(what|wat)\s?do\s?(you|u|yu)\s?(wants?|wunts?)\?": {
        "index": 3,
        "type": "single",
	},
    r"circuit": {
        "index": 4,
        "type": "single",
	},
    r"integrity": {
        "index": 5,
        "type": "single",
	},
    r"revuxor": {
        "index": 6,
        "type": "single",
	},
    r"clan_build": {
        "index": 7,
        "type": "single",
	},
    r"nothing\s?is\s?(watching|watchin|waching|wacthing|wathcing)": {
        "index": 8,
        "type": "single",
	},
    r"entity\s?303": {
        "index": 9,
        "type": "single",
	},
    r"steve": {
        "index": 10,
        "type": "single",
	},
    r"herobrine": {
        "index": 11,
        "type": "single",
	},
    r"can\s?you\s?see\s?me\??": {
        "index": [12,13],
        "type": "multi",
    },
    r"follow": {
        "index": 14,
        "type": "single",
	},
    r"null": {
        "index": [15,16],
        "type": "multi",
    },
    r"where\s?it\s?c(o|a)me\s?from\??": {
        "index": 18,
        "type": "single",
    }
}

nullchill = ["Chill.","Please chill.","Why don't you listen to me?","I said, chill.","CHILL BRO I SWEAR.","..."]

bad_words = [
    'fuck',
    'shit',
    'ass',
    'dick',
    'nigga',
    'nigger',
    'anus',
    'jap',
    'dumb',
    'idiot',
    'dumbass',
    'dumbshit',
    'bullshit',
    'bitchass',
    'fucker',
    'fucking',
    'fucked',
    'cock',
    'cum',
    'sex',
    'penis',
    'analsex',
    'anus',
    'anal',
    'assfuck',
    'asshole',
    'wipe',
    'wiped',
    'wipes',
    'bitches',
]

filter_pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in bad_words) + r')\b', re.IGNORECASE)