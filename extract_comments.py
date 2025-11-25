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

# Split into single-word vs multi-word
single_terms = [t for t in othering_terms if " " not in t]
multi_terms = [t for t in othering_terms if " " in t]

# Regex for single-word terms
single_patterns = [
    re.compile(rf"(?i)(?<!\w){re.escape(t)}(?!\w)") for t in single_terms
]

input_path = "/pl/active/blast-data/corpora/reddit/subreddits24/changemyview_comments.zst"
output_path = "full_comments/changemyview.jsonl"

counter = 0
matches = 0

with open(input_path, "rb") as fh, open(output_path, "w") as out:
    dctx = zstd.ZstdDecompressor(max_window_size=2**31)

    with dctx.stream_reader(fh) as reader:
        buffer = b""

        while True:
            chunk = reader.read(2**20)  # 1MB
            if not chunk:
                break

            buffer += chunk
            lines = buffer.split(b"\n")
            buffer = lines.pop()

            for raw_line in lines:
                counter += 1

                if counter % 500000 == 0:
                    print(
                        f"Processed {counter:,} comments; matches so far: {matches:,}"
                    )

                try:
                    line = raw_line.decode("utf-8", errors="ignore")
                except:
                    continue

                # --- parse JSON FIRST ---
                try:
                    obj = json.loads(line)
                except:
                    continue

                body = obj.get("body", "").lower()

                # Skip deleted/removed
                if body in ("[deleted]", "[removed]"):
                    continue

                # --- apply matching ONLY on comment body ---
                if not (
                    any(term in body for term in multi_terms)
                    or any(p.search(body) for p in single_patterns)
                ):
                    continue

                # --- token limit ---
                token_count = len(body.split())
                if token_count > 100:
                    continue

                # --- save match ---
                matches += 1
                out.write(json.dumps(obj) + "\n")
