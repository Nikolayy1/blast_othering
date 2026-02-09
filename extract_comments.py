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

othering_terms_de = [
    # Dehumanizing terms (animals, pests, disease metaphors)
    "tier",
    "bestie",
    "wild",
    "barbarisch",
    "unmensch",
    "untermensch",
    "primitiv",
    "parasit",
    "parasiten",
    "ungeziefer",
    "ratte",
    "kakerlake",
    "ungeheuer",
    "monster",
    "brut",
    "affe",
    "gorilla",
    "hund",
    "schwein",
    "sau",
    "ziege",
    "insekt",
    "egel",
    "zecke",
    "laus",
    "maden",
    "wurm",
    "krebs",
    "tumor",
    "virus",
    "pest",
    "seuche",
    "infektion",

    # Moral judgment / worthlessness
    "abschaum",
    "müll",
    "dreck",
    "wertlos",
    "minderwertig",
    "degeneriert",
    "asozial",
    "gesindel",
    "unwürdig",
    "unrein",
    "verdorben",
    "schmutzig",
    "ekelhaft",
    "widerlich",
    "verachtenswert",
    "böse",
    "verkommen",
    "sündig",
    "verflucht",
    "last",
    "schmarotzer",
    "parasitär",
    "sozialschmarotzer",

    # Threatening / dangerous
    "gefährlich",
    "gewalttätig",
    "aggressiv",
    "feindselig",
    "kriminell",
    "verbrecher",
    "gangster",
    "schläger",
    "abartig",
    "radikal",
    "extremist",
    "fundamentalist",
    "terrorist",
    "raubtier",
    "vergewaltiger",
    "invasor",
    "eindringling",
    "besatzer",
    "unterwanderer",
    "bedrohung",

    # Exclusion / separation
    "außenseiter",
    "fremdkörper",
    "eindringling",
    "alien",
    "fremder",
    "ausländer",
    "feind",
    "unerwünscht",
    "illegal",
    "illegale",
    "abschieben",
    "abschiebung",
    "ausgestoßener",
    "unerwünschte",
    "kolonialist",
    "siedler",

    # Diminishing / infantilizing
    "ignorant",
    "rückständig",
    "naiv",
    "unzivilisiert",
    "hilflos",
    "schwach",
    "dumm",
    "faul",
    "unreif",
    "kindisch",
    "lächerlich",
    "überemotional",
    "hysterisch",
    "irrational",
    "ahnungslos",
    "hirngewaschen",
    "schaf",
    "mitläufer",
    "marionette",

    # Religion & secular identities
    "atheisten",
    "ungläubige",
    "gottlose",
    "säkularisten",
    "buddhisten",
    "hindus",
    "christen",
    "christlich",
    "katholiken",
    "protestanten",
    "evangelikale",
    "mormonen",
    "heidnische",
    "satanisten",
    "muslime",
    "islamisch",
    "islamisten",
    "juden",
    "jüdisch",
    "zionisten",
    "orthodoxe juden",

    # Migration / nationality
    "migranten",
    "immigranten",
    "ausländer",
    "fremde",
    "flüchtlinge",
    "asylbewerber",
    "asylanten",
    "expats",
    "einheimische",
    "illegale einwanderer",
    "invasoren",
    "kolonisatoren",
    "siedler",

    # Gender & women
    "frauen",
    "frau",
    "mädchen",
    "weibchen",
    "damen",
    "ehefrauen",
    "mütter",
    "schlampen",
    "nutten",
    "huren",
    "fotzen",
    "zicken",
    "feministinnen",
    "feminazis",

    # LGBTQ+
    "lgbt",
    "schwul",
    "schwule",
    "lesbisch",
    "lesben",
    "bisexuell",
    "transgender",
    "trans",
    "transe",
    "queer",
    "tunte",
    "schwuchtel",
    "nichtbinär",
    "dragqueen",
    "dragking",
]


# Split into single-word vs multi-word ENGLISH
single_terms = [t for t in othering_terms if " " not in t]
multi_terms = [t for t in othering_terms if " " in t]

# Split into single-word vs multi-word GERMAN
single_terms_de = [t for t in othering_terms if " " not in t]
multi_terms_de = [t for t in othering_terms_de if " " in t]

# Regex for single-word terms
single_patterns = [
    re.compile(rf"(?i)(?<!\w){re.escape(t)}(?!\w)") for t in single_terms
]

# Regex for single-word terms GERMAN
single_patterns_de = [
    re.compile(rf"(?i)(?<!\w){re.escape(t)}(?!\w)") for t in single_terms_de
]

#input_path = "/pl/active/blast-data/corpora/reddit/subreddits24/changemyview_comments.zst"
#output_path = "full_comments/changemyview.jsonl"

input_path = "/pl/active/blast-data/corpora/reddit/subreddits24/DePi_comments.zst"
output_path = "full_comments/DePi_comments.jsonl"

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
                    any(term in body for term in multi_terms_de)
                    or any(p.search(body) for p in single_patterns_de)
                ):
                    continue

                # --- token limit ---
                token_count = len(body.split())
                if token_count > 100:
                    continue

                # --- save match ---
                matches += 1
                out.write(json.dumps(obj) + "\n")
