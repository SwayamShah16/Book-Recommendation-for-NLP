import sys, re, json
from pathlib import Path
from collections import Counter
import streamlit as st
import pandas as pd

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from src.preprocessing import tokenize, filter_tokens, validate_script, stopword_stem_lemma, morphology
from src.experiment_tools import build_ngram_model, predict_next_word, generate_text, compare_texts

st.set_page_config(page_title='BookWise — Read your next favorite', page_icon='📚', layout='wide', initial_sidebar_state='expanded', menu_items={})

BOOKS = [
 {'id':1,'title':'The Midnight Library','author':'Matt Haig','genre':'Fantasy','year':2020,'rating':4.4,'pages':304,'description':'Between life and death there is a library, and within that library, the shelves go on forever. Every book offers a chance to try another life you could have lived.','tagline':'One library. Infinite lives.','color':'#5267A8','emoji':'🌙'},
 {'id':2,'title':'Atomic Habits','author':'James Clear','genre':'Self-help','year':2018,'rating':4.7,'pages':320,'description':'A practical guide to building good habits, breaking bad ones, and making small changes that compound into remarkable results.','tagline':'Tiny changes, remarkable results.','color':'#D8A34D','emoji':'⚡'},
 {'id':3,'title':'The Silent Patient','author':'Alex Michaelides','genre':'Thriller','year':2019,'rating':4.2,'pages':336,'description':'A famous painter shoots her husband and never speaks another word. A criminal psychotherapist becomes obsessed with uncovering her silence.','tagline':'A shocking psychological mystery.','color':'#426C68','emoji':'🗝️'},
 {'id':4,'title':'Educated','author':'Tara Westover','genre':'Memoir','year':2018,'rating':4.5,'pages':352,'description':'Born to survivalists in the mountains of Idaho, a young woman transforms herself through education and discovers the world beyond her family.','tagline':'A memoir of transformation.','color':'#A87963','emoji':'🎓'},
 {'id':5,'title':'Dune','author':'Frank Herbert','genre':'Science Fiction','year':1965,'rating':4.3,'pages':688,'description':'On the desert planet Arrakis, political intrigue, ecology, prophecy, and the struggle for a precious resource shape the fate of an empire.','tagline':'Fear is the mind-killer.','color':'#B8783D','emoji':'🏜️'},
 {'id':6,'title':'The Alchemist','author':'Paulo Coelho','genre':'Fiction','year':1988,'rating':4.1,'pages':208,'description':'A young Andalusian shepherd travels from Spain to the Egyptian desert in search of treasure and learns to listen to his heart.','tagline':'Follow your personal legend.','color':'#C79A46','emoji':'✨'},
 {'id':7,'title':'Sapiens','author':'Yuval Noah Harari','genre':'History','year':2011,'rating':4.4,'pages':464,'description':'A sweeping exploration of humankind, from early humans to modern societies, examining how shared stories shaped our world.','tagline':'A brief history of humankind.','color':'#8B5E70','emoji':'🌍'},
 {'id':8,'title':'Pride and Prejudice','author':'Jane Austen','genre':'Romance','year':1813,'rating':4.5,'pages':432,'description':'Elizabeth Bennet navigates manners, family, class, and first impressions as she encounters the proud and enigmatic Mr Darcy.','tagline':'First impressions can deceive.','color':'#B45F76','emoji':'🌹'},
 {'id':9,'title':'Project Hail Mary','author':'Andy Weir','genre':'Science Fiction','year':2021,'rating':4.6,'pages':496,'description':'A lone astronaut wakes up far from Earth with no memory and must use science, ingenuity, and an unexpected friendship to save humanity.','tagline':'A mission with everything at stake.','color':'#3C83A6','emoji':'🚀'},
 {'id':10,'title':'Thinking, Fast and Slow','author':'Daniel Kahneman','genre':'Psychology','year':2011,'rating':4.2,'pages':512,'description':'A Nobel laureate explains the two systems that drive human thought and how biases influence decisions, judgement, and everyday life.','tagline':'Understand how you think.','color':'#557C70','emoji':'🧠'},
 {'id':11,'title':'A Good Girl’s Guide to Murder','author':'Holly Jackson','genre':'Mystery','year':2019,'rating':4.3,'pages':400,'description':'A student reopens a closed murder case for a school project and discovers that the truth is much closer and more dangerous than expected.','tagline':'Who really did it?','color':'#547A55','emoji':'🔎'},
 {'id':12,'title':'Deep Work','author':'Cal Newport','genre':'Productivity','year':2016,'rating':4.3,'pages':296,'description':'Rules and strategies for cultivating intense focus, reducing distraction, and producing valuable work in a world full of interruptions.','tagline':'Rules for focused success.','color':'#4E6487','emoji':'🎯'},
 {'id':13,'title':'The Hobbit','author':'J.R.R. Tolkien','genre':'Fantasy','year':1937,'rating':4.6,'pages':310,'description':'Bilbo Baggins leaves a quiet home for a dangerous adventure with dwarves, a dragon, riddles, and unexpected courage.','tagline':'There and back again.','color':'#65834D','emoji':'🍃'},
 {'id':14,'title':'It Ends with Us','author':'Colleen Hoover','genre':'Romance','year':2016,'rating':4.0,'pages':376,'description':'A young woman building a new life confronts difficult patterns from her past while navigating love, family, and difficult choices.','tagline':'Sometimes the hardest choice is the right one.','color':'#B96D78','emoji':'🌸'},
 {'id':15,'title':'The Psychology of Money','author':'Morgan Housel','genre':'Finance','year':2020,'rating':4.5,'pages':256,'description':'Timeless lessons about wealth, greed, risk, luck, and how personal behaviour matters more than formulas in financial decisions.','tagline':'Doing well with money is about behaviour.','color':'#6B8A68','emoji':'💡'},
 {'id':16,'title':'1984','author':'George Orwell','genre':'Dystopian','year':1949,'rating':4.4,'pages':328,'description':'In a totalitarian society under constant surveillance, Winston Smith struggles with truth, freedom, language, and resistance.','tagline':'Big Brother is watching.','color':'#9A4F4F','emoji':'👁️'},
 {'id':17,'title':'The Song of Achilles','author':'Madeline Miller','genre':'Historical Fiction','year':2011,'rating':4.5,'pages':416,'description':'A lyrical retelling of Greek myth follows Patroclus and Achilles from their youth to the Trojan War and the bonds that shape them.','tagline':'A tale of love and destiny.','color':'#6B6DA0','emoji':'⚔️'},
 {'id':18,'title':'Ikigai','author':'Héctor García and Francesc Miralles','genre':'Self-help','year':2016,'rating':4.0,'pages':208,'description':'An exploration of the Japanese concept of purpose, daily rituals, community, and the habits that support a long and meaningful life.','tagline':'The Japanese secret to a long life.','color':'#7D9B81','emoji':'🍵'},
 {'id':19,'title':'The Martian','author':'Andy Weir','genre':'Science Fiction','year':2011,'rating':4.4,'pages':384,'description':'Stranded alone on Mars, an astronaut uses engineering, humour, and relentless problem-solving to survive against impossible odds.','tagline':'Solve one problem at a time.','color':'#B66B4D','emoji':'🪐'},
 {'id':20,'title':'And Then There Were None','author':'Agatha Christie','genre':'Mystery','year':1939,'rating':4.3,'pages':272,'description':'Ten strangers are invited to an isolated island, where a mysterious voice accuses each of a crime and they begin to die one by one.','tagline':'Ten strangers. One island. No escape.','color':'#626B79','emoji':'🕯️'},
]
BOOKS.extend([
 {'id':21,'title':'The Book Thief','author':'Markus Zusak','genre':'Historical Fiction','year':2005,'rating':4.5,'pages':584,'description':'A young girl living in Nazi Germany finds comfort in stealing books and sharing stories while the world around her changes.','tagline':'Words can be life-changing.','color':'#8D5C4A','emoji':'📕'},
 {'id':22,'title':'The Power of Habit','author':'Charles Duhigg','genre':'Self-help','year':2012,'rating':4.2,'pages':371,'description':'A journalist explores the science of habits and how routines can be understood and reshaped in life and organizations.','tagline':'Understand the routines that shape you.','color':'#B58B4B','emoji':'🔁'},
 {'id':23,'title':'The Three-Body Problem','author':'Liu Cixin','genre':'Science Fiction','year':2008,'rating':4.1,'pages':400,'description':'A scientist becomes involved in a mysterious virtual world and an unfolding first-contact puzzle spanning science and civilization.','tagline':'A mystery on a cosmic scale.','color':'#375B73','emoji':'🪐'},
 {'id':24,'title':'Gone Girl','author':'Gillian Flynn','genre':'Thriller','year':2012,'rating':4.1,'pages':432,'description':'When a wife disappears on her anniversary, media attention and competing accounts turn a marriage into a dark psychological puzzle.','tagline':'Every story has another side.','color':'#6D3438','emoji':'🗝️'},
 {'id':25,'title':'The Little Prince','author':'Antoine de Saint-Exupéry','genre':'Fiction','year':1943,'rating':4.5,'pages':96,'description':'A pilot stranded in the desert meets a young traveller whose encounters reveal tender lessons about love, friendship, and seeing clearly.','tagline':'What matters is often invisible.','color':'#6E8DB5','emoji':'⭐'},
 {'id':26,'title':'The Design of Everyday Things','author':'Don Norman','genre':'Design','year':1988,'rating':4.2,'pages':368,'description':'A foundational guide to human-centred design explaining affordances, feedback, usability, and why everyday objects confuse people.','tagline':'Make things understandable.','color':'#4D8079','emoji':'💡'},
 {'id':27,'title':'Quiet','author':'Susan Cain','genre':'Psychology','year':2012,'rating':4.2,'pages':368,'description':'An exploration of introversion and the strengths of quiet people in a culture that often rewards extroversion and constant self-promotion.','tagline':'The power of a quieter voice.','color':'#7C6A91','emoji':'🌿'},
 {'id':28,'title':'The Lean Startup','author':'Eric Ries','genre':'Business','year':2011,'rating':4.1,'pages':336,'description':'A framework for building ventures through experimentation, validated learning, rapid feedback, and iterative product development.','tagline':'Learn fast, build smarter.','color':'#47735B','emoji':'🚀'},
 {'id':29,'title':'Circe','author':'Madeline Miller','genre':'Fantasy','year':2018,'rating':4.3,'pages':393,'description':'The daughter of a god discovers witchcraft and independence, navigating immortals, monsters, exile, and the cost of choosing her own path.','tagline':'A goddess finds her own voice.','color':'#526A45','emoji':'🌙'},
 {'id':30,'title':'The Thursday Murder Club','author':'Richard Osman','genre':'Mystery','year':2020,'rating':4.1,'pages':368,'description':'Four retirement-village friends who meet to discuss cold cases find themselves investigating a real murder close to home.','tagline':'An unlikely team. A very real mystery.','color':'#6D8C78','emoji':'🔎'},
])
DF = pd.DataFrame(BOOKS)
FULL_TEXT_BOOKS = {8: ROOT / 'data' / 'full_texts' / 'pride_and_prejudice.txt'}


@st.cache_data(show_spinner=False)
def load_full_book_text(book_id):
    """Load the novel body from a bundled public-domain Project Gutenberg file."""
    path = FULL_TEXT_BOOKS.get(int(book_id))
    if not path or not path.exists():
        return ''
    raw = path.read_text(encoding='utf-8', errors='replace')
    start = re.search(r'(?im)^[ \t]*Chapter I\.\][ \t]*$', raw)
    if not start:
        start = re.search(r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK[^\n]*\*\*\*', raw, re.I)
    end = re.search(r'\*\*\* END OF THE PROJECT GUTENBERG EBOOK', raw, re.I)
    body_start = start.start() if start else 0
    body_end = end.start() if end and end.start() > body_start else len(raw)
    return raw[body_start:body_end].strip()


st.markdown('''<style>

:root{--ink:var(--text-color,#202523);--muted:color-mix(in srgb,var(--text-color,#202523) 62%,transparent);--paper:var(--background-color,#f7f6f2);--panel:var(--secondary-background-color,#fff);--green:var(--primary-color,#1d4c3e);--lime:#d9ef84;--line:color-mix(in srgb,var(--text-color,#202523) 14%,transparent)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text-color,#202523)} .stApp{background:var(--background-color,#f7f6f2);color:var(--text-color,#202523)}
.block-container{padding-top:1.7rem;padding-bottom:3rem;max-width:1440px}
[data-testid="stSidebar"]{background:var(--secondary-background-color,#f0efe8);border-right:1px solid var(--line)}
[data-testid="stSidebar"] h1{font-family:'Playfair Display',serif;color:var(--green)}
.hero{background:#1d4c3e;color:#fff;border-radius:24px;padding:34px 38px;position:relative;overflow:hidden;margin-bottom:22px}
.hero:after{content:'✳';position:absolute;right:38px;top:-52px;font-size:220px;color:#d9ef84;opacity:.13}
.eyebrow{letter-spacing:2.4px;text-transform:uppercase;font-size:11px;font-weight:700;color:#d9ef84}
.hero h1{font-family:'Playfair Display',serif;font-size:42px;line-height:1.1;margin:12px 0;color:#fff}
.hero p{color:#dce8df;max-width:560px;font-size:15px;line-height:1.7}
.metric{background:var(--secondary-background-color,#fff);border:1px solid var(--line);border-radius:16px;padding:18px 20px}
.metric .num{font-size:27px;font-weight:700;color:var(--green)}.metric .lbl{font-size:12px;color:var(--muted);margin-top:2px}
.book-card{background:var(--secondary-background-color,#fff);border:1px solid var(--line);border-radius:17px;padding:14px;height:100%;box-shadow:0 4px 16px #26332c08}
.cover{height:190px;border-radius:10px;display:flex;flex-direction:column;justify-content:space-between;padding:16px;color:white;box-shadow:inset 0 0 0 1px #ffffff22;}
.cover .emoji{font-size:30px}.cover .title{font-family:'Playfair Display',serif;font-size:22px;line-height:1.08;font-weight:600}.cover .author{font-size:10px;letter-spacing:1px;text-transform:uppercase;opacity:.85}
.book-title{font-family:'Playfair Display',serif;font-size:18px;font-weight:600;margin-top:12px}.muted{color:var(--muted);font-size:12px}.pill{display:inline-block;background:#edf3e8;color:#315745;border-radius:100px;padding:4px 9px;font-size:11px;font-weight:600}
.section-title{font-family:'Playfair Display',serif;font-size:28px;margin:16px 0 4px}.small-label{font-size:11px;text-transform:uppercase;letter-spacing:1.6px;color:#748078;font-weight:700}
div.stButton>button{border-radius:11px;border:1px solid #d9ddd6;font-weight:600;min-height:2.5rem}div.stButton>button[kind="primary"]{background:#1d4c3e;border-color:#1d4c3e;color:white}
.stTabs [data-baseweb="tab-list"]{gap:8px}.stTabs [data-baseweb="tab"]{border-radius:10px;padding:8px 14px}
div[data-testid="stExpander"]{background:#fff;border-radius:12px;border:1px solid var(--line)}

/* BookWise visual refresh: editorial, calm, and responsive */
.block-container{padding-top:1.25rem;max-width:1480px}
[data-testid="stSidebar"]{background:var(--secondary-background-color,#f0efe8);padding-top:.8rem}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1{font-size:1.65rem;letter-spacing:-.7px;margin-bottom:.25rem}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{font-size:.78rem;line-height:1.35}
[data-testid="stSidebar"] [role="radiogroup"] label p{font-size:.86rem;line-height:1.2}
[data-testid="stSidebar"] [role="radiogroup"]{gap:7px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:5px 8px;border-radius:10px;transition:background .18s ease}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:color-mix(in srgb,var(--primary-color,#1d4c3e) 10%,transparent)}
.hero{padding:42px 42px;border-radius:26px;box-shadow:0 16px 38px #173e3010;background:radial-gradient(circle at 88% 8%,#477761 0%,#1d4c3e 38%,#173b31 100%)}
.hero h1{font-size:clamp(34px,4vw,52px);letter-spacing:-1.3px;max-width:740px}
.hero p{font-size:15px;max-width:610px}
.metric{min-height:96px;box-shadow:0 7px 22px #26332c05;transition:transform .18s ease,box-shadow .18s ease}
.metric:hover,.book-card:hover{transform:translateY(-2px);box-shadow:0 12px 28px #26332c0d}
.book-card{padding:13px;border-radius:19px;transition:transform .18s ease,box-shadow .18s ease;overflow:hidden}
.cover{border-radius:13px;position:relative;box-shadow:inset 0 0 0 1px #ffffff22,0 8px 16px #16241d14}
.cover:after{content:'';position:absolute;inset:0;border-radius:13px;background:linear-gradient(180deg,#ffffff0a 0%,#00000000 40%,#00000025 100%);pointer-events:none}
.book-title{letter-spacing:-.25px}
.section-title{letter-spacing:-.6px;margin-top:24px}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div{border-radius:12px!important}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#477761!important;box-shadow:0 0 0 1px #47776122!important}
div.stButton>button{transition:all .16s ease;border-radius:12px}
div.stButton>button:hover{border-color:#1d4c3e;color:#1d4c3e;transform:translateY(-1px)}
div.stButton>button[kind="primary"]:hover{background:#28624f;color:#fff}
.stTabs [data-baseweb="tab-list"]{background:var(--secondary-background-color,#eeede6);padding:5px;border-radius:14px;flex-wrap:wrap}
.stTabs [data-baseweb="tab"]{border-radius:10px;padding:9px 12px}
.stTabs [aria-selected="true"]{background:var(--background-color,#fff)!important;box-shadow:0 2px 8px #1d4c3e0d}
div[data-testid="stExpander"],div[data-testid="stAlert"]{border-radius:14px}
[data-testid="stMetric"]{background:var(--secondary-background-color,#fff);border:1px solid var(--line);padding:12px 14px;border-radius:14px}
@media(max-width:760px){.block-container{padding-left:1rem;padding-right:1rem}.hero{padding:28px 23px}.hero h1{font-size:34px}.cover{height:165px!important}.cover .title{font-size:19px}}



/* Stable light theme, visible sidebar controls, and no Streamlit deploy decorations. */
:root { color-scheme: light; --ink:#202523; --muted:#68736c; --paper:#f7f6f2; --panel:#ffffff; --green:#1d4c3e; --line:#dfe3dc; }
html, body, .stApp, [data-testid="stAppViewContainer"] { background:#f7f6f2!important; color:#202523!important; }
/* Keep Streamlit header available so the sidebar toggle remains visible. Hide only deploy/menu decorations. */
[data-testid="stDecoration"], #MainMenu, footer { display:none!important; visibility:hidden!important; height:0!important; }
/* Sidebar collapse/expand controls intentionally remain visible and usable. */
[data-testid="stSidebar"] { background:#eeefe8!important; border-right:1px solid #dfe3dc; overflow-x:hidden; }

[data-testid="stSidebarResizer"], [data-testid="stSidebarResizeHandle"] { display:none!important; width:0!important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"], [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#202523!important; overflow-wrap:anywhere; }
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"], .stText, label, [data-testid="stWidgetLabel"] p { color:#202523; }
.muted,.small-label,.metric .lbl { color:#68736c!important; }
.book-title,.section-title { color:#202523!important; }
[data-testid="stExpander"] { background:#ffffff!important; }
.stTextInput input, .stTextArea textarea { color:#202523!important; background:#fff!important; }
[data-baseweb="select"] > div { background:#fff!important; color:#202523!important; }
/* Responsive content and cards */
.block-container { width:100%; min-width:0; }
[data-testid="stImage"] img { display:block; width:100%; height:auto; aspect-ratio: 2 / 3; object-fit:cover; border-radius:12px; }
/* Avoid artificial blank card blocks above covers; style image and nearby book content directly. */
[data-testid="stImage"] { margin-top:0!important; padding-top:0!important; }
[data-testid="stImage"] > img { margin-top:0!important; }
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stImage"]) { margin-top:0!important; }

.book-card { min-width:0; }
@media (max-width: 1050px) {
  .block-container { padding-left:1.2rem; padding-right:1.2rem; }
  .hero { padding:30px 26px; }
  .section-title { font-size:25px; }
}
@media (max-width: 760px) {
  
  
  .block-container { padding-left:0.8rem; padding-right:0.8rem; padding-top:0.8rem; }
  .hero { padding:25px 20px; border-radius:18px; }
  .hero h1 { font-size:clamp(29px,8vw,38px); }
  .hero p { font-size:14px; }
  .metric { padding:13px; min-height:80px; }
  .metric .num { font-size:22px; }
  .book-card { padding:10px; }
  .book-title { font-size:16px; }
  [data-testid="stHorizontalBlock"] { gap:0.65rem; }
}
@media (max-width: 480px) {
  .cover { height:155px !important; }
  .cover .title { font-size:17px; }
  .section-title { font-size:23px; }
  div.stButton > button { padding-left:0.5rem; padding-right:0.5rem; font-size:0.85rem; }
}

/* BookWise professional polish: offline-safe typography, responsive layout, and accessible states. */
:root{--ink:#202523;--muted:#68736c;--paper:#f7f6f2;--green:#1d4c3e;--green-soft:#e8efe9;--line:#dfe3dc;--serif:Georgia,'Times New Roman',serif;--sans:'Aptos','Segoe UI',sans-serif}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--paper)!important;color:var(--ink)!important;font-family:var(--sans)}
.block-container{width:100%;max-width:1440px;padding:1.35rem 2rem 3rem;min-width:0}
[data-testid="stSidebar"]{background:#eeefe8!important;border-right:1px solid var(--line);overflow-x:hidden}
[data-testid="stSidebar"] h1{font-family:var(--serif);color:var(--green);font-size:1.7rem;letter-spacing:-.04em}
[data-testid="stSidebar"] [role="radiogroup"]{gap:5px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:6px 9px;border-radius:10px;transition:background .16s ease}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#dfe8df}
.hero{padding:40px 42px;border-radius:24px;background:radial-gradient(circle at 88% 8%,#477761 0%,#1d4c3e 38%,#173b31 100%);box-shadow:0 14px 34px #173e3012}
.hero h1{max-width:740px;font-family:var(--serif);font-size:clamp(34px,4vw,52px);letter-spacing:-1.2px}
.hero p{max-width:610px;color:#e2ebe4;line-height:1.7}
.section-title,.book-title{font-family:var(--serif);color:var(--ink)!important;letter-spacing:-.35px}
.section-title{margin:22px 0 4px;font-size:28px}.book-title{font-size:18px;font-weight:700}
.muted,.small-label,.metric .lbl{color:var(--muted)!important}.muted{font-size:12px;line-height:1.5}
.pill{background:var(--green-soft);color:#315745;border-radius:999px;font-weight:650}
.metric{min-height:92px;padding:17px 18px;border:1px solid var(--line);border-radius:16px;background:#fff;box-shadow:0 5px 18px #26332c06;transition:transform .18s ease,box-shadow .18s ease}
.metric:hover{transform:translateY(-2px);box-shadow:0 10px 24px #26332c0d}
.cover{border-radius:13px;box-shadow:inset 0 0 0 1px #ffffff22,0 8px 16px #16241d14}.cover .title{font-family:var(--serif);font-weight:700}
[data-testid="stImage"] img{display:block;width:100%;height:auto;aspect-ratio:2/3;object-fit:cover;border-radius:12px}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div{border-radius:11px!important;background:#fff!important;color:var(--ink)!important}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#477761!important;box-shadow:0 0 0 2px #47776122!important}
div.stButton>button{min-height:2.55rem;border:1px solid #d9ddd6;border-radius:11px;font-weight:650;transition:transform .16s ease,background .16s ease,border-color .16s ease}
div.stButton>button:hover{transform:translateY(-1px);border-color:var(--green);color:var(--green)}
div.stButton>button[kind="primary"]{border-color:var(--green);background:var(--green);color:#fff}
div.stButton>button[kind="primary"]:hover{background:#28624f;color:#fff}div.stButton>button:focus-visible{outline:3px solid #95b6a2;outline-offset:2px}
[data-testid="stMetric"],div[data-testid="stExpander"],div[data-testid="stAlert"]{border-radius:14px}
.stTabs [data-baseweb="tab-list"]{gap:5px;flex-wrap:wrap;padding:5px;border-radius:13px;background:#eeede6}.stTabs [data-baseweb="tab"]{padding:8px 11px;border-radius:9px}
.stTabs [aria-selected="true"]{background:#fff!important;box-shadow:0 2px 8px #1d4c3e0d}div[data-testid="stExpander"]{border:1px solid var(--line);background:#fff}
@media(max-width:1050px){.block-container{padding-left:1.2rem;padding-right:1.2rem}.hero{padding:32px 28px}.section-title{font-size:25px}}
@media(max-width:760px){.block-container{padding:.9rem .85rem 2.5rem}.hero{padding:27px 21px;border-radius:19px}.hero h1{font-size:clamp(30px,8vw,39px)}.hero p{font-size:14px}.metric{min-height:78px;padding:12px}.metric .num{font-size:22px}.cover{height:165px!important}.cover .title{font-size:19px}.book-title{font-size:16px}[data-testid="stHorizontalBlock"]{gap:.65rem}}
@media(max-width:480px){.cover{height:150px!important}.cover .title{font-size:17px}.section-title{font-size:23px}div.stButton>button{padding-right:.5rem;padding-left:.5rem;font-size:.85rem}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important}}
</style>''', unsafe_allow_html=True)

PAGES = ['Discover','Recommendations','My Shelf','Reading Tracker','Explore Insights','Book Insights','Text Insights','Similarity Matcher','About BookWise']
if 'page' not in st.session_state or st.session_state.page not in PAGES: st.session_state.page = 'Discover'
if 'shelf' not in st.session_state: st.session_state.shelf = []
if 'liked' not in st.session_state: st.session_state.liked = []
if 'reading_status' not in st.session_state: st.session_state.reading_status = {}
if 'reading_progress' not in st.session_state: st.session_state.reading_progress = {}
if 'reviews' not in st.session_state: st.session_state.reviews = {}
if 'goal' not in st.session_state: st.session_state.goal = 12
if 'preferred_genres' not in st.session_state: st.session_state.preferred_genres = ['Fantasy','Mystery','Science Fiction']

with st.sidebar:
    st.markdown('<div style="font-size:34px">✳</div>', unsafe_allow_html=True)
    st.markdown('# BookWise')
    st.caption('YOUR NEXT CHAPTER STARTS HERE')
    st.divider()
    page = st.radio('YOUR READING SPACE', PAGES, index=PAGES.index(st.session_state.page), label_visibility='visible', format_func=lambda x: {'Discover':'⌂  Discover','Recommendations':'✦  For You','My Shelf':'▤  My Shelf','Reading Tracker':'◷  Reading Tracker','Explore Insights':'◈  Explore Insights','Book Insights':'▧  Book Insights','Text Insights':'⌘  Text Insights','Similarity Matcher':'⇄  Similarity Matcher','About BookWise':'ⓘ  About BookWise'}[x])
    st.session_state.page = page
    st.divider()
    st.markdown('**Your reading space**')
    st.caption(f'♡  {len(st.session_state.shelf)} saved books')
    st.caption(f'◷  {sum(1 for v in st.session_state.reading_status.values() if v == "Finished")} finished books')
    st.caption('Smart matching · TF-IDF · similarity scoring')
    st.markdown('<div style="height:12px"></div><div style="font-size:11px;color:#788078">PERSONAL READING COMPANION<br>OFFLINE DEMO CATALOGUE</div>', unsafe_allow_html=True)


def book_cover(book, height=190):
    """Display a bundled, offline-safe original cover illustration for a catalogue book."""
    cover_path = ROOT / 'assets' / 'covers' / f"{int(book['id']):02d}.jpg"
    if cover_path.exists():
        st.image(str(cover_path), use_container_width=True)
    else:
        st.markdown(f'''<div class="cover" style="height:{height}px;background:linear-gradient(145deg,{book['color']},#202b31)"><div class="emoji">{book['emoji']}</div><div><div class="title">{book['title']}</div><div class="author" style="margin-top:9px">{book['author']}</div></div></div>''', unsafe_allow_html=True)


def add_book(book_id):
    if book_id not in st.session_state.shelf: st.session_state.shelf.append(book_id)


def recommend(query, genre='All genres', min_rating=0.0, top_n=6):
    candidates = DF.copy()
    if genre != 'All genres': candidates = candidates[candidates.genre == genre]
    candidates = candidates[candidates.rating >= min_rating]
    if candidates.empty: return candidates
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        corpus = (DF.title + ' ' + DF.author + ' ' + DF.genre + ' ' + DF.description).tolist()
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
        matrix = vectorizer.fit_transform(corpus)
        qv = vectorizer.transform([query])
        scores = cosine_similarity(qv, matrix).ravel()
    except Exception:
        terms = set(re.findall(r'\w+', query.lower()))
        scores = [len(terms & set(re.findall(r'\w+', x.lower()))) / max(len(terms),1) for x in (DF.title+' '+DF.author+' '+DF.genre+' '+DF.description)]
    candidates = candidates.copy(); candidates['match'] = [float(scores[i-1]) for i in candidates.id]
    return candidates.sort_values(['match','rating'],ascending=False).head(top_n)


def render_book_grid(frame, prefix='discover'):
    if frame.empty:
        st.info('No books match these filters. Try a broader genre or lower rating.')
        return
    cols = st.columns(3, gap='medium')
    for idx, (_, row) in enumerate(frame.iterrows()):
        b = row.to_dict(); bid=int(b['id'])
        with cols[idx % 3]:
            book_cover(b)
            st.markdown(f'<div class="book-title">{b["title"]}</div><div class="muted">{b["author"]} · {int(b["year"])}</div><div style="margin-top:9px"><span class="pill">{b["genre"]}</span> &nbsp; <span style="font-size:12px;color:#9b7730">★ {b["rating"]}</span></div><p style="font-size:12px;line-height:1.55;color:#626a64;min-height:55px">{b["description"][:112]}…</p>', unsafe_allow_html=True)
            if 'match' in b and float(b.get('match',0)) > 0:
                st.caption(f'✳ {round(float(b["match"])*100)}% text match')
            c1,c2,c3=st.columns(3)
            with c1:
                if st.button('＋ Save', key=f'{prefix}_save_{bid}', use_container_width=True):
                    add_book(bid); st.toast('Added to My Shelf')
            with c2:
                if st.button('Details', key=f'{prefix}_details_{bid}', use_container_width=True):
                    st.session_state[f'detail_{prefix}'] = bid
            with c3:
                if st.button('Insights', key=f'{prefix}_insights_{bid}', use_container_width=True):
                    st.session_state.insights_book_id = bid
                    st.session_state.book_insights_title = b['title']
                    st.session_state.page = 'Book Insights'
                    st.rerun()
            if st.session_state.get(f'detail_{prefix}') == bid:
                with st.expander(f'About {b["title"]}', expanded=True):
                    st.write(b['description']); st.caption(f'{b["pages"]} pages · Published {b["year"]} · Rated {b["rating"]}/5')
                    st.write('**Why it may fit:** ' + (f"Your search overlaps with this book's description (text match {float(b.get('match',0)):.2f})." if 'match' in b else 'Explore its genre, themes, and description.'))

def render_text_insight_tools(text_input, book_title=None):
    tabs=st.tabs(['Overview','Clean keywords','Refine words','Word forms','Next-word ideas','Sentence roles','Key phrases','Names & places','Compare text','Popular words'])
    with tabs[0]:
        if book_title:
            st.subheader(f'Text profile · {book_title}')
            st.write('The tools below analyze the selected text. Whole-book totals above use the full bundled novel when available.')
            st.write('**Techniques:** Tokenization · TF-IDF · cosine similarity · word frequency analysis')
        else:
            st.subheader('How BookWise understands your search')
            st.write('**Problem:** Readers face difficulty finding books matching their interests across large catalogs.')
            st.write('**Approach:** Text categorization, text similarity, information retrieval, and preprocessing.')
            st.write('**Techniques:** Tokenization · TF-IDF · cosine similarity · word frequency analysis')
            st.success('BookWise helps readers discover stories that fit their interests.')
    with tabs[1]:
        st.subheader('Tokenization, filtration & script validation')
        tokens=tokenize(text_input); filtered=filter_tokens(tokens); valid=validate_script(text_input)
        a,b,c=st.columns(3)
        a.metric('Tokens',len(tokens)); b.metric('Filtered tokens',len(filtered)); c.metric('Scripts detected',len(valid['scripts_found']))
        st.write('**Tokens**'); st.code(' · '.join(tokens) or '(empty)'); st.write('**Filtered tokens**'); st.code(' · '.join(filtered) or '(empty)'); st.json(valid)
    with tabs[2]:
        st.subheader('Stop-word removal, stemming & lemmatization')
        result=stopword_stem_lemma(text_input)
        for label,key in [('Original tokens','tokens'),('Without stop words','without_stopwords'),('Stemmed words','stemmed'),('Lemmatized words','lemmatized')]:
            st.markdown('**'+label+'**'); st.code(' · '.join(result[key]) or '(empty)')
        st.caption('Stemming and lemmatization are lightweight educational approximations, not a full linguistic model.')
    with tabs[3]:
        st.subheader('Morphological analysis & word generation')
        result=morphology(text_input)
        if result['analysis']: st.dataframe(pd.DataFrame(result['analysis']),use_container_width=True,hide_index=True)
        else: st.info('Enter some alphabetic words to analyze morphology.')
    with tabs[4]:
        st.subheader('N-gram model, next-word prediction & generation')
        n=st.select_slider('N-gram size',options=[2,3,4],value=2); context=st.text_input('Context / seed phrase','a curious young')
        model=build_ngram_model(text_input,n); prediction=predict_next_word(model,context); generated=generate_text(model,context or text_input.split()[0] if text_input.split() else '',8)
        st.metric('N-gram contexts',len(model)); st.write('**Next word prediction**'); st.info(prediction or 'No matching context found in this input.'); st.write('**Generated continuation**'); st.code(generated or 'Add more text to build a model.')
        st.caption('This is a small corpus-based demo; results depend on the text supplied.')
    with tabs[5]:
        st.subheader('Part-of-speech tagging')
        try:
            import nltk
            toks=nltk.word_tokenize(text_input); tags=nltk.pos_tag(toks)
            st.dataframe(pd.DataFrame(tags,columns=['Token','POS tag']),use_container_width=True,hide_index=True)
        except Exception:
            words=re.findall(r"\b[\w']+\b|[^\w\s]",text_input)
            st.dataframe(pd.DataFrame([(w,'NN (fallback)') for w in words],columns=['Token','POS tag']),use_container_width=True,hide_index=True)
            st.warning('NLTK tagger resources are unavailable in this environment, so a clearly labelled fallback is shown. Optional resource download instructions are in README.md.')
    with tabs[6]:
        st.subheader('Chunking with a simple NP / PP / VP grammar')
        try:
            import nltk
            tagged=nltk.pos_tag(nltk.word_tokenize(text_input)); grammar=r'NP: {<DT>?<JJ.*>*<NN.*>+}\nPP: {<IN><NP>}\nVP: {<VB.*><NP|PP>*}'
            tree=nltk.RegexpParser(grammar).parse(tagged)
            chunks=[]
            for subtree in tree.subtrees():
                if subtree.label() in ['NP','VP','PP']: chunks.append({'type':subtree.label(),'phrase':' '.join(w for w,t in subtree.leaves())})
            if chunks: st.dataframe(pd.DataFrame(chunks),use_container_width=True,hide_index=True)
            else: st.info('No chunks identified by the simple grammar.')
            st.code(str(tree))
        except Exception: st.warning('Chunking requires NLTK tokenizer and POS-tagger resources. Try the POS tag experiment or install resources as documented in README.md.')
    with tabs[7]:
        st.subheader('Named entity recognition')
        try:
            import nltk
            tagged=nltk.pos_tag(nltk.word_tokenize(text_input)); tree=nltk.ne_chunk(tagged)
            entities=[]
            for node in tree:
                if hasattr(node,'label'): entities.append({'entity':' '.join(w for w,t in node.leaves()),'label':node.label()})
            if entities: st.dataframe(pd.DataFrame(entities),use_container_width=True,hide_index=True)
            else: st.info('No named entities identified in this text.')
        except Exception: st.warning('NER requires optional NLTK tokenizer, POS-tagger and named-entity resources. Install resources as documented in README.md.')
    with tabs[8]:
        st.subheader('TF-IDF text similarity recognizer')
        other=st.text_area('Compare with another description',value='A young investigator searches for clues in a secret archive and uncovers a mystery about courage and friendship.',height=100)
        score,level=compare_texts(text_input,other); st.metric('Cosine similarity',f'{score*100:.1f}%'); st.progress(min(max(score,0),1)); st.write(f'**Similarity level:** {level}')
        st.caption('TF-IDF highlights overlapping informative terms; similarity is not a measure of literary quality.')
    with tabs[9]:
        st.subheader('Text exploratory analysis & word frequencies')
        cleaned=re.sub(r'[^a-zA-Z\s]','',str(text_input).lower()); stop={'a','an','the','and','or','is','are','of','to','in','for','on','with','it','this','that'}
        freq=Counter(w for w in cleaned.split() if w not in stop)
        if freq:
            freq_df=pd.DataFrame(freq.most_common(15),columns=['Word','Frequency'])
            st.bar_chart(freq_df.set_index('Word')); st.dataframe(freq_df,use_container_width=True,hide_index=True)
        else: st.info('Enter a longer text to see word frequencies.')
        st.caption('The chart is a frequency view; it is not a generated word-cloud image.')

if page == 'Discover':
    st.markdown('''<div class="hero"><div class="eyebrow">✳ A little more you, in every book</div><h1>Find the story<br>that finds you.</h1><p>Discover books that match your mood, interests, and curiosity. Describe what you love, and find your next memorable read.</p></div>''', unsafe_allow_html=True)
    m1,m2,m3,m4=st.columns(4)
    for col,num,lbl in [(m1,'30','Curated demo books'),(m2,'10','reading insights tools'),(m3,'TF-IDF','Text understanding'),(m4,'♡ '+str(len(st.session_state.shelf)),'Books on your shelf')]:
        with col: st.markdown(f'<div class="metric"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">What are you in the mood for?</div><div class="muted">Search by a feeling, topic, genre, author, or a sentence about what you want to read.</div>',unsafe_allow_html=True)
    with st.form('search_form'):
        query=st.text_input('Describe your next read', placeholder='e.g. a clever mystery with unexpected twists, or a book about building better habits')
        f1,f2,f3=st.columns([1.2,1,1])
        genres=['All genres']+sorted(DF.genre.unique().tolist())
        with f1: genre=st.selectbox('Genre',genres)
        with f2: min_rating=st.select_slider('Minimum reader rating',options=[0.0,3.5,4.0,4.2,4.5],value=0.0,format_func=lambda x:'Any' if x==0 else f'{x} ★+')
        with f3: top_n=st.selectbox('Recommendations', [3,6,9],index=1)
        submitted=st.form_submit_button('✳ Find my next read', type='primary', use_container_width=True)
    if submitted:
        if not query.strip(): query='popular engaging books across different genres'
        st.session_state.search_query=query
        st.session_state.search_results=recommend(query,genre,min_rating,top_n)
    if st.session_state.get('search_results') is not None:
        st.markdown(f'<div class="section-title">Your recommendations</div><div class="muted">Ranked by textual similarity to: “{st.session_state.get("search_query", "") }”</div>',unsafe_allow_html=True)
        render_book_grid(st.session_state.search_results, 'search')
    else:
        st.markdown('<div class="section-title">Popular with curious readers</div><div class="muted">A hand-picked mix to get your discovery started.</div>',unsafe_allow_html=True)
        render_book_grid(DF.sort_values('rating',ascending=False).head(6),'popular')

elif page == 'Recommendations':
    st.markdown('<div class="section-title">Picked for your next chapter</div><div class="muted">Tune your reading tastes and get recommendations shaped around your interests.</div>', unsafe_allow_html=True)
    genres=sorted(DF.genre.unique().tolist())
    st.session_state.preferred_genres=st.multiselect('Genres you enjoy', genres, default=[g for g in st.session_state.preferred_genres if g in genres])
    mood=st.selectbox('What kind of read are you in the mood for?', ['Surprise me','Thought-provoking','Comforting and uplifting','Fast-paced and suspenseful','Learn something practical','Epic and imaginative','Short and easy to finish'])
    reading_time=st.select_slider('Preferred length',options=['Quick read','Medium','Long immersive read'],value='Medium')
    if st.button('Build my reading list',type='primary'):
        mood_terms={'Surprise me':'engaging curious discovery','Thought-provoking':'psychology ideas society philosophy','Comforting and uplifting':'hopeful personal growth friendship','Fast-paced and suspenseful':'mystery thriller secrets clues danger','Learn something practical':'habits productivity money learning','Epic and imaginative':'fantasy adventure science fiction world','Short and easy to finish':'short concise accessible'}
        base=DF[DF.genre.isin(st.session_state.preferred_genres)] if st.session_state.preferred_genres else DF.copy()
        if reading_time=='Quick read': base=base[base.pages<=300]
        elif reading_time=='Long immersive read': base=base[base.pages>=400]
        ranked=recommend(mood_terms[mood],top_n=9)
        if not base.empty: ranked=ranked[ranked.id.isin(base.id)]
        st.session_state.personal_results=ranked if not ranked.empty else recommend(mood_terms[mood],top_n=6)
    if st.session_state.get('personal_results') is not None: render_book_grid(st.session_state.personal_results,'personal')
    else:
        st.info('Choose your favourite genres and reading mood, then build a list tailored to you.')
        render_book_grid(DF.sort_values('rating',ascending=False).head(6),'for_you_seed')

elif page == 'Reading Tracker':
    st.markdown('<div class="section-title">Your reading journey</div><div class="muted">Set a goal, track your progress, and celebrate every finished chapter.</div>', unsafe_allow_html=True)
    finished=sum(1 for v in st.session_state.reading_status.values() if v=='Finished')
    currently=sum(1 for v in st.session_state.reading_status.values() if v=='Currently Reading')
    a,b,c=st.columns(3); a.metric('Books finished',finished); b.metric('In progress',currently); c.metric('Yearly goal',st.session_state.goal)
    st.session_state.goal=st.number_input('Books to finish this year',min_value=1,max_value=200,value=int(st.session_state.goal),step=1)
    st.progress(min(finished/st.session_state.goal,1.0),text=f'{finished} of {st.session_state.goal} books completed · {max(st.session_state.goal-finished,0)} to go')
    st.subheader('Update your reading')
    title=st.selectbox('Choose a book',DF.title.tolist(),key='tracker_book_select')
    book=DF[DF.title==title].iloc[0]; bid=int(book.id)
    current=st.session_state.reading_status.get(bid,'Want to Read')
    status=st.selectbox('Reading status',['Want to Read','Currently Reading','Finished'],index=['Want to Read','Currently Reading','Finished'].index(current))
    maxpages=int(book.pages); progress=int(st.session_state.reading_progress.get(bid,0))
    pages=st.slider('Pages read',0,maxpages,min(progress,maxpages),key=f'pages_{bid}')
    rating=st.slider('Your personal rating',1,5,int(st.session_state.reviews.get(bid,5)),key=f'rating_{bid}')
    note=st.text_area('Private reading note (optional)',value=st.session_state.get(f'note_{bid}',''),placeholder='A quote, thought, or takeaway you want to remember…')
    if st.button('Save reading update',type='primary'):
        st.session_state.reading_status[bid]=status; st.session_state.reading_progress[bid]=pages; st.session_state.reviews[bid]=rating; st.session_state[f'note_{bid}']=note
        if status=='Finished': st.session_state.reading_progress[bid]=maxpages
        st.toast('Reading progress saved'); st.rerun()
    st.subheader('Your reading log')
    rows=[]
    for book_id,stt in st.session_state.reading_status.items():
        r=DF[DF.id==int(book_id)].iloc[0]
        rows.append({'Book':r.title,'Status':stt,'Progress':f"{st.session_state.reading_progress.get(book_id,0)}/{int(r.pages)} pages",'Your rating':'★'*int(st.session_state.reviews.get(book_id,0))})
    if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else: st.info('Your reading log is empty. Add a book above to start tracking.')
    if rows: st.download_button('Export reading log',pd.DataFrame(rows).to_csv(index=False).encode(), 'bookwise_reading_log.csv','text/csv')

elif page == 'Explore Insights':
    st.markdown('<div class="section-title">Explore the catalogue</div><div class="muted">A closer look at genres, ratings, reading length, and the collection.</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3); c1.metric('Titles in catalogue',len(DF)); c2.metric('Genres',DF.genre.nunique()); c3.metric('Average rating',f"{DF.rating.mean():.1f} ★")
    left,right=st.columns(2)
    with left:
        st.subheader('Books by genre'); st.bar_chart(DF.genre.value_counts().sort_values(ascending=False))
        st.subheader('Rating distribution'); st.bar_chart(DF.assign(Rating=DF.rating.round(1)).groupby('Rating').size())
    with right:
        st.subheader('Reading length'); st.bar_chart(DF.assign(Length=pd.cut(DF.pages,[0,250,400,1000],labels=['Short','Medium','Long'])).groupby('Length',observed=False).size())
        st.subheader('Highest-rated picks'); st.dataframe(DF.sort_values(['rating','year'],ascending=[False,False])[['title','author','genre','rating','pages']].head(10),use_container_width=True,hide_index=True)
    st.download_button('Download full catalogue CSV',DF.drop(columns=['color','emoji']).to_csv(index=False).encode(),'bookwise_catalogue.csv','text/csv')

elif page == 'Similarity Matcher':
    st.markdown('<div class="section-title">Compare two book ideas</div><div class="muted">Paste descriptions or select books to see how closely their themes and language overlap.</div>',unsafe_allow_html=True)
    options=['Write my own text…']+DF.title.tolist()
    one=st.selectbox('First book or description',options,key='sim_one'); two=st.selectbox('Second book or description',options,index=2,key='sim_two')
    def get_desc(choice,key):
        if choice=='Write my own text…': return st.text_area('Enter description',key=key,placeholder='Paste a short synopsis or your reading idea…')
        return str(DF[DF.title==choice].iloc[0].description)
    t1=get_desc(one,'sim_text_one'); t2=get_desc(two,'sim_text_two')
    if one!='Write my own text…': st.caption('First description: '+t1)
    if two!='Write my own text…': st.caption('Second description: '+t2)
    if st.button('Compare descriptions',type='primary'):
        score,level=compare_texts(t1,t2); a,b=st.columns([1,2]); a.metric('Similarity score',f'{score*100:.1f}%'); b.progress(min(max(score,0),1),text=level)
        st.write('**How to read this:** higher scores indicate more shared terms and themes, not a judgement of quality or a guarantee that you will like both books.')

elif page == 'My Shelf':
    st.markdown('<div class="section-title">My Shelf</div><div class="muted">A quiet corner for the books you want to come back to.</div>',unsafe_allow_html=True)
    ids=st.session_state.shelf
    if not ids:
        st.info('Your shelf is waiting for its first book. Head to Discover and choose ＋ Save on any title.')
        render_book_grid(DF.sort_values('rating',ascending=False).head(3),'shelf_suggest')
    else:
        st.markdown(f'**{len(ids)} saved title(s)**')
        selected=DF[DF.id.isin(ids)]
        cols=st.columns(3)
        for i,(_,r) in enumerate(selected.iterrows()):
            b=r.to_dict(); bid=int(b['id'])
            with cols[i%3]:
                book_cover(b,170)
                st.markdown(f'<div class="book-title">{b["title"]}</div><div class="muted">{b["author"]}</div><p style="font-size:12px">{b["description"]}</p>',unsafe_allow_html=True)
                remove_col,insight_col=st.columns(2)
                with remove_col:
                    if st.button('Remove from shelf',key=f'remove_{bid}',use_container_width=True):
                        st.session_state.shelf.remove(bid); st.rerun()
                with insight_col:
                    if st.button('Insights',key=f'shelf_insights_{bid}',use_container_width=True):
                        st.session_state.insights_book_id = bid
                        st.session_state.book_insights_title = b['title']
                        st.session_state.page = 'Book Insights'
                        st.rerun()
        csv=selected[['title','author','genre','year','rating']].to_csv(index=False).encode('utf-8')
        st.download_button('↓ Export my shelf (CSV)',csv,'my_bookwise_shelf.csv','text/csv')

elif page == 'Book Insights':
    st.markdown('<div class="section-title">Book-by-book text insights</div><div class="muted">Choose a title to explore its language. A complete text from Project Gutenberg is bundled for Pride and Prejudice; other titles use their catalogue synopsis.</div>', unsafe_allow_html=True)
    titles=DF.title.tolist()
    default_book_id=int(st.session_state.get('insights_book_id', 8))
    default_row=DF[DF.id==default_book_id]
    default_title=str(default_row.iloc[0].title) if not default_row.empty else titles[0]
    if 'book_insights_title' not in st.session_state:
        st.session_state.book_insights_title=default_title
    selected_title=st.selectbox('Choose a book',titles,key='book_insights_title')
    book=DF[DF.title==selected_title].iloc[0].to_dict()
    bid=int(book['id'])
    st.session_state.insights_book_id=bid
    full_text=load_full_book_text(bid)
    analysis_source=full_text if full_text else str(book['description'])
    if full_text:
        words=re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?",analysis_source.lower())
        stopwords=set('all am an and are as at be been before being but by can could did do does for from had has have he her hers herself him himself his how i if in into is it its just may me might more most must my no nor not of off on once only or other our ours out over own said same she should so some such than that the their them then there these they this those through to too up us very was we were what when where which while who whom why will with would you your mr mrs miss ms sir madam one much little every'.split())
        keywords=[word for word in filter_tokens(words) if word not in stopwords]
        chapters=len(re.findall(r'(?im)^[ \t]*Chapter\s+[IVXLCDM]+\.\]?[ \t]*$',analysis_source))
        metric_cols=st.columns(4)
        metric_cols[0].metric('Words in full text',f'{len(words):,}')
        metric_cols[1].metric('Distinct terms',f'{len(set(keywords)):,}')
        metric_cols[2].metric('Chapters',f'{chapters:,}')
        metric_cols[3].metric('Text source','Full book')
        st.markdown('#### Most-used keywords')
        frequent=Counter(keywords).most_common(15)
        if frequent:
            frequency_frame=pd.DataFrame(frequent,columns=['Word','Frequency'])
            chart_col,table_col=st.columns([1.3,1])
            with chart_col: st.bar_chart(frequency_frame.set_index('Word'))
            with table_col: st.dataframe(frequency_frame,use_container_width=True,hide_index=True)
        next_chapter=re.search(r'(?im)^[ \t]*Chapter II\.\]?[ \t]*$',analysis_source)
        excerpt=analysis_source[:next_chapter.start()] if next_chapter else analysis_source[:4500]
        st.caption('Whole-book totals and frequent terms use the complete novel. The interactive classroom tools below start with Chapter I so their detailed tables stay responsive; you can edit the sample text.')
        st.markdown('[Full text source: Project Gutenberg, eBook 1342](https://www.gutenberg.org/ebooks/1342)')
    else:
        excerpt=analysis_source
        words=re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?",analysis_source.lower())
        metric_cols=st.columns(3)
        metric_cols[0].metric('Words in synopsis',f'{len(words):,}')
        metric_cols[1].metric('Distinct terms',f'{len(set(filter_tokens(words))):,}')
        metric_cols[2].metric('Text source','Catalogue synopsis')
        st.info('This title has no complete text bundled. Insights use the short catalogue synopsis. Add a text you own or are licensed to use, then register its path in FULL_TEXT_BOOKS in app.py to enable full-book analysis.')
    st.subheader(f"Explore {book['title']}")
    analysis_excerpt=st.text_area('Text used by the interactive tools',value=excerpt,height=180,key=f'book_lab_text_{bid}',help='For the bundled full-text title, whole-book statistics above use the complete novel; detailed classroom tools use this editable excerpt.')
    render_text_insight_tools(analysis_excerpt, book_title=book['title'])
elif page == 'Text Insights':
    st.markdown('<div class="section-title">Reading Insights</div><div class="muted">Explore the ten reading insights tools integrated into the BookWise project. Use any text or a sample book description.</div>',unsafe_allow_html=True)
    sample='A curious young detective discovers a hidden library filled with mysterious stories and ancient secrets. She follows clues through the city and learns that courage, friendship, and knowledge can change the world.'
    text_input=st.text_area('Input text',value=sample,height=110,help='This text is used by the text-processing experiments below.')
    render_text_insight_tools(text_input)

elif page == 'About BookWise':
    st.markdown('<div class="section-title">About BookWise</div><div class="muted">A thoughtful book discovery experience with an integrated reading insights studio.</div>',unsafe_allow_html=True)
    st.markdown('''<div class="hero"><div class="eyebrow">PROJECT OVERVIEW</div><h1>Books picked for your kind of curiosity</h1><p>BookWise helps readers discover relevant books by comparing the language of their interests with book descriptions using TF-IDF and cosine similarity.</p></div>''',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.subheader('Problem statement'); st.write('Readers face difficulty finding books matching their interests across large catalogs. BookWise provides a simple discovery interface that searches book metadata and ranks textually relevant titles.')
        st.subheader('Core features')
        for x in ['Search by topic, mood, title, author, or description','Genre and minimum-rating filters','TF-IDF / cosine-similarity recommendations','Save books to a personal shelf and export CSV','Book-by-book text insights, including one complete Project Gutenberg text','Interactive reading insights with ten text-analysis tools']: st.markdown('✓ '+x)
    with c2:
        st.subheader('Technology stack')
        st.markdown('- **Python** — application logic\n- **Streamlit** — interactive web UI\n- **scikit-learn** — TF-IDF and cosine similarity\n- **NLTK** — optional POS tagging, chunking, and NER\n- **Pandas** — book catalogue and tables')
        st.subheader('System workflow')
        st.code('User query → Text preprocessing → TF-IDF vectors → Cosine similarity → Ranked recommendations → Save to shelf')
        st.subheader('Project limitations')
        st.caption('The included catalogue is a curated demo dataset, not a live commercial book database. Recommendations are content-based and do not use collaborative filtering or real user ratings.')
    st.download_button('↓ Download catalogue data (CSV)',DF.drop(columns=['color','emoji']).to_csv(index=False).encode('utf-8'),'book_catalogue.csv','text/csv')

st.markdown('<div style="border-top:1px solid #e5e3dc;margin-top:38px;padding-top:16px;color:#8b918b;font-size:11px;display:flex;justify-content:space-between"><span>BOOKWISE · SMART BOOK DISCOVERY</span><span>Built for learning · Demo catalogue</span></div>',unsafe_allow_html=True)
