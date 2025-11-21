import json
import re
import zstandard as zstd

othering_terms = [
    # Dehumanizing terms (animals, pests, disease metaphors)
    "animal",
    "beast",
    "savage",
    "barbaric",
    "subhuman",
    "primitive",
    "parasite",
    "vermin",
    "rat",
    "cockroach",
    "monster",
    "brute",
    "ape",
    "gorilla",
    "monkey",
    "dog",
    "pig",
    "swine",
    "goat",
    "bug",
    "leech",
    "tick",
    "lice",
    "maggot",
    "worm",
    "cancer",
    "tumor",
    "virus",
    "plague",
    "infection",
    "disease",
    # Moral judgment / worthlessness
    "scum",
    "trash",
    "filth",
    "worthless",
    "inferior",
    "degenerate",
    "lowlife",
    "unworthy",
    "unclean",
    "impure",
    "corrupt",
    "dirty",
    "disgusting",
    "vile",
    "evil",
    "wicked",
    "sinful",
    "cursed",
    "burden",
    "freeloader",
    "sponger",
    # Threatening / dangerous
    "dangerous",
    "violent",
    "aggressive",
    "hostile",
    "criminal",
    "thug",
    "deviant",
    "radical",
    "extremist",
    "fundamentalist",
    "terrorist",
    "predator",
    "rapist",
    "gangster",
    "invader",
    "occupier",
    "conqueror",
    "infiltrator",
    "threat",
    # Exclusion / separation
    "outsider",
    "intruder",
    "alien",
    "stranger",
    "foreigner",
    "enemy",
    "unwelcome",
    "illegal",
    "unwanted",
    "expat",
    "outcast",
    "undesirable",
    "colonizer",
    "settler",
    # Diminishing / infantilizing
    "ignorant",
    "backward",
    "naive",
    "uncivilized",
    "helpless",
    "weak",
    "stupid",
    "lazy",
    "immature",
    "childlike",
    "silly",
    "emotional",
    "hysterical",
    "irrational",
    "clueless",
    "brainwashed",
    "sheep",
    "puppet",
    "follower",
    # Religion & secular identities
    "atheists",
    "non-believers",
    "secular people",
    "buddhists",
    "buddhist people",
    "hindus",
    "hindu people",
    "christians",
    "christian people",
    "catholics",
    "protestants",
    "mormons",
    "evangelicals",
    "pagans",
    "satanists",
    "muslims",
    "islamic people",
    "islamists",
    "muzzies",
    "ragheads",
    "jews",
    "jewish people",
    "zionists",
    "orthodox jews",
    # Migration / nationality
    "immigrants",
    "migrants",
    "foreigners",
    "outsiders",
    "refugees",
    "asylum seekers",
    "expats",
    "nationals",
    "illegal aliens",
    "illegals",
    "invaders",
    "colonizers",
    "settlers",
    # Gender & women
    "women",
    "woman",
    "girl",
    "girls",
    "females",
    "ladies",
    "wives",
    "mothers",
    "bitches",
    "sluts",
    "whores",
    "feminists",
    "feminazis",
    # LGBTQ+
    "lgbtq",
    "gay",
    "gays",
    "lesbian",
    "lesbians",
    "bisexual",
    "transgender",
    "trans",
    "tranny",
    "trannies",
    "queer",
    "queers",
    "dyke",
    "dykes",
    "faggot",
    "faggots",
    "non-binary",
    "drag queens",
    "drag kings",
]

# split terms into single-word and multi-word
single_terms = [t for t in othering_terms if " " not in t]
multi_terms = [t for t in othering_terms if " " in t]

# compile regex for single words
single_patterns = [
    re.compile(rf"(?i)(?<!\w){re.escape(t)}(?!\w)") for t in single_terms
]

input_path = "/pl/active/blast-data/corpora/reddit/comments/RC_2023-03.zst"
output_path = "full_comments/RC_2023-03_results.jsonl"

with open(input_path, "rb") as fh, open(output_path, "w") as out:
    dctx = zstd.ZstdDecompressor(max_window_size=2**31)
    with dctx.stream_reader(fh) as reader:
        for raw_line in reader:
            # decode
            try:
                line = raw_line.decode("utf-8", errors="ignore")
            except:
                continue

            text = line.lower()

            # fast substring check for multi-word phrases
            if any(term in text for term in multi_terms):
                pass
            # fallback to regex for single words
            elif not any(p.search(text) for p in single_patterns):
                continue

            # parse json
            try:
                obj = json.loads(text)
            except:
                continue

            # write output
            out.write(json.dumps(obj) + "\n")
