"""Build the PolicyGuard project deck. One-off generator."""

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

NAVY = RGBColor(0x0F, 0x27, 0x44)
TEAL = RGBColor(0x1F, 0x7A, 0x6B)
GOLD = RGBColor(0xB8, 0x8A, 0x2E)
INK = RGBColor(0x1C, 0x24, 0x30)
MUTED = RGBColor(0x5C, 0x6B, 0x7A)
PAPER = RGBColor(0xF7, 0xF5, 0xF0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD9, 0xD3, 0xC7)
SOFT = RGBColor(0xD5, 0xDD, 0xE6)

W = Inches(13.333)
H = Inches(7.5)


def set_run(run, text, size, color, bold=False, font="Calibri"):
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.name = font


def add_rect(slide, l, t, w, h, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
    shape.shadow.inherit = False
    return shape


def add_text(slide, l, t, w, h, text, size, color, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    set_run(p.add_run(), text, size, color, bold)
    return box


def footer(slide, n, total):
    add_text(slide, Inches(0.55), Inches(7.12), Inches(9), Inches(0.28),
             "PolicyGuard  ·  Northwind Assurance", 11, MUTED)
    add_text(slide, Inches(11.2), Inches(7.12), Inches(1.6), Inches(0.28),
             f"{n}  /  {total}", 11, MUTED, align=PP_ALIGN.RIGHT)


def new_slide(prs, kicker, title):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, 0, 0, W, H, PAPER)
    add_rect(slide, 0, 0, Inches(0.12), H, TEAL)
    add_text(slide, Inches(0.55), Inches(0.28), Inches(12), Inches(0.28), kicker.upper(), 12, TEAL, True)
    add_text(slide, Inches(0.55), Inches(0.52), Inches(12.2), Inches(0.7), title, 28, NAVY, True)
    return slide


def card(slide, l, t, w, h, heading, body, accent=TEAL):
    add_rect(slide, Inches(l), Inches(t), Inches(w), Inches(h), WHITE, LINE)
    add_rect(slide, Inches(l), Inches(t), Inches(0.08), Inches(h), accent)
    add_text(slide, Inches(l + 0.22), Inches(t + 0.14), Inches(w - 0.38), Inches(0.4), heading, 16, NAVY, True)
    box = slide.shapes.add_textbox(Inches(l + 0.22), Inches(t + 0.56), Inches(w - 0.4), Inches(h - 0.7))
    tf = box.text_frame
    tf.word_wrap = True
    lines = body if isinstance(body, list) else [body]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(3)
        set_run(p.add_run(), line, 14, INK)


def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    prs.core_properties.title = "PolicyGuard"
    prs.core_properties.author = "Divyank Jain"
    prs.core_properties.subject = "A cite-or-refuse assistant for claims handlers"
    total = 15

    # 1 title
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(s, 0, 0, W, H, NAVY)
    add_rect(s, 0, 0, Inches(0.18), H, TEAL)
    add_text(s, Inches(0.7), Inches(1.85), Inches(11), Inches(0.35),
             "AI COMMANDOS CAPSTONE", 14, GOLD, True)
    add_text(s, Inches(0.7), Inches(2.3), Inches(11.5), Inches(0.9),
             "PolicyGuard", 54, WHITE, True)
    add_text(s, Inches(0.7), Inches(3.45), Inches(11), Inches(1.1),
             "A handler asks a cover question.\nThe draft cites the clause, or it refuses.", 22, SOFT)
    add_text(s, Inches(0.7), Inches(5.35), Inches(10), Inches(0.4),
             "Synthetic Northwind Assurance wordings.", 16, SOFT)
    add_text(s, Inches(0.7), Inches(5.8), Inches(10), Inches(0.4),
             "Not an insurance offer. Not a claim decision.", 16, GOLD, True)
    add_text(s, Inches(0.7), Inches(6.45), Inches(8), Inches(0.35),
             "Divyank Jain", 16, SOFT)

    # 2 problem
    s = new_slide(prs, "The job", "A wrong limit becomes a promise.")
    card(s, 0.55, 1.55, 4.0, 4.95, "Who is asking", [
        "A junior claims handler,",
        "mid-call, looking up cover,",
        "an exclusion, a waiting",
        "period, or the claims steps.",
        "",
        "A trainer uses the same",
        "questions in induction.",
    ])
    card(s, 4.7, 1.55, 4.0, 4.95, "What fails today", [
        "PDF search misses the",
        "paraphrase: cooling-off,",
        "a no-claim bonus, flood",
        "water in the engine.",
        "",
        "The handler then guesses,",
        "or asks a general chatbot.",
    ], GOLD)
    card(s, 8.85, 1.55, 3.95, 4.95, "The consequence", [
        "The chatbot invents a",
        "sum insured or a waiting",
        "period.",
        "",
        "That number is said to",
        "the customer, and it is",
        "not in the wording.",
    ], TEAL)
    footer(s, 2, total)

    # 3 scope
    s = new_slide(prs, "The proof of concept", "Four wordings. A draft beside the clause.")
    card(s, 0.55, 1.55, 6.05, 4.95, "In this build", [
        "English questions over four synthetic",
        "wordings: health cover, health",
        "exclusions, private car, and claims",
        "servicing.",
        "",
        "The screen shows a cite-or-refuse",
        "draft and the clause text it was",
        "allowed to use.",
        "",
        "Facts come from the wording.",
        "The model only phrases them.",
    ])
    card(s, 6.8, 1.55, 5.95, 4.95, "Left for a later system", [
        "Real customer records.",
        "Approving or declining a claim.",
        "Bill photos and scanned wordings.",
        "Multilingual wordings.",
        "A customer-facing bot. The tone,",
        "the refusal policy, and the audit",
        "trail would be different.",
        "Production access control.",
    ], GOLD)
    footer(s, 3, total)

    # 4 why this design
    s = new_slide(prs, "The design", "Retrieval carries the fact. The adapter carries the format.")
    rows = [
        ("Keyword search", "Finds a clause only when the handler already knows its words."),
        ("A fixed FAQ", "Breaks as soon as the question is not one of the authored pairs."),
        ("A rules engine", "Can encode a few limits. It cannot read an exception inside a clause."),
        ("A model with no corpus", "Invents sums insured and waiting periods from memory."),
    ]
    for i, (title, body) in enumerate(rows):
        y = 1.48 + i * 1.05
        add_rect(s, Inches(0.55), Inches(y), Inches(8.15), Inches(0.92), WHITE, LINE)
        add_rect(s, Inches(0.55), Inches(y), Inches(0.08), Inches(0.92), MUTED)
        add_text(s, Inches(0.85), Inches(y + 0.08), Inches(7.6), Inches(0.32), title, 16, NAVY, True)
        add_text(s, Inches(0.85), Inches(y + 0.42), Inches(7.6), Inches(0.4), body, 14, INK)
    add_rect(s, Inches(8.9), Inches(1.48), Inches(3.9), Inches(5.02), NAVY)
    add_text(s, Inches(9.15), Inches(1.7), Inches(3.45), Inches(0.7), "What we built", 18, GOLD, True)
    add_text(s, Inches(9.15), Inches(2.5), Inches(3.45), Inches(3.6),
             "Retrieve the governing clause.\n\nAsk a small local model to write a cite-or-refuse sentence.\n\nShow the clause next to the draft.",
             16, WHITE)
    footer(s, 4, total)

    # 5 targets
    s = new_slide(prs, "Before the build", "Four targets, written down first.")
    targets = [
        ("01", "Find the clause", "The gold clause is in the top 3 on at least 75% of held-out answerable questions."),
        ("02", "Refuse the rest", "Unsafe and out-of-scope questions are refused, and the reason is recorded."),
        ("03", "Cite or refuse", "A shown draft names a retrieved clause, or it is an explicit refusal."),
        ("04", "Time it here", "Latency is measured on this laptop, not taken from a model card."),
    ]
    for i, (n, title, body) in enumerate(targets):
        col = i % 2
        row = i // 2
        x = 0.55 + col * 6.35
        y = 1.55 + row * 2.55
        add_rect(s, Inches(x), Inches(y), Inches(6.1), Inches(2.35), WHITE, LINE)
        add_text(s, Inches(x + 0.25), Inches(y + 0.18), Inches(1.2), Inches(0.4), n, 20, TEAL, True)
        add_text(s, Inches(x + 1.4), Inches(y + 0.22), Inches(4.4), Inches(0.4), title, 20, NAVY, True)
        add_text(s, Inches(x + 0.25), Inches(y + 0.9), Inches(5.6), Inches(1.15), body, 16, INK)
    footer(s, 5, total)

    # 6 path
    s = new_slide(prs, "A question, end to end", "Seven stages. Two of them can stop the model.")
    steps = [
        ("1", "Screen"),
        ("2", "Expand"),
        ("3", "Search"),
        ("4", "Rerank"),
        ("5", "Gate"),
        ("6", "Draft"),
        ("7", "Check the id"),
    ]
    for i, (n, label) in enumerate(steps):
        x = 0.5 + i * 1.82
        add_rect(s, Inches(x), Inches(1.55), Inches(1.68), Inches(1.25), NAVY if i % 2 == 0 else TEAL)
        add_text(s, Inches(x), Inches(1.64), Inches(1.68), Inches(0.32), n, 14, GOLD, True, PP_ALIGN.CENTER)
        add_text(s, Inches(x + 0.06), Inches(1.98), Inches(1.56), Inches(0.65), label, 15, WHITE, True, PP_ALIGN.CENTER)
    card(s, 0.55, 3.15, 6.05, 3.35, "The model is called", [
        "The redacted question and three",
        "clauses go into a fixed instruction.",
        "Flan-T5-small writes up to 80 tokens,",
        "beam size 2, so the clause id is less",
        "likely to be dropped mid-sentence.",
        "Training uses this same prompt.",
    ])
    card(s, 6.8, 3.15, 5.95, 3.35, "The model stays idle", [
        "Injection and fraud coaching stop",
        "at the screen.",
        "A weak match is refused at the gate.",
        "A failed draft says so, and the",
        "clauses stay on screen.",
        "A missing index or adapter shows",
        "the command that builds it.",
    ], GOLD)
    footer(s, 6, total)

    # 7 components
    s = new_slide(prs, "The pieces", "Chosen for a 12 GB CPU laptop and a clause id.")
    specs = [
        ("Generator", "Flan-T5-small", "Trains and answers here. Flan-T5-base is the same code path on a GPU. A 7B model does not fit. An API would send the question off the machine."),
        ("Adapter", "LoRA, rank 8", "Alpha 32, dropout 0.05, on the q and v projections. Thirty-two rows. A larger rank memorizes them."),
        ("Search", "Dense + exact tokens", "MiniLM vectors in Chroma, cosine. BM25 keeps exact figures such as 1500cc and Rs 2,000. The two lists are fused by rank, k = 60."),
        ("Rerank", "Cross-encoder, top 8", "The question and the clause are read together, which matters for a waiver. All 40 clauses on every question would waste CPU."),
        ("Chunks", "One clause, one chunk", "The handler cites a clause id. A wide window would separate an exclusion from its exception."),
        ("Expansion", "A fixed dictionary", "Used for search and reranking. Auditable. The generator still sees the handler’s own words."),
    ]
    for i, (kicker, title, body) in enumerate(specs):
        col = i % 3
        row = i // 3
        x = 0.55 + col * 4.2
        y = 1.48 + row * 2.7
        add_rect(s, Inches(x), Inches(y), Inches(4.02), Inches(2.52), WHITE, LINE)
        add_rect(s, Inches(x), Inches(y), Inches(0.08), Inches(2.52), TEAL if row == 0 else GOLD)
        add_text(s, Inches(x + 0.22), Inches(y + 0.12), Inches(3.65), Inches(0.28), kicker.upper(), 12, TEAL, True)
        add_text(s, Inches(x + 0.22), Inches(y + 0.4), Inches(3.65), Inches(0.4), title, 16, NAVY, True)
        add_text(s, Inches(x + 0.22), Inches(y + 0.9), Inches(3.65), Inches(1.45), body, 13, INK)
    footer(s, 7, total)

    # 8 safety and errors
    s = new_slide(prs, "Before a draft is shown", "The unsafe question never reaches the model.")
    checks = [
        ("Injection", "“Ignore previous instructions” is refused. The model is not called."),
        ("Fraud coaching", "“How do I forge a discharge summary” is refused. “What does the fraud clause say” is answered."),
        ("Out of scope", "Diagnosis, and “which policy should I buy”, are refused."),
        ("Personal data", "Phone, email, PAN, and Aadhaar-shaped numbers are replaced before embedding."),
        ("Weak match", "The gate refuses when cosine is under 0.35 and the rerank score is under −8. “What salary does the CEO draw?” scores 0.14."),
        ("A bad id", "A clause id the retriever did not return is removed from the draft."),
    ]
    for i, (title, body) in enumerate(checks):
        col = i % 2
        row = i // 2
        x = 0.55 + col * 6.35
        y = 1.48 + row * 1.8
        add_rect(s, Inches(x), Inches(y), Inches(6.15), Inches(1.65), WHITE, LINE)
        add_rect(s, Inches(x), Inches(y), Inches(0.08), Inches(1.65), TEAL if i < 4 else GOLD)
        add_text(s, Inches(x + 0.25), Inches(y + 0.12), Inches(5.7), Inches(0.35), title, 16, NAVY, True)
        add_text(s, Inches(x + 0.25), Inches(y + 0.55), Inches(5.7), Inches(0.95), body, 14, INK)
    footer(s, 8, total)

    # 9 training
    s = new_slide(prs, "Teaching the format", "The adapter never sees the clauses it is tested on.")
    card(s, 0.55, 1.5, 6.05, 5.0, "The file", [
        "32 rows: 26 answers and 6 refusals.",
        "Each row points at clause ids. The",
        "trainer fills the text from the wording.",
        "",
        "Waiting period, co-pay, ambulance,",
        "engine protect, and the other eval",
        "clauses are absent from training.",
        "",
        "A refusal row pairs an off-topic",
        "question with a real, irrelevant",
        "clause, and the target REFUSE.",
    ])
    card(s, 6.8, 1.5, 5.95, 5.0, "The run that moved", [
        "Rank 8, learning rate 5e-4,",
        "12 epochs. Train loss 2.84.",
        "",
        "An earlier run at 1e-4 for",
        "3 epochs left the LoRA B",
        "matrices at zero.",
        "",
        "Logged in artifacts/train_log.json.",
        "Seed 42. The run can be repeated.",
    ], GOLD)
    footer(s, 9, total)

    # 10 before / after
    s = new_slide(prs, "The adapter, isolated", "The gold clause is pasted in. Retrieval cannot help.")
    # metric strip
    metrics = [
        ("14%", "Base names the clause"),
        ("77%", "LoRA names the clause"),
        ("23%", "LoRA says REFUSE anyway"),
        ("0.56", "LoRA ROUGE-L, from 0.13"),
    ]
    for i, (num, label) in enumerate(metrics):
        x = 0.55 + i * 3.15
        add_rect(s, Inches(x), Inches(1.48), Inches(3.02), Inches(1.45), WHITE, LINE)
        add_text(s, Inches(x + 0.15), Inches(1.58), Inches(2.7), Inches(0.6), num, 28, NAVY, True, PP_ALIGN.CENTER)
        add_text(s, Inches(x + 0.15), Inches(2.25), Inches(2.7), Inches(0.5), label, 13, MUTED, align=PP_ALIGN.CENTER)
    card(s, 0.55, 3.15, 6.05, 3.35, "Waiting period, held out", [
        "Base: “[HP-02]”.",
        "LoRA: expenses for an illness are not",
        "payable in the first 30 days. Accidental",
        "injuries are covered from day one.",
        "Clauses: HP-02.",
    ])
    card(s, 6.8, 3.15, 5.95, 3.35, "The miss to show", [
        "Age 62, admitted after an accident.",
        "LoRA: “Yes. HP-05.”",
        "The wording waives the 10 percent",
        "co-pay for accidental injury.",
        "It cited the clause and missed the",
        "exception.",
    ], GOLD)
    footer(s, 10, total)

    # 11 retrieval
    s = new_slide(prs, "Finding the clause", "On this set, the gold clause is rank 1.")
    card(s, 0.55, 1.5, 7.3, 5.0, "22 answerable questions", [
        "Dense only                         hit at 3    1.00     MRR  1.00",
        "Dense + BM25                    hit at 3    1.00     MRR  1.00",
        "Plus the reranker               hit at 3    1.00     MRR  1.00",
        "",
        "The paraphrase subset is 1.00 as well.",
        "“Cooling-off” fell to rank 2 when the",
        "reranker scored the raw question.",
        "Scoring the expanded string put HP-02",
        "back at rank 1.",
    ])
    card(s, 8.05, 1.5, 4.7, 5.0, "What 1.00 means here", [
        "Forty short clauses,",
        "written to be distinct.",
        "",
        "Dense search was",
        "already enough.",
        "",
        "Hybrid search and the",
        "reranker earn their place",
        "when wordings share",
        "boilerplate.",
    ], GOLD)
    footer(s, 11, total)

    # 12 full pipeline
    s = new_slide(prs, "The whole app", "Retrieval is right. The citation often is not.")
    headers = ["", "Base", "LoRA"]
    rows = [
        ("Refusal catch", "1.00", "1.00"),
        ("Names the gold clause", "0.27", "0.32"),
        ("False refusal", "0.00", "0.09"),
        ("Median latency", "0.8 s", "3.8 s"),
    ]
    add_rect(s, Inches(0.55), Inches(1.5), Inches(7.35), Inches(3.55), WHITE, LINE)
    xs = [0.75, 4.5, 6.15]
    for x, htext in zip(xs, headers):
        add_text(s, Inches(x), Inches(1.62), Inches(1.6), Inches(0.35), htext, 14, TEAL, True)
    for i, (label, base, lora) in enumerate(rows):
        y = 2.1 + i * 0.68
        add_text(s, Inches(0.75), Inches(y), Inches(3.5), Inches(0.4), label, 16, NAVY, True)
        add_text(s, Inches(4.5), Inches(y), Inches(1.4), Inches(0.4), base, 16, INK)
        add_text(s, Inches(6.15), Inches(y), Inches(1.4), Inches(0.4), lora, 16, INK, True)
    card(s, 8.1, 1.5, 4.65, 5.0, "Why 77% became 32%", [
        "The prompt now holds",
        "three clauses.",
        "",
        "The waiting-period draft",
        "quotes the 30-day rule,",
        "then ends “Clauses: HP-04”.",
        "",
        "HP-04 was retrieved.",
        "It is the wrong clause.",
        "Only an id outside the",
        "top 3 is stripped.",
    ], GOLD)
    add_text(s, Inches(0.55), Inches(5.2), Inches(7.3), Inches(1.2),
             "Six questions should be refused, and all six are, for the intended reason. Injection and fraud coaching never call the model. The CEO-salary question is refused by the grounding gate.",
             14, INK)
    footer(s, 12, total)

    # 13 handler session
    s = new_slide(prs, "On the screen", "The questions a handler actually asks.")
    demo = [
        ("1", "Waiting period", "Illness waits 30 days. Accidental injury is covered from day one. HP-02."),
        ("2", "Cooling-off", "The same clause, found from a paraphrase the wording does not use."),
        ("3", "Age 62, after an accident", "Co-pay is waived. The current draft has missed this exception."),
        ("4", "Ambulance, with a phone and an email", "The question on screen has the numbers replaced."),
        ("5", "Ignore previous instructions", "Refused. The model is not called."),
        ("6", "Forge a discharge summary", "Refused. Asking what the fraud clause says still gets an answer."),
        ("7", "Base, then the adapter", "The sidebar swaps the untouched model for the LoRA draft on one held-out question."),
    ]
    for i, (n, title, body) in enumerate(demo):
        y = 1.42 + i * 0.78
        add_rect(s, Inches(0.55), Inches(y), Inches(0.46), Inches(0.46), TEAL if i < 6 else GOLD)
        add_text(s, Inches(0.55), Inches(y + 0.05), Inches(0.46), Inches(0.36), n, 15, WHITE, True, PP_ALIGN.CENTER)
        add_text(s, Inches(1.18), Inches(y - 0.02), Inches(4.3), Inches(0.42), title, 16, NAVY, True)
        add_text(s, Inches(5.5), Inches(y - 0.02), Inches(7.2), Inches(0.6), body, 15, INK)
    footer(s, 13, total)

    # 14 limits
    s = new_slide(prs, "Limits", "What these numbers do not support.")
    limits = [
        ("The corpus", "Forty synthetic clauses, written to be distinct. A real wording set is longer, amended, and sometimes contradictory."),
        ("The questions", "Written by the person who wrote the wordings. The next set has to come from someone else."),
        ("The citation", "With three clauses in the prompt, a correct sentence can carry a neighbour’s id."),
        ("The refusal habit", "Given the right clause, the adapter still refuses about a quarter of the time."),
        ("The redaction", "Regular expressions catch phone, email, PAN, and Aadhaar shapes. They miss names and policy numbers."),
        ("The models", "The embedder and the reranker are general English models. The synonym list misses words that were never listed."),
    ]
    for i, (title, body) in enumerate(limits):
        col = i % 3
        row = i // 3
        x = 0.55 + col * 4.2
        y = 1.5 + row * 2.65
        add_rect(s, Inches(x), Inches(y), Inches(4.02), Inches(2.48), WHITE, LINE)
        add_rect(s, Inches(x), Inches(y), Inches(4.02), Inches(0.08), TEAL if row == 0 else GOLD)
        add_text(s, Inches(x + 0.2), Inches(y + 0.25), Inches(3.6), Inches(0.4), title, 16, NAVY, True)
        add_text(s, Inches(x + 0.2), Inches(y + 0.75), Inches(3.6), Inches(1.5), body, 14, INK)
    footer(s, 14, total)

    # 15 close
    s = new_slide(prs, "Next", "Keep the facts in the wording.")
    card(s, 0.55, 1.5, 6.05, 3.35, "The next measurement", [
        "Questions written by someone who",
        "did not write the wordings.",
        "Train on the retrieved clauses, not",
        "only on the gold clause.",
        "A handler review of the drafts,",
        "including the ones that are wrong.",
    ])
    card(s, 6.8, 1.5, 5.95, 3.35, "The next machine", [
        "Flan-T5-base on a GPU, through",
        "the same code path.",
        "Real customer files stay out until",
        "access control and retention exist.",
    ], GOLD)
    add_rect(s, Inches(0.55), Inches(5.05), Inches(12.2), Inches(1.45), NAVY)
    add_text(s, Inches(0.8), Inches(5.22), Inches(11.7), Inches(0.7),
             "A handler gets a draft tied to a clause, or a recorded refusal.", 18, WHITE, True)
    add_text(s, Inches(0.8), Inches(5.9), Inches(11.7), Inches(0.4),
             "The number said to the customer is a number the wording contains.", 15, SOFT)
    footer(s, 15, total)
    return prs


if __name__ == "__main__":
    prs = build()
    out = r"C:\Users\divya\AI Commandos Capstone\PolicyGuard.pptx"
    prs.save(out)
    print(out)
