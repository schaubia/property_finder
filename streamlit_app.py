import streamlit as st

st.set_page_config(
    page_title="Career Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main > div { padding-top: 1rem; }

h1, h2, h3 {
    font-family: 'DM Serif Display', serif !important;
    font-weight: 400 !important;
}

.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    font-weight: 400;
    text-align: center;
    margin-bottom: 0.5rem;
    line-height: 1.2;
}

.hero-title em {
    color: #1D9E75;
    font-style: italic;
}

.hero-sub {
    text-align: center;
    color: #666;
    font-size: 1rem;
    margin-bottom: 2.5rem;
    line-height: 1.7;
}

.section-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    color: #1D9E75;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.section-heading {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    font-weight: 400;
    margin-bottom: 0.3rem;
}

.section-desc {
    color: #777;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
    line-height: 1.6;
}

.path-card {
    background: #f8f9fa;
    border-radius: 12px;
    border: 0.5px solid #e0e0e0;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}

.path-title {
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 0.4rem;
}

.path-why {
    font-size: 0.88rem;
    color: #555;
    line-height: 1.6;
    margin-bottom: 0.8rem;
}

.badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 12px;
    margin-right: 6px;
    margin-bottom: 4px;
}

.badge-green { background: #E1F5EE; color: #085041; }
.badge-amber { background: #FAEEDA; color: #633806; }
.badge-blue  { background: #E6F1FB; color: #042C53; }
.badge-red   { background: #FCEBEB; color: #791F1F; }
.badge-gray  { background: #F1EFE8; color: #5F5E5A; border: 0.5px solid #ddd; }

.resource-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 0.5px solid #e8e8e8;
    font-size: 0.85rem;
}

.resource-row:last-child { border-bottom: none; }
.res-name { font-weight: 500; }
.res-meta { font-size: 0.78rem; color: #888; }

.risk-bar-container {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 7px;
}

.risk-label {
    font-size: 0.8rem;
    color: #555;
    min-width: 200px;
}

.risk-track {
    flex: 1;
    height: 6px;
    background: #eee;
    border-radius: 3px;
    overflow: hidden;
}

.risk-pct {
    font-size: 0.78rem;
    color: #888;
    min-width: 36px;
    text-align: right;
}

.alert-info {
    background: #E6F1FB;
    border: 0.5px solid #85B7EB;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.88rem;
    color: #042C53;
    margin-bottom: 1.2rem;
    line-height: 1.6;
}

.alert-warn {
    background: #FAEEDA;
    border: 0.5px solid #FAC775;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.88rem;
    color: #633806;
    margin-bottom: 1.2rem;
    line-height: 1.6;
}

.insight-pill {
    display: inline-block;
    font-size: 0.8rem;
    padding: 5px 13px;
    border-radius: 20px;
    margin: 4px 4px 4px 0;
}

.pill-green { background: #E1F5EE; color: #085041; }
.pill-blue  { background: #E6F1FB; color: #042C53; }
.pill-amber { background: #FAEEDA; color: #633806; }

.divider {
    height: 0.5px;
    background: #e8e8e8;
    margin: 1.2rem 0;
}

.step-progress {
    display: flex;
    gap: 6px;
    justify-content: center;
    margin-bottom: 2rem;
}

.step-pip {
    width: 32px;
    height: 4px;
    border-radius: 2px;
}

.stButton > button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
}

.stButton > button[kind="primary"] {
    background-color: #1D9E75 !important;
    border-color: #1D9E75 !important;
    color: white !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: #0F6E56 !important;
    border-color: #0F6E56 !important;
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Data ───────────────────────────────────────────────────────────────────────
REGIONS = {
    "🌍 Western Europe": "UK, Germany, France, Nordics, Netherlands...",
    "🌍 Eastern Europe": "Bulgaria, Romania, Poland, Czech Republic, Balkans...",
    "🌎 North America": "USA, Canada",
    "🌎 Latin America": "Brazil, Mexico, Argentina, Colombia...",
    "🌏 Asia & Pacific": "India, Southeast Asia, Japan, South Korea, Australia...",
    "🌍 Africa & Middle East": "Nigeria, Kenya, Egypt, UAE, South Africa...",
}

BUDGETS = {
    "◦  Little to nothing": ("none", "I need free or near-free paths only"),
    "◦◦  Limited budget": ("low", "A few hundred per year at most"),
    "◦◦◦  Moderate budget": ("mid", "Community college / part-time course range"),
    "◦◦◦◦  Full university budget": ("full", "Can consider full degree programmes"),
}

INTERESTS = [
    "Technology & coding", "Design & creativity", "Science & research",
    "People & society", "Business & entrepreneurship", "Health & medicine",
    "Environment & climate", "Arts & storytelling", "Education & teaching",
    "Law & justice", "Finance & economics", "Agriculture & food",
    "Engineering & making", "Language & communication", "Maths & logic",
]

FORMATS = {
    "Fully online": "Self-paced, remote, from anywhere in the world",
    "Mix of both": "Some online flexibility, some in-person connection",
    "On campus": "Traditional university or college environment",
    "Work & learn": "Apprenticeship, bootcamp, or earn-while-you-learn",
}

AI_RISK_DATA = [
    ("Data entry & clerical work", 92, "#E24B4A", "Already largely automated"),
    ("Basic customer service / call centres", 85, "#E24B4A", "Chatbots replacing ~70% of tasks"),
    ("Repetitive legal & financial analysis", 78, "#E24B4A", "AI handles research drafts now"),
    ("Basic accounting & bookkeeping", 74, "#E24B4A", "AI handles most routine entries"),
    ("Journalism & content writing", 45, "#BA7517", "AI drafts, humans curate & judge"),
    ("Medical imaging & diagnostics", 55, "#BA7517", "AI assists, doctors decide"),
    ("Teaching & education", 22, "#1D9E75", "Personalisation tool, not replacement"),
    ("Creative direction & strategy", 12, "#1D9E75", "AI executes, humans still direct"),
    ("Skilled trades (plumbing, electrical)", 8, "#1D9E75", "Physical dexterity + judgment needed"),
    ("Psychotherapy & social work", 6, "#1D9E75", "Human trust is core to the work"),
]

PATH_DB = {
    "Technology & coding": {
        "paths": [
            {
                "title": "Software engineering / full-stack development",
                "why": "One of the fastest routes into well-paid remote work globally. Even as AI writes code, humans are needed to architect systems, review AI output, and bridge business logic with real-world needs.",
                "badges": [("AI-resilient", "green"), ("Remote-friendly", "blue"), ("High demand", "green")],
                "resources": [
                    ("The Odin Project", "Free · Full-stack web curriculum", "https://www.theodinproject.com"),
                    ("CS50 by Harvard", "Free · Computer science foundations", "https://cs50.harvard.edu"),
                    ("freeCodeCamp", "Free · Project-based web development", "https://www.freecodecamp.org"),
                    ("The Missing CS Semester (MIT)", "Free · Tools every developer needs", "https://missing.csail.mit.edu"),
                ]
            },
            {
                "title": "AI / machine learning engineering",
                "why": "Understanding how AI systems work makes you the person who builds and governs them — not the one they replace. This decade needs people who can evaluate, fine-tune, and audit AI tools critically.",
                "badges": [("Field of the decade", "blue"), ("High runway", "green"), ("Maths needed", "amber")],
                "resources": [
                    ("fast.ai", "Free · Practical deep learning from scratch", "https://www.fast.ai"),
                    ("Kaggle Learn", "Free · Bite-sized ML courses with datasets", "https://www.kaggle.com/learn"),
                    ("DeepLearning.AI short courses", "Free/low cost · Andrew Ng's curated AI courses", "https://www.deeplearning.ai"),
                ]
            }
        ],
        "ai_note": "Junior coding tasks — boilerplate, CRUD apps, basic scripts — are increasingly handled by AI. The real competitive edge is systems thinking, debugging AI output, and domain expertise layered on top of code.",
        "ai_opportunity": "AI tools like GitHub Copilot and Cursor dramatically accelerate what one developer can ship. Learning to direct AI effectively is itself a high-value skill."
    },
    "Design & creativity": {
        "paths": [
            {
                "title": "UX / product design",
                "why": "AI generates visuals but struggles with empathy-driven design decisions. UX designers who understand human behaviour and can work alongside AI tools are in growing demand across every industry.",
                "badges": [("AI-collaborative", "blue"), ("Portfolio-driven", "gray"), ("Remote-friendly", "blue")],
                "resources": [
                    ("Google UX Design Certificate", "Low cost · Coursera · ~6 months", "https://www.coursera.org/google-certificates"),
                    ("Shift Nudge", "Paid · Deep UI design principles from practitioners", "https://shiftnudge.com"),
                    ("Laws of UX (free)", "Free · Essential principles reference", "https://lawsofux.com"),
                ]
            },
            {
                "title": "Creative & art direction",
                "why": "AI generates images at scale, but someone with taste and a point of view still decides what's made, why, and for whom. Cultural context, narrative, and creative judgment remain hard to automate.",
                "badges": [("Taste-driven", "amber"), ("Portfolio essential", "gray"), ("High ceiling", "green")],
                "resources": [
                    ("Domestika", "Low cost · Creative skills from working practitioners", "https://www.domestika.org"),
                    ("Futur Academy", "Paid · Business of creativity and design thinking", "https://thefutur.com"),
                ]
            }
        ],
        "ai_note": "Generative AI (Midjourney, Adobe Firefly, Stable Diffusion) is disrupting stock photography and basic graphic work rapidly. Creative roles with strategic, narrative, and cultural judgment are much more resilient.",
        "ai_opportunity": "Designers who become fluent in AI generation tools can produce work 10x faster — making them more competitive, not less relevant."
    },
    "Health & medicine": {
        "paths": [
            {
                "title": "Nursing & allied health professions",
                "why": "Hands-on caregiving requires physical presence, emotional attunement, and clinical judgment that AI cannot replicate. There is a global shortage of nurses — making this one of the most secure career paths available.",
                "badges": [("Very AI-resilient", "green"), ("Global demand", "green"), ("Regulated entry", "amber")],
                "resources": [
                    ("Khan Academy Health & Medicine", "Free · Foundation biological sciences", "https://www.khanacademy.org/science/health-and-medicine"),
                    ("Coursera Healthcare courses", "Free to audit · Various universities", "https://www.coursera.org"),
                ]
            },
            {
                "title": "Mental health & psychology",
                "why": "Demand for mental health support is growing globally as awareness increases. The therapeutic relationship — human trust and vulnerability — is specifically what AI cannot replicate at any meaningful scale.",
                "badges": [("Extremely AI-resilient", "green"), ("Growing urgently", "green"), ("Long training path", "amber")],
                "resources": [
                    ("Open University Psychology", "Flexible, online · UK-based, internationally recognised", "https://www.open.ac.uk"),
                    ("Coursera: Science of Well-Being (Yale)", "Free · Evidence-based psychology foundations", "https://www.coursera.org/learn/the-science-of-well-being"),
                ]
            }
        ],
        "ai_note": "AI is transforming medical imaging and drug discovery significantly. But direct patient care, mental health, surgical skill, and complex clinical judgment remain deeply human for the foreseeable future.",
        "ai_opportunity": "Healthcare professionals who understand AI diagnostic tools will be more effective — not replaced by them. Digital health literacy is becoming a core clinical skill."
    },
    "Environment & climate": {
        "paths": [
            {
                "title": "Environmental engineering & renewable energy",
                "why": "The energy transition is one of the largest infrastructure projects in human history. Engineers, project managers, and policy experts in this space are urgently and chronically needed.",
                "badges": [("Urgently needed", "green"), ("Growing fast", "green"), ("Global opportunities", "blue")],
                "resources": [
                    ("edX Climate & Sustainability courses", "Free to audit · MIT, TU Delft, others", "https://www.edx.org"),
                    ("Climatebase", "Free · Climate career guidance and job board", "https://climatebase.org"),
                    ("Solar Energy Engineering (edX)", "Free to audit · DTU Denmark", "https://www.edx.org"),
                ]
            },
            {
                "title": "Climate policy & environmental communication",
                "why": "Technical solutions to climate change exist — the bottleneck is political will and public understanding. People who can communicate complex environmental issues clearly are increasingly valuable.",
                "badges": [("High impact", "green"), ("Interdisciplinary", "blue"), ("Growing field", "green")],
                "resources": [
                    ("Climate Reality Leadership Corps", "Free · Al Gore's climate training programme", "https://www.climaterealityproject.org"),
                ]
            }
        ],
        "ai_note": "Climate data analysis and modelling will be heavily AI-assisted, dramatically accelerating research. But physical infrastructure work, community engagement, policy advocacy, and field science are distinctly human.",
        "ai_opportunity": "AI is accelerating climate modelling and clean energy optimisation dramatically. Understanding these tools gives environmental scientists a massive productivity edge."
    },
    "Business & entrepreneurship": {
        "paths": [
            {
                "title": "Entrepreneurship & product thinking",
                "why": "Building something new — understanding a real problem, testing solutions, shipping to users — is hard to automate because it requires risk tolerance, context reading, and constant adaptation to the unexpected.",
                "badges": [("Self-directed", "amber"), ("AI can accelerate you", "blue"), ("High variance", "amber")],
                "resources": [
                    ("Y Combinator Startup School", "Free · Founders curriculum from YC partners", "https://www.startupschool.org"),
                    ("Lean Startup methodology", "Low cost / free summaries · Core build-measure-learn loop", "https://theleanstartup.com"),
                    ("Indie Hackers community", "Free · Learn from bootstrapped founders", "https://www.indiehackers.com"),
                ]
            },
            {
                "title": "Operations & supply chain management",
                "why": "Every product or service needs people who understand how to make things actually work at scale — logistics, procurement, quality, process. AI optimises supply chains but humans still navigate disruption.",
                "badges": [("Stable demand", "green"), ("Cross-industry", "blue"), ("AI-augmented", "amber")],
                "resources": [
                    ("Coursera: Supply Chain Specialisation", "Free to audit · Rutgers University", "https://www.coursera.org"),
                    ("APICS certifications", "Paid · Industry-recognised supply chain credentials", "https://www.ascm.org"),
                ]
            }
        ],
        "ai_note": "AI dramatically lowers the cost of building software products — one person with AI tools can now do what previously required a team of five. This is a massive opportunity for entrepreneurial thinkers willing to move fast.",
        "ai_opportunity": "AI is a co-founder that never sleeps. Entrepreneurs who learn to direct AI tools effectively have an unprecedented productivity advantage over those who don't."
    },
    "Science & research": {
        "paths": [
            {
                "title": "Data science & computational research",
                "why": "Humans who can formulate sharp research questions and interpret data in context remain essential — even as AI automates analysis. The person who knows what question to ask is still irreplaceable.",
                "badges": [("AI-collaborative", "blue"), ("High demand", "green"), ("Maths foundations needed", "amber")],
                "resources": [
                    ("DataCamp", "Low cost · Python, R, SQL structured tracks", "https://www.datacamp.com"),
                    ("Kaggle", "Free · Competitions, datasets, notebooks", "https://www.kaggle.com"),
                    ("StatQuest (YouTube)", "Free · Statistics and ML explained clearly", "https://www.youtube.com/@statquest"),
                ]
            },
            {
                "title": "Biotechnology & life sciences",
                "why": "AI is accelerating drug discovery and protein folding research (AlphaFold). Life scientists who can work at the interface of biology and computation will define the next medical era.",
                "badges": [("Long training", "amber"), ("High impact", "green"), ("AI-supercharged", "blue")],
                "resources": [
                    ("MIT OpenCourseWare Biology", "Free · Full MIT undergraduate biology curriculum", "https://ocw.mit.edu/courses/7-01sc-fundamentals-of-biology-fall-2011/"),
                    ("Rosalind (bioinformatics problems)", "Free · Learn bioinformatics by solving problems", "https://rosalind.info"),
                ]
            }
        ],
        "ai_note": "AI is accelerating scientific discovery at a historic pace — AlphaFold solved protein folding, AI models are screening drug candidates in days instead of years. This raises the ceiling for researchers enormously.",
        "ai_opportunity": "Scientists who are fluent in AI tools (machine learning, large-scale data analysis) will be able to run experiments and test hypotheses that were previously impossible."
    },
    "Education & teaching": {
        "paths": [
            {
                "title": "Teaching & learning design",
                "why": "AI tutors will supplement classrooms — not replace the skilled teacher who builds relationships, reads the room, and responds to what a student actually needs in the moment.",
                "badges": [("Very AI-resilient", "green"), ("Stable demand", "green"), ("Meaningful work", "blue")],
                "resources": [
                    ("Coursera: Learning How to Learn", "Free · Evidence-based study science (world's most enrolled MOOC)", "https://www.coursera.org/learn/learning-how-to-learn"),
                    ("Teach For All network", "Free · Global teaching fellowships and training", "https://teachforall.org"),
                ]
            },
            {
                "title": "Educational technology & instructional design",
                "why": "The e-learning market is growing rapidly. People who understand both pedagogy and technology — how to design learning that actually works online — are in growing demand at companies, NGOs, and governments.",
                "badges": [("Growing field", "green"), ("AI-augmented", "blue"), ("Remote-friendly", "blue")],
                "resources": [
                    ("ATD (Association for Talent Development)", "Low cost · Instructional design resources", "https://www.td.org"),
                    ("EdSurge", "Free · News and resources on edtech", "https://www.edsurge.com"),
                ]
            }
        ],
        "ai_note": "Personalised AI tutoring (Khan Academy's Khanmigo, Duolingo AI) is transforming self-directed learning and will personalise education at scale. But classroom teaching, mentorship, and social-emotional learning remain deeply human.",
        "ai_opportunity": "Teachers who learn to use AI tutoring tools effectively will be dramatically more impactful — personalising at a scale that was previously impossible."
    },
    "Arts & storytelling": {
        "paths": [
            {
                "title": "Screenwriting, narrative design & game writing",
                "why": "AI can generate text but not a coherent, emotionally resonant story that understands human experience. Writers who understand structure, character, and cultural nuance are still the creative core of media.",
                "badges": [("Judgment-dependent", "green"), ("Portfolio-driven", "gray"), ("Evolving field", "amber")],
                "resources": [
                    ("John August's Screenwriting Lessons", "Free · Practical craft for film and TV", "https://johnaugust.com"),
                    ("Scriptnotes Podcast", "Free · Industry-level screenwriting discussion", "https://johnaugust.com/scriptnotes"),
                ]
            }
        ],
        "ai_note": "AI is generating enormous volumes of generic content. This is actually raising the value of distinctly human storytelling — authentic voice, lived experience, and cultural depth that AI cannot fake.",
        "ai_opportunity": "Writers who use AI as a drafting and research tool can iterate faster and spend more time on the high-craft decisions that make work memorable."
    },
    "People & society": {
        "paths": [
            {
                "title": "Social work & community development",
                "why": "Humans navigating crisis, poverty, trauma, or systemic injustice need other humans — not chatbots. Social workers operate in the irreplaceable space of trust, advocacy, and human dignity.",
                "badges": [("Very AI-resilient", "green"), ("High meaning", "green"), ("Often underpaid", "amber")],
                "resources": [
                    ("NASW (Social Work resources)", "Free · Career guidance and learning", "https://www.socialworkers.org"),
                    ("Coursera: Social Work courses", "Free to audit · Various universities", "https://www.coursera.org"),
                ]
            },
            {
                "title": "Sociology, anthropology & policy research",
                "why": "Understanding why societies work the way they do — and how to change them — requires deep qualitative insight that AI cannot generate. Policy researchers shape the decisions that affect millions.",
                "badges": [("Interdisciplinary", "blue"), ("High impact", "green"), ("Research-focused", "gray")],
                "resources": [
                    ("Our World in Data", "Free · Data-driven social research and writing", "https://ourworldindata.org"),
                    ("80,000 Hours career guide", "Free · Impact-focused career research", "https://80000hours.org"),
                ]
            }
        ],
        "ai_note": "AI can analyse social data at scale but cannot understand cultural nuance, navigate ethical complexity, or build the human relationships that community change requires.",
        "ai_opportunity": "Social researchers who use AI for large-scale data analysis can draw insights from datasets that would previously have taken years to process."
    },
    "Finance & economics": {
        "paths": [
            {
                "title": "Financial analysis & risk management",
                "why": "AI is automating routine financial analysis fast. The resilient roles are those involving judgment, relationship, regulatory navigation, and strategic interpretation — not data crunching alone.",
                "badges": [("Partially disrupted", "amber"), ("High earning", "green"), ("Judgment essential", "blue")],
                "resources": [
                    ("CFA Institute free resources", "Free · Finance foundations and ethics", "https://www.cfainstitute.org"),
                    ("Investopedia Academy", "Low cost · Practical financial literacy", "https://www.investopedia.com/investopedia-academy-4687859"),
                    ("Khan Academy Finance", "Free · Economics and personal finance", "https://www.khanacademy.org/economics-finance-domain"),
                ]
            }
        ],
        "ai_note": "Basic accounting, data entry, and routine financial modelling are being automated rapidly. The high-value future of finance is in strategic advising, risk judgment, client relationships, and regulatory expertise.",
        "ai_opportunity": "Financial analysts who use AI modelling tools can run scenarios and stress tests that would previously have taken a full team — a significant productivity advantage."
    },
    "Engineering & making": {
        "paths": [
            {
                "title": "Electrical & mechanical engineering",
                "why": "The physical world still needs engineers who can design, test, and fix real systems. Automation and robotics are creating more engineering work, not less — someone has to design the machines.",
                "badges": [("AI-resilient", "green"), ("Strong demand", "green"), ("Hands-on", "blue")],
                "resources": [
                    ("MIT OpenCourseWare Engineering", "Free · Full MIT engineering curricula", "https://ocw.mit.edu"),
                    ("Coursera Engineering courses", "Free to audit · Various top universities", "https://www.coursera.org"),
                ]
            },
            {
                "title": "Skilled trades (electrician, plumber, HVAC)",
                "why": "These are among the most AI-resistant careers that exist — they require physical dexterity, real-world problem-solving, and showing up in person. And they pay well, with genuine shortages globally.",
                "badges": [("Extremely AI-resilient", "green"), ("Global shortage", "green"), ("Apprenticeship path", "blue")],
                "resources": [
                    ("SkillsUSA", "Free · Vocational trade training resources (US)", "https://www.skillsusa.org"),
                    ("City & Guilds", "Low cost · UK vocational qualifications", "https://www.cityandguilds.com"),
                ]
            }
        ],
        "ai_note": "AI is automating engineering design and simulation tasks. But physical installation, troubleshooting on-site, and building/maintaining real infrastructure require humans — often urgently.",
        "ai_opportunity": "Engineers who use AI-powered design tools (CAD with AI, simulation AI) can prototype and test ideas dramatically faster."
    },
    "Law & justice": {
        "paths": [
            {
                "title": "Law — human rights, policy & advocacy",
                "why": "Legal research is being rapidly automated. But courtroom advocacy, ethical judgment, client relationships, and policy interpretation require human understanding that AI cannot replicate reliably.",
                "badges": [("Partially disrupted", "amber"), ("High impact", "green"), ("Long training", "amber")],
                "resources": [
                    ("Khan Academy Law & Government", "Free · Foundations of law and civics", "https://www.khanacademy.org/humanities/us-government-and-civics"),
                    ("Coursera: Introduction to Law", "Free to audit · Multiple law schools", "https://www.coursera.org"),
                    ("Law Without Walls (LWOW)", "Free/low cost · Global innovation in legal education", "https://www.lawwithoutwalls.org"),
                ]
            }
        ],
        "ai_note": "AI is automating contract review, legal research, and document drafting fast. Junior legal roles doing routine document work are most at risk. Advocacy, court work, and complex judgment are much more resilient.",
        "ai_opportunity": "Lawyers who use AI research tools (Westlaw AI, Harvey) can prepare cases in a fraction of the time — a major competitive advantage."
    },
    "Language & communication": {
        "paths": [
            {
                "title": "Translation & intercultural communication",
                "why": "Machine translation is improving rapidly for common languages, but nuance, cultural subtext, specialised domains (legal, medical, literary), and less-resourced languages still require human expertise.",
                "badges": [("Partially disrupted", "amber"), ("Specialism matters", "blue"), ("High value niches", "green")],
                "resources": [
                    ("Coursera: Translation Studies", "Free to audit · Various universities", "https://www.coursera.org"),
                    ("ProZ.com community", "Free · Largest professional translator network", "https://www.proz.com"),
                ]
            },
            {
                "title": "Journalism & investigative reporting",
                "why": "AI can generate generic content but cannot cultivate sources, investigate wrongdoing, or bring lived experience to reporting on human events. Investigative journalism is increasingly differentiated from commodity content.",
                "badges": [("Judgment-dependent", "green"), ("Evolving fast", "amber"), ("High importance", "green")],
                "resources": [
                    ("GIJN (Global Investigative Journalism Network)", "Free · Resources for investigative journalists worldwide", "https://gijn.org"),
                    ("Bellingcat open-source investigation guide", "Free · OSINT and open-source research skills", "https://www.bellingcat.com"),
                ]
            }
        ],
        "ai_note": "AI translation is disrupting high-volume, low-complexity translation work significantly. But literary translation, specialised domains, and languages with less AI training data remain strong niches for human experts.",
        "ai_opportunity": "Translators and journalists who are fluent in AI tools can handle research and first drafts faster, focusing human attention on the nuanced, high-value work."
    },
    "Maths & logic": {
        "paths": [
            {
                "title": "Mathematics & statistics",
                "why": "Mathematical thinking — formulating problems, constructing proofs, designing statistical tests — remains a core human cognitive skill. Mathematicians are the people who build the tools AI runs on.",
                "badges": [("Foundational", "blue"), ("High ceiling", "green"), ("AI-adjacent", "blue")],
                "resources": [
                    ("3Blue1Brown (YouTube)", "Free · Beautiful visual mathematics", "https://www.youtube.com/@3blue1brown"),
                    ("Khan Academy Maths", "Free · Full K-12 through university curriculum", "https://www.khanacademy.org/math"),
                    ("Art of Problem Solving", "Low cost · Competition maths and deep problem solving", "https://artofproblemsolving.com"),
                ]
            }
        ],
        "ai_note": "AI is beginning to assist in mathematical proof-checking and conjecture generation (e.g. AlphaGeometry). But formulating the right mathematical question and interpreting results remains deeply human.",
        "ai_opportunity": "Mathematicians with computational skills are in exceptional demand for AI development, quantitative finance, cryptography, and scientific research."
    },
    "Agriculture & food": {
        "paths": [
            {
                "title": "Sustainable agriculture & food systems",
                "why": "The world needs to feed 10 billion people while reversing environmental damage. Agronomists, food scientists, and sustainable farming specialists are at the centre of one of the defining challenges of this century.",
                "badges": [("Essential work", "green"), ("Growing urgency", "green"), ("Hands-on", "blue")],
                "resources": [
                    ("Coursera: Sustainable Food Systems", "Free to audit · Various universities", "https://www.coursera.org"),
                    ("FAO eLearning Academy", "Free · Global food and agriculture courses", "https://elearning.fao.org"),
                ]
            }
        ],
        "ai_note": "AI is transforming precision agriculture — crop monitoring, yield prediction, pest detection. But field work, community farming knowledge, and food systems design remain human-led.",
        "ai_opportunity": "Farmers and agronomists who use AI-powered monitoring tools can optimise yields and reduce chemical use significantly — a competitive and environmental advantage."
    },
}

DEFAULT_PATH = {
    "paths": [
        {
            "title": "Critical thinking & communication",
            "why": "Whatever field you enter, the ability to evaluate arguments clearly, write well, and navigate complexity will be amplified by AI tools — not replaced by them. It is the meta-skill of the AI era.",
            "badges": [("Foundation skill", "blue"), ("Cross-field value", "green"), ("Always valuable", "green")],
            "resources": [
                ("Writing Well — Julian Shapiro", "Free · Clear, honest writing guide", "https://www.julian.com/guide/write/intro"),
                ("Coursera: Learning How to Learn", "Free · Evidence-based study science", "https://www.coursera.org/learn/learning-how-to-learn"),
                ("80,000 Hours career guide", "Free · How to have a meaningful, impactful career", "https://80000hours.org"),
            ]
        }
    ],
    "ai_note": "Whatever you choose, the core human advantage in an AI world is judgment, creativity, and the ability to ask good questions — not just execute tasks efficiently.",
    "ai_opportunity": "People who become fluent AI users — regardless of their field — will be dramatically more productive than those who don't. This fluency is learnable now, for free."
}

BUDGET_NOTES = {
    "none": "Since your budget is close to zero, the resources below are entirely free. The good news: many of today's most in-demand skills can genuinely be learned for free — from Harvard's CS50 to MIT OpenCourseWare to Kaggle. What you trade is structure and a credential; what you gain is knowledge and a portfolio.",
    "low": "With a limited budget, you have access to low-cost certifications, Coursera financial aid, and community college pricing. Many employers now value demonstrated skills and portfolio work over expensive degrees — especially in tech, design, and data.",
    "mid": "With a moderate budget you can access professional certificates (Google, IBM, AWS), part-time programmes, and community college courses. These can be a more affordable and often more practical alternative to a full degree.",
    "full": "With full university budget, you have the widest range of options — including traditional degrees, which still provide strong networks and structured learning paths. Consider whether the full degree is the right fit for your specific interest, or whether a targeted professional programme offers better value."
}

FORMAT_NOTES = {
    "Fully online": "Online learning gives you access to the world's best courses regardless of where you are. The key challenge is self-discipline — structure your own schedule and find communities (Discord servers, study groups) to stay motivated.",
    "Mix of both": "A hybrid approach gives you flexibility while maintaining some in-person connection. Many community colleges and universities now offer this model — look for 'blended' or 'hybrid' programmes in your area.",
    "On campus": "Campus-based study gives you access to facilities, faculty, peers, and the serendipity of being around people with shared curiosity. The network you build during university is often as valuable as the qualification itself.",
    "Work & learn": "Apprenticeships and bootcamps offer an earn-while-you-learn model with direct employer links. In some countries (UK, Germany, Australia) apprenticeships are formalised and well-respected. Bootcamps are shorter but intense — research completion rates and job placement carefully.",
}

FUTURE_PROOF_SKILLS = [
    ("Systems thinking", "green"), ("Emotional intelligence", "green"),
    ("Critical judgment", "green"), ("AI tool fluency", "blue"),
    ("Prompt engineering", "blue"), ("Data literacy", "blue"),
    ("Creative direction", "amber"), ("Ethical reasoning", "amber"),
    ("Cross-disciplinary thinking", "amber"), ("Physical / dexterous skills", "green"),
    ("Intercultural communication", "blue"), ("Complex problem framing", "green"),
]


# ── Session state ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "step": 0,
        "region": None,
        "budget_key": None,
        "budget_id": None,
        "interests": [],
        "format": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

TOTAL_STEPS = 5


# ── Progress bar ───────────────────────────────────────────────────────────────
def render_progress():
    cols = st.columns(TOTAL_STEPS)
    for i, col in enumerate(cols):
        if i < st.session_state.step:
            col.markdown(f'<div style="height:4px;background:#0F6E56;border-radius:2px;opacity:0.4;"></div>', unsafe_allow_html=True)
        elif i == st.session_state.step:
            col.markdown(f'<div style="height:4px;background:#1D9E75;border-radius:2px;"></div>', unsafe_allow_html=True)
        else:
            col.markdown(f'<div style="height:4px;background:#e0e0e0;border-radius:2px;"></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ── Badge helper ───────────────────────────────────────────────────────────────
def badges_html(badge_list):
    html = ""
    for text, typ in badge_list:
        html += f'<span class="badge badge-{typ}">{text}</span>'
    return html


# ── Risk bar helper ────────────────────────────────────────────────────────────
def risk_bar_html(label, pct, color, note):
    return f"""
    <div class="risk-bar-container">
      <div class="risk-label">{label}</div>
      <div class="risk-track">
        <div style="width:{pct}%;height:6px;background:{color};border-radius:3px;"></div>
      </div>
      <div class="risk-pct">{pct}%</div>
    </div>
    <div style="font-size:0.75rem;color:#999;margin-bottom:10px;margin-left:210px;">{note}</div>
    """


# ── STEP 0: Region ─────────────────────────────────────────────────────────────
def step_region():
    st.markdown('<div class="section-label">Step 1 of 5</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Where in the world are you?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">This affects which study options, costs, and job markets are most relevant to you.</div>', unsafe_allow_html=True)

    options = ["— Select your region —"] + list(REGIONS.keys())
    current_index = 0
    if st.session_state.region and st.session_state.region in options:
        current_index = options.index(st.session_state.region)

    choice = st.selectbox("Region", options, index=current_index, label_visibility="collapsed")

    if choice != "— Select your region —":
        st.session_state.region = choice
        st.markdown(f'<div style="font-size:0.85rem;color:#555;margin-top:6px;">{REGIONS[choice]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.region and choice != "— Select your region —":
        if st.button("Next →", type="primary", key="next0"):
            st.session_state.step = 1
            st.rerun()
    else:
        st.info("Select a region to continue.")


# ── STEP 1: Budget ─────────────────────────────────────────────────────────────
def step_budget():
    st.markdown('<div class="section-label">Step 2 of 5</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">What\'s your financial situation?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Be honest — this shapes realistic paths. Great options exist at every level, including free ones that are genuinely excellent.</div>', unsafe_allow_html=True)

    budget_list = list(BUDGETS.items())
    cols = st.columns(2)
    for i, (label, (bid, sub)) in enumerate(budget_list):
        col = cols[i % 2]
        with col:
            selected = st.session_state.budget_key == label
            border = "border: 1.5px solid #1D9E75; background: #E1F5EE;" if selected else "border: 0.5px solid #e0e0e0; background: white;"
            st.markdown(f"""
                <div style="border-radius:12px;padding:14px 16px;margin-bottom:10px;{border}">
                    <div style="font-size:0.85rem;font-weight:500;letter-spacing:0.1em;margin-bottom:4px;">{label}</div>
                    <div style="font-size:0.78rem;color:#888;">{sub}</div>
                </div>""", unsafe_allow_html=True)
            if st.button("Select", key=f"budget_{i}"):
                st.session_state.budget_key = label
                st.session_state.budget_id = bid
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back", key="back1"):
            st.session_state.step = 0
            st.rerun()
    with col2:
        if st.session_state.budget_key:
            st.success(f"Selected: **{st.session_state.budget_key}**")
            if st.button("Next →", type="primary", key="next1"):
                st.session_state.step = 2
                st.rerun()
        else:
            st.info("Select a budget level to continue.")


# ── STEP 2: Interests ──────────────────────────────────────────────────────────
def step_interests():
    st.markdown('<div class="section-label">Step 3 of 5</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">What pulls your attention?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Pick everything that genuinely interests you — not what sounds impressive or safe. You can choose several. This is about what you actually want to learn.</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, interest in enumerate(INTERESTS):
        col = cols[i % 3]
        with col:
            checked = interest in st.session_state.interests
            if st.checkbox(interest, value=checked, key=f"interest_{i}"):
                if interest not in st.session_state.interests:
                    st.session_state.interests.append(interest)
            else:
                if interest in st.session_state.interests:
                    st.session_state.interests.remove(interest)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back", key="back2"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.session_state.interests:
            st.success(f"Selected {len(st.session_state.interests)} interest(s): {', '.join(st.session_state.interests[:3])}{'...' if len(st.session_state.interests) > 3 else ''}")
            if st.button("Next →", type="primary", key="next2"):
                st.session_state.step = 3
                st.rerun()
        else:
            st.info("Select at least one interest to continue.")


# ── STEP 3: Format ─────────────────────────────────────────────────────────────
def step_format():
    st.markdown('<div class="section-label">Step 4 of 5</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">How do you prefer to learn?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">There is no wrong answer. Knowing your learning style helps narrow what will actually stick and suit your life.</div>', unsafe_allow_html=True)

    format_list = list(FORMATS.items())
    cols = st.columns(2)
    for i, (name, sub) in enumerate(format_list):
        col = cols[i % 2]
        with col:
            selected = st.session_state.format == name
            border = "border: 1.5px solid #1D9E75; background: #E1F5EE;" if selected else "border: 0.5px solid #e0e0e0; background: white;"
            st.markdown(f"""
                <div style="border-radius:12px;padding:14px 16px;margin-bottom:10px;{border}">
                    <div style="font-weight:500;font-size:0.9rem;margin-bottom:2px;">{name}</div>
                    <div style="font-size:0.78rem;color:#888;">{sub}</div>
                </div>""", unsafe_allow_html=True)
            if st.button("Select", key=f"format_{i}"):
                st.session_state.format = name
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back", key="back3"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.session_state.format:
            st.success(f"Selected: **{st.session_state.format}**")
            if st.button("See my personalised guide →", type="primary", key="next3"):
                st.session_state.step = 4
                st.rerun()
        else:
            st.info("Select a learning format to continue.")


# ── STEP 4: Results ────────────────────────────────────────────────────────────
def step_results():
    interests = st.session_state.interests
    budget_id = st.session_state.budget_id
    fmt = st.session_state.format
    region = st.session_state.region

    st.markdown('<div class="section-label">Your personalised guide</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-heading">Here\'s what makes sense for you</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-desc">Based on your interests, location, budget, and how you learn — plus an honest look at where the job market is heading.</div>', unsafe_allow_html=True)

    # Summary pills
    st.markdown(f"""
    <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:1.5rem;">
        <span class="insight-pill pill-blue">📍 {region}</span>
        <span class="insight-pill pill-amber">💰 {st.session_state.budget_key.strip()}</span>
        <span class="insight-pill pill-green">🎓 {fmt}</span>
    </div>
    """, unsafe_allow_html=True)

    # Budget note
    note = BUDGET_NOTES.get(budget_id, "")
    st.markdown(f'<div class="alert-info">{note}</div>', unsafe_allow_html=True)

    # Format note
    fnote = FORMAT_NOTES.get(fmt, "")
    if fnote:
        st.markdown(f'<div class="alert-warn">{fnote}</div>', unsafe_allow_html=True)

    # ── Learning paths ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Your learning paths")

    relevant_interests = [i for i in interests if i in PATH_DB]
    shown_paths = 0
    max_paths = 4

    if not relevant_interests:
        data = DEFAULT_PATH
        for path in data["paths"][:2]:
            _render_path_card(path)
            shown_paths += 1
    else:
        for interest in relevant_interests:
            if shown_paths >= max_paths:
                break
            data = PATH_DB[interest]
            st.markdown(f"#### {interest}")
            for path in data["paths"][:2]:
                if shown_paths >= max_paths:
                    break
                _render_path_card(path)
                shown_paths += 1

    # ── AI disruption section ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### The AI displacement picture — honestly")
    st.markdown("""
    These are estimated automation risk levels for common job categories, based on research from McKinsey Global Institute, Oxford University, and the World Economic Forum.
    The percentage reflects estimated share of *tasks* that are automatable by AI by 2030–2035 — not a prediction that entire jobs disappear, but where change is fastest and most disruptive.
    """)

    risk_html = ""
    for label, pct, color, note in AI_RISK_DATA:
        risk_html += risk_bar_html(label, pct, color, note)

    st.markdown(risk_html, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.8rem;color:#999;margin-top:6px;line-height:1.6;">
    Sources: McKinsey Global Institute "The Future of Work" (2023), Oxford Martin Programme "The Future of Employment" (Frey & Osborne), WEF "Future of Jobs Report" 2023.
    Percentages are estimates and subject to ongoing revision as AI capabilities evolve.
    </div>
    """, unsafe_allow_html=True)

    # ── AI notes for chosen interests ──────────────────────────────────────
    if relevant_interests:
        st.markdown("---")
        st.markdown("### How AI is changing your specific fields")
        for interest in relevant_interests[:3]:
            data = PATH_DB[interest]
            with st.expander(f"🔍 {interest} — AI impact"):
                st.markdown(f"**The risk:** {data['ai_note']}")
                st.markdown(f"**The opportunity:** {data['ai_opportunity']}")

    # ── Future-proof skills ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Skills that stay valuable in an AI world")
    st.markdown("""
    The pattern across all research: AI automates the *execution* of tasks. It does not yet replicate judgment about *which* tasks matter, *why*, or *for whom*.
    Pair deep curiosity in any field with these meta-skills — and you will be very hard to replace.
    """)

    pills_html = ""
    for skill, typ in FUTURE_PROOF_SKILLS:
        cls = f"pill-{typ}"
        pills_html += f'<span class="insight-pill {cls}">{skill}</span>'
    st.markdown(f'<div style="margin-bottom:1rem;">{pills_html}</div>', unsafe_allow_html=True)

    # ── Where to start this month ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### If you could start only one thing this month...")

    if budget_id in ("none", "low"):
        st.markdown("""
        **Start here, for free:**
        - **[CS50 (Harvard)](https://cs50.harvard.edu)** — If you have any interest in technology, this is the finest free introduction to computer science that exists. Hundreds of thousands of people have changed their careers with it.
        - **[Coursera: Learning How to Learn](https://www.coursera.org/learn/learning-how-to-learn)** — The world's most-enrolled online course. Learn how to learn effectively before you commit to any path.
        - **[Khan Academy](https://www.khanacademy.org)** — Fill any gaps in maths, science, or economics foundations. Completely free, surprisingly excellent.
        """)
    else:
        st.markdown("""
        **Strong starting points for your budget level:**
        - **[Google Career Certificates (Coursera)](https://www.coursera.org/google-certificates)** — Industry-recognised, affordable, 6 months, designed for career changers.
        - **[edX MicroMasters programmes](https://www.edx.org/micromasters)** — University-level credentials from MIT, Harvard, and more. Often free to audit, paid to certify.
        - **[Codecademy Pro](https://www.codecademy.com/pro)** — Structured technical skills with a clear curriculum if you're drawn to tech.
        """)

    st.info("💡 **The honest advice:** Before choosing a course or institution, spend 2 weeks genuinely exploring your top interest area through free content. Read articles, watch talks, try beginner tutorials. Make sure the curiosity is real — then invest in structured learning.")

    # ── Resources by format ─────────────────────────────────────────────────
    if fmt == "Fully online":
        st.markdown("---")
        st.markdown("### Best online learning platforms for your path")
        st.markdown("""
        | Platform | Best for | Cost |
        |---|---|---|
        | [Coursera](https://www.coursera.org) | University-level certificates, structured courses | Free to audit / ~$50/month |
        | [edX](https://www.edx.org) | University courses, MicroMasters, professional certs | Free to audit / paid cert |
        | [freeCodeCamp](https://www.freecodecamp.org) | Web development, Python, data analysis | Completely free |
        | [Khan Academy](https://www.khanacademy.org) | Maths, science, economics foundations | Completely free |
        | [fast.ai](https://www.fast.ai) | Machine learning and AI from scratch | Completely free |
        | [Kaggle](https://www.kaggle.com) | Data science, ML competitions, real datasets | Completely free |
        | [Domestika](https://www.domestika.org) | Creative skills from working practitioners | Low cost / frequent sales |
        | [Brilliant](https://www.brilliant.org) | Maths, logic, data science interactively | ~$10/month |
        """)

    # ── Restart ─────────────────────────────────────────────────────────────
    st.markdown("---")
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back", key="back4"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Start over", key="restart"):
            for k in ["step", "region", "budget_key", "budget_id", "interests", "format"]:
                st.session_state[k] = 0 if k == "step" else ([] if k == "interests" else None)
            st.rerun()


def _render_path_card(path):
    badges = badges_html(path["badges"])
    resources_html = ""
    for rname, rmeta, rurl in path.get("resources", []):
        resources_html += f"""
        <div class="resource-row">
            <div>
                <div class="res-name">{rname}</div>
                <div class="res-meta">{rmeta}</div>
            </div>
            <a href="{rurl}" target="_blank" style="font-size:0.82rem;color:#1D9E75;text-decoration:none;font-weight:500;">Visit →</a>
        </div>"""

    st.markdown(f"""
    <div class="path-card">
        <div class="path-title">{path['title']}</div>
        <div class="path-why">{path['why']}</div>
        <div style="margin-bottom:10px;">{badges}</div>
        {f'<div class="divider"></div><div style="margin-top:8px;">{resources_html}</div>' if resources_html else ''}
    </div>
    """, unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="hero-title">Find your <em>path</em></div>
    <div class="hero-sub">
        Not a university rankings list. A genuine guide to what's worth learning —<br>
        and an honest look at what the future of work actually looks like.
    </div>
    """, unsafe_allow_html=True)

    render_progress()

    step = st.session_state.step
    if step == 0:
        step_region()
    elif step == 1:
        step_budget()
    elif step == 2:
        step_interests()
    elif step == 3:
        step_format()
    elif step == 4:
        step_results()


main()
