import re
from convokit import Corpus, download
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# Method definitions
def load_dataset_dynamic(corpus, start_index, end_index):
    return Corpus(
        filename=download(corpus),
        backend="mem",
        utterance_start_index=start_index,
        utterance_end_index=end_index
    )

def load_dataset_to_memory(corpus_path):
    return Corpus(
        filename=corpus_path,
        backend="mem"
    )

def get_target_ids(corpus):
    target_ids = []
    
    othering_terms = [
        # Dehumanizing terms (animals, pests, disease metaphors)
        "animal", "beast", "savage", "barbaric", "subhuman", "primitive",
        "parasite", "vermin", "rat", "cockroach", "monster", "brute",
        "ape", "gorilla", "monkey", "dog", "pig", "swine", "goat",
        "bug", "leech", "tick", "lice", "maggot", "worm",
        "cancer", "tumor", "virus", "plague", "infection", "disease",

        # Moral judgment / worthlessness
        "scum", "trash", "filth", "worthless", "inferior", "degenerate",
        "lowlife", "unworthy", "unclean", "impure", "corrupt", "dirty",
        "disgusting", "vile", "evil", "wicked", "sinful", "cursed",
        "burden", "freeloader", "sponger",

        # Threatening / dangerous
        "dangerous", "violent", "aggressive", "hostile", "criminal", "thug",
        "deviant", "radical", "extremist", "fundamentalist", "terrorist",
        "predator", "rapist", "gangster", "invader", "occupier", "conqueror",
        "infiltrator", "threat",

        # Exclusion / separation
        "outsider", "intruder", "alien", "stranger", "foreigner", "enemy",
        "unwelcome", "illegal", "unwanted", "expat", "outcast", "undesirable",
        "colonizer", "settler",

        # Diminishing / infantilizing
        "ignorant", "backward", "naive", "uncivilized", "helpless",
        "weak", "stupid", "lazy", "immature", "childlike", "silly",
        "emotional", "hysterical", "irrational", "clueless",
        "brainwashed", "sheep", "puppet", "follower",

        # Religion & secular identities
        "atheists", "non-believers", "secular people",
        "buddhists", "buddhist people",
        "hindus", "hindu people",
        "christians", "christian people", "catholics", "protestants",
        "mormons", "evangelicals", "pagans", "satanists",
        "muslims", "islamic people", "islamists", "muzzies", "ragheads",
        "jews", "jewish people", "zionists", "orthodox jews",

        # Migration / nationality
        "immigrants", "migrants", "foreigners", "outsiders", "refugees",
        "asylum seekers", "expats", "nationals", "illegal aliens", "illegals",
        "invaders", "colonizers", "settlers",

        # Gender & women
        "women", "woman", "girl", "girls", "females", "ladies", "wives", "mothers",
        "bitches", "sluts", "whores", "feminists", "feminazis",

        # LGBTQ+
        "lgbtq", "gay", "gays", "lesbian", "lesbians",
        "bisexual", "transgender", "trans", "tranny", "trannies",
        "queer", "queers", "dyke", "dykes", "faggot", "faggots",
        "non-binary", "drag queens", "drag kings"
    ]
    
    # Pre-compile regex patterns
    patterns = [
        re.compile(r"(?i)(?<!\w)" + re.escape(term) + r"(?!\w)")
        for term in othering_terms
    ]

    for utt in corpus.iter_utterances():
        if any(p.search(utt.text) for p in patterns):
            target_ids.append(utt.id)

    return target_ids

    
def get_id_chain(corpus, target_id):
    chain = []
    utt = corpus.get_utterance(target_id)
    while utt is not None:
        chain.append(utt)
        utt = corpus.get_utterance(utt.reply_to) if utt.reply_to else None

    # reverse so it's from root → target
    chain = chain[::-1]
    return chain

def plot_wordcloud(chain, title):
    all_words = " ".join(u.text for u in chain).lower()
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=STOPWORDS).generate(all_words)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.show()
    
def export_comments_to_json(corpus, target_ids, filepath):
    results = []
    
    for target_id in target_ids:
        id_chain = get_id_chain(corpus, target_id)
        record = {
            "id": target_id.id,
            "text": utt.text,
            "timestamp": getattr(utt, "timestamp", None),
            "conversation_id": getattr(utt, "conversation_id", None),
            "comment_chain": chain
        }
        results.append(record)
            
if __name__ == "__main__":
    corpus = load_dataset_dynamic("reddit-corpus-small", 200, 1000)
    target_ids = get_target_ids(corpus)

    for target_id in target_ids:
        chain = get_id_chain(corpus, target_id)
        for u in chain:
            print(f"{u.id}")
        print("-----")

    print(target_ids)
    
    print(plot_wordcloud(get_id_chain(corpus, "e6x0yb0"), f"Conversation Chain for Target ID {'e6x0yb0'}"))
    print(corpus.get_utterance("9k4nb6"))
    print(corpus.get_conversation("9k4nb6"))

