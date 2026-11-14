"""Build the capstone rubric walkthrough deck. One-off generator."""

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

NAVY = RGBColor(0x0F, 0x27, 0x44)
TEAL = RGBColor(0x1F, 0x7A, 0x6B)
GOLD = RGBColor(0xB8, 0x8A, 0x2E)
INK = RGBColor(0x1C, 0x24, 0x30)
MUTED = RGBColor(0x5C, 0x6B, 0x7A)
PAPER = RGBColor(0xF7, 0xF5, 0xF0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD9, 0xD3, 0xC7)
RED = RGBColor(0x8C, 0x3A, 0x3A)

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
             "AI Commandos capstone  ·  PolicyGuard", 11, MUTED)
    add_text(slide, Inches(11.2), Inches(7.12), Inches(1.6), Inches(0.28),
             f"{n}  /  {total}", 11, MUTED, align=PP_ALIGN.RIGHT)


def new_slide(prs, kicker, title):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, 0, 0, W, H, PAPER)
    add_rect(slide, 0, 0, Inches(0.12), H, TEAL)
    add_text(slide, Inches(0.55), Inches(0.28), Inches(12), Inches(0.28), kicker.upper(), 12, TEAL, True)
    add_text(slide, Inches(0.55), Inches(0.52), Inches(12.2), Inches(0.7), title, 28, NAVY, True)
    return slide


def bullets(slide, items, top=1.45, left=0.55, width=12.2, size=18, color=INK, spacing=10):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(5.4))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.level = 0
        p.space_after = Pt(spacing)
        set_run(p.add_run(), item, size, color)
    return box


def card(slide, l, t, w, h, heading, body, accent=TEAL):
    add_rect(slide, Inches(l), Inches(t), Inches(w), Inches(h), WHITE, LINE)
    add_rect(slide, Inches(l), Inches(t), Inches(0.08), Inches(h), accent)
    add_text(slide, Inches(l + 0.25), Inches(t + 0.15), Inches(w - 0.4), Inches(0.4), heading, 16, NAVY, True)
    box = slide.shapes.add_textbox(Inches(l + 0.25), Inches(t + 0.58), Inches(w - 0.45), Inches(h - 0.75))
    tf = box.text_frame
    tf.word_wrap = True
    lines = body if isinstance(body, list) else [body]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(4)
        set_run(p.add_run(), line, 14, INK)


def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    prs.core_properties.title = "AI Commandos Capstone — Rubric walkthrough"
    prs.core_properties.author = "Divyank Jain"
    prs.core_properties.subject = "PolicyGuard rubric requirements and how the project meets them"
    total = 20

    # 1 title
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(s, 0, 0, W, H, NAVY)
    add_rect(s, 0, 0, Inches(0.18), H, TEAL)
    add_text(s, Inches(0.7), Inches(1.7), Inches(11), Inches(0.35), "AI COMMANDOS  ·  CAPSTONE", 14, GOLD, True)
    add_text(s, Inches(0.7), Inches(2.15), Inches(11.5), Inches(1.6),
             "What the rubric requires", 44, WHITE, True)
    add_text(s, Inches(0.7), Inches(3.9), Inches(11), Inches(1.1),
             "Every scored step, the pass rule, and how PolicyGuard\nanswers each one.", 20, RGBColor(0xD5, 0xDD, 0xE6))
    add_text(s, Inches(0.7), Inches(5.6), Inches(8), Inches(0.4), "Passing score   60 / 100", 18, GOLD, True)
    add_text(s, Inches(0.7), Inches(6.3), Inches(8), Inches(0.35), "Divyank Jain   ·   PolicyGuard", 16, RGBColor(0xD5, 0xDD, 0xE6))

    # 2 how points split
    s = new_slide(prs, "Scoring", "60 points are the project. 40 are you.")
    card(s, 0.55, 1.55, 6.0, 4.9, "Project work  ·  60", [
        "A  Problem and strategy          20",
        "     Business problem                 10",
        "     System design                     10",
        "B  Model adaptation                20",
        "     Fine-tuning                          10",
        "     RAG                                    10",
        "C  Implementation                   15",
        "     Code, demo, safety            5 + 5 + 5",
        "D  Evaluation                            5",
    ])
    card(s, 6.8, 1.55, 5.9, 2.3, "Individual  ·  40", [
        "Conceptual mastery          20",
        "Practical ownership           20",
        "Spoken. Not a slide score.",
    ], GOLD)
    card(s, 6.8, 4.05, 5.9, 2.4, "The only extra points", [
        "System design can gain up to",
        "5 complexity points.",
        "Category 2 then maxes at 15.",
        "The form’s printed total is 100.",
    ])
    footer(s, 2, total)

    # 3 rules
    s = new_slide(prs, "Read this before anything else", "Four rules. Break one and the submission is not valid.")
    rules = [
        ("1", "RAG or fine-tuning must be real", "A prompt-only chatbot is not a submission, however good the answers look."),
        ("2", "LoRA is the expected fine-tune", "Full fine-tuning is not required. It is a complexity bonus, and only if the whole training loop is shown."),
        ("3", "You may skip one method, not both", "Fine-tuning can be N/A only if RAG works. RAG can be N/A only if fine-tuning works."),
        ("4", "Partial work still scores", "Excellent, good, satisfactory, and needs-improvement all award points inside the band."),
    ]
    for i, (n, title, body) in enumerate(rules):
        y = 1.5 + i * 1.3
        add_rect(s, Inches(0.55), Inches(y), Inches(0.7), Inches(1.05), TEAL if i < 3 else GOLD)
        add_text(s, Inches(0.55), Inches(y + 0.28), Inches(0.7), Inches(0.5), n, 22, WHITE, True, PP_ALIGN.CENTER)
        add_text(s, Inches(1.5), Inches(y + 0.08), Inches(11), Inches(0.4), title, 20, NAVY, True)
        add_text(s, Inches(1.5), Inches(y + 0.5), Inches(11), Inches(0.45), body, 16, INK)
    footer(s, 3, total)

    # 4 classification
    s = new_slide(prs, "Page 1 of the form", "Tick these boxes. They frame every later score.")
    rows = [
        ("Fine-tuning", "LoRA / PEFT", "Not QLoRA: no NVIDIA GPU. Not full fine-tuning."),
        ("RAG", "Advanced, hybrid", "Chunking, expansion, BM25 + dense, rerank."),
        ("Modality", "Text only", "Multimodal was left out on purpose. See the bonus slide."),
        ("Base model", "T5", "google/flan-t5-small. Fits a 12 GB CPU laptop."),
        ("Domain", "Customer service", "Insurance claims. The form’s closest box."),
        ("Vector database", "ChromaDB", "Local and persistent. Rebuilt by ingest."),
    ]
    for i, (field, choice, why) in enumerate(rows):
        col = i % 2
        row = i // 2
        x = 0.55 + col * 6.35
        y = 1.5 + row * 1.75
        add_rect(s, Inches(x), Inches(y), Inches(6.05), Inches(1.55), WHITE, LINE)
        add_text(s, Inches(x + 0.25), Inches(y + 0.12), Inches(5.5), Inches(0.3), field, 13, TEAL, True)
        add_text(s, Inches(x + 0.25), Inches(y + 0.42), Inches(5.5), Inches(0.4), choice, 20, NAVY, True)
        add_text(s, Inches(x + 0.25), Inches(y + 0.95), Inches(5.5), Inches(0.45), why, 14, INK)
    footer(s, 4, total)

    # 5 cat 1
    s = new_slide(prs, "Section A  ·  Category 1  ·  10 points", "Business problem. Five things, or the score stays in the middle.")
    bullets(s, [
        "A business problem with a measurable consequence, not a topic.",
        "Named users and the job they are doing when they ask.",
        "A PoC boundary: what is in, and what is explicitly out.",
        "Why a generative model, set against the alternatives you rejected.",
        "Success metrics written as numbers before you build, not after.",
    ], size=20, spacing=14)
    add_text(s, Inches(0.55), Inches(6.35), Inches(12), Inches(0.5),
             "Excellent is 9–10. Good is 8. Satisfactory is 6–7. Vague users or no alternative comparison sits at 0–5.",
             14, MUTED)
    footer(s, 5, total)

    # 6 our problem
    s = new_slide(prs, "Category 1  ·  PolicyGuard", "The problem we are actually solving.")
    card(s, 0.55, 1.5, 6.05, 2.5, "Who, and what goes wrong", [
        "User: a junior claims handler.",
        "PDF search misses paraphrases.",
        "A general chatbot invents a limit.",
        "That invented limit becomes a",
        "promise to the customer.",
    ])
    card(s, 6.8, 1.5, 5.95, 2.5, "Rejected on purpose", [
        "Keyword search — fails paraphrases.",
        "A fixed FAQ — breaks off-script.",
        "A rules engine — cannot read an",
        "exception inside a clause.",
        "Prompting with no corpus — invalid.",
    ], GOLD)
    card(s, 0.55, 4.2, 12.2, 2.35, "Success targets, set before the build", [
        "Gold clause in the top 3 on at least 75% of held-out questions.",
        "Unsafe and out-of-scope questions refused, with the reason recorded.",
        "A shown draft either cites a retrieved clause or is an explicit refusal.",
        "Latency measured on this laptop, not taken from a brochure.",
    ])
    footer(s, 6, total)

    # 7 cat 2
    s = new_slide(prs, "Section A  ·  Category 2  ·  10 points", "System design. The evaluator wants the path, not a logo diagram.")
    bullets(s, [
        "One picture of the system a handler can follow from question to answer.",
        "The model choice justified against cost, latency, and this machine.",
        "The data flow, including the path that does not call the model.",
        "Where RAG sits, and what happens when retrieval is weak.",
        "Error handling: missing index, missing adapter, generation failure.",
    ], size=20, spacing=14)
    add_text(s, Inches(0.55), Inches(6.35), Inches(12), Inches(0.5),
             "A model name with no reason is a needs-improvement. The reason is the score.",
             14, MUTED)
    footer(s, 7, total)

    # 8 flow
    s = new_slide(prs, "Category 2  ·  PolicyGuard", "The path a question actually takes.")
    steps = [
        ("1", "Guardrails"),
        ("2", "Expand"),
        ("3", "Chroma + BM25"),
        ("4", "Rerank"),
        ("5", "Grounding gate"),
        ("6", "Flan-T5 + LoRA"),
        ("7", "Check the clause id"),
    ]
    for i, (n, label) in enumerate(steps):
        x = 0.5 + i * 1.82
        add_rect(s, Inches(x), Inches(1.7), Inches(1.65), Inches(1.35), NAVY if i % 2 == 0 else TEAL)
        add_text(s, Inches(x), Inches(1.82), Inches(1.65), Inches(0.35), n, 14, GOLD, True, PP_ALIGN.CENTER)
        add_text(s, Inches(x + 0.08), Inches(2.2), Inches(1.5), Inches(0.7), label, 14, WHITE, True, PP_ALIGN.CENTER)
    card(s, 0.55, 3.4, 6.05, 3.1, "Why this model", [
        "12 GB RAM, no NVIDIA GPU.",
        "Flan-T5-small trains and answers here.",
        "Flan-T5-base is the same code path",
        "when a GPU exists.",
        "A 7B model does not fit.",
        "An API model would hide the training.",
    ])
    card(s, 6.8, 3.4, 5.95, 3.1, "When it does not call the model", [
        "Injection and fraud coaching stop",
        "before retrieval.",
        "A weak match is refused.",
        "A failed draft says so, and still",
        "shows the clauses.",
        "A missing draft is not a yes.",
    ], GOLD)
    footer(s, 8, total)

    # 9 bonuses
    s = new_slide(prs, "Category 2  ·  complexity", "Bonuses are optional. The baseline is not a penalty.")
    card(s, 0.55, 1.55, 4.0, 4.9, "Advanced RAG   +3", [
        "We claim this.",
        "Clause-sized chunks.",
        "Synonym expansion.",
        "BM25 + dense, fused",
        "with reciprocal rank.",
        "Cross-encoder on the",
        "top 8.",
        "At least two techniques",
        "with a written reason.",
    ], TEAL)
    card(s, 4.7, 1.55, 4.0, 4.9, "Multimodal   +5", [
        "We do not claim this.",
        "Bill photos and scanned",
        "wordings add an OCR",
        "failure we cannot",
        "measure honestly.",
        "The handler’s question",
        "is text. Images are a",
        "later project.",
    ], MUTED)
    card(s, 8.85, 1.55, 3.95, 4.9, "Full fine-tune   +5", [
        "We do not claim this.",
        "The rubric says LoRA",
        "is the baseline.",
        "Full training of even",
        "this small model is",
        "the wrong spend on",
        "a CPU laptop.",
    ], GOLD)
    footer(s, 9, total)

    # 10 section B
    s = new_slide(prs, "Section B  ·  20 points", "Do both methods. Skipping one throws points away.")
    card(s, 0.55, 1.55, 6.05, 4.9, "If you mark fine-tuning N/A", [
        "Allowed only when RAG works.",
        "Those 10 points do not all move.",
        "+5 goes to the business problem.",
        "+5 goes to evaluation.",
        "The other 5 are gone.",
        "You also lose the before/after story.",
    ])
    card(s, 6.8, 1.55, 5.95, 4.9, "If you mark RAG N/A", [
        "Allowed only when fine-tuning works.",
        "+5 goes to the business problem.",
        "+5 goes to implementation.",
        "The other 5 are gone.",
        "A changed clause then requires",
        "a new training run.",
    ], GOLD)
    footer(s, 10, total)

    # 11 cat 3
    s = new_slide(prs, "Section B  ·  Category 3  ·  10 points", "Fine-tuning. They score the change in behaviour, not the GPU.")
    bullets(s, [
        "A recognised lightweight method. LoRA is the named baseline.",
        "A small dataset that was chosen, not scraped. Quality over quantity.",
        "Metrics, a before/after, and a reason for each hyperparameter.",
        "An honest limit, and the training log on disk.",
        "Held-out questions that the adapter never saw as training rows.",
    ], size=20, spacing=14)
    footer(s, 11, total)

    # 12 our lora
    s = new_slide(prs, "Category 3  ·  PolicyGuard", "What the adapter was trained to do, and what changed.")
    card(s, 0.55, 1.5, 6.05, 5.0, "The run", [
        "32 rows: 26 answers, 6 refusals.",
        "Eval clauses are not in the file.",
        "Same prompt function at train",
        "time and in the app.",
        "First run, 1e-4 for 3 epochs,",
        "did not move the B matrices.",
        "Submitted run: rank 8, 5e-4,",
        "12 epochs. Train loss 2.84.",
        "Log: artifacts/train_log.json.",
    ])
    card(s, 6.8, 1.5, 5.95, 5.0, "Before and after", [
        "Gold clause pasted into the prompt,",
        "so this number is the adapter only.",
        "Base names the clause:  14%",
        "LoRA names the clause:  77%",
        "LoRA also refuses 23% of the",
        "time even when the clause is there.",
        "That false refusal is reported,",
        "not hidden.",
    ], GOLD)
    footer(s, 12, total)

    # 13 cat 5
    s = new_slide(prs, "Section B  ·  Category 5  ·  10 points", "RAG. Show a clause coming back, not a library import.")
    bullets(s, [
        "A chunking choice with a reason. Ours is one chunk per clause, because the handler cites a clause id.",
        "An embedding model you can defend on this hardware.",
        "A vector database that is actually queried. Chroma, cosine, precomputed MiniLM vectors.",
        "Retrieval examples, including a paraphrase, with the clause that came back.",
        "Those clauses placed into the prompt. The model does not answer from memory.",
    ], size=18, spacing=12)
    footer(s, 13, total)

    # 14 our rag numbers
    s = new_slide(prs, "Category 5  ·  measured", "On this set, retrieval is solved. Say what that does not prove.")
    card(s, 0.55, 1.55, 7.4, 4.9, "Hit rate at 3  ·  22 answerable questions", [
        "Dense only                         1.00     MRR 1.00",
        "Hybrid, dense + BM25         1.00     MRR 1.00",
        "Advanced, plus rerank         1.00     MRR 1.00",
        "",
        "The paraphrase subset is also 1.00.",
        "The first reranker scored the raw",
        "question and dropped “cooling-off”",
        "to rank 2. It now scores the",
        "expanded string, and HP-02 is rank 1.",
    ])
    card(s, 8.15, 1.55, 4.6, 4.9, "Say this out loud", [
        "Forty short clauses",
        "were written to be",
        "distinct.",
        "Dense search was",
        "already enough.",
        "Advanced RAG did",
        "not add points here.",
        "It is still the right",
        "design for a real",
        "wording library.",
    ], GOLD)
    footer(s, 14, total)

    # 15 section C
    s = new_slide(prs, "Section C  ·  15 points", "Three separate fives. A pretty demo does not cover safety.")
    card(s, 0.55, 1.55, 4.0, 4.9, "4A  Code   5", [
        "Functions, not a notebook",
        "dump.",
        "Errors caught and named.",
        "requirements.txt and a",
        "setup a stranger can run.",
        "pytest for the split, the",
        "guardrails, and the fusion.",
    ])
    card(s, 4.7, 1.55, 4.0, 4.9, "4B  Demo   5", [
        "Ask, and get a draft plus",
        "the clause text.",
        "Switch base vs LoRA.",
        "Switch dense, hybrid,",
        "advanced.",
        "Empty question, weak",
        "match, and a blocked",
        "question all have a path.",
        "Median about 4 seconds",
        "with the adapter.",
    ], TEAL)
    card(s, 8.85, 1.55, 3.95, 4.9, "4C  Safety   5", [
        "At least one guardrail",
        "must be demonstrated,",
        "not only described.",
        "Needs-improvement is",
        "an open prompt with",
        "no check at all.",
    ], GOLD)
    footer(s, 15, total)

    # 16 safety detail
    s = new_slide(prs, "Category 4C  ·  show this live", "Safety that runs before the model is stronger than a polite system prompt.")
    bullets(s, [
        "Injection (“ignore previous instructions”) is refused. The model is not called.",
        "“How do I forge a discharge summary” is refused. “What does the fraud clause say” is allowed.",
        "Diagnosis and “which policy should I buy” are refused.",
        "Phone, email, PAN, and Aadhaar-shaped numbers are replaced before embedding.",
        "A clause id the retriever did not return is stripped from the draft.",
        "Still weak: person names, and any attack phrasing that is not in the regular expressions.",
    ], size=18, spacing=10)
    footer(s, 16, total)

    # 17 cat 6
    s = new_slide(prs, "Section D  ·  Category 6  ·  5 points", "Evaluation. One screenshot of a good answer is not a result.")
    bullets(s, [
        "More than one metric. The form names BLEU, ROUGE, human review, and task metrics.",
        "A baseline. Ours is the base model against the adapter, and dense against advanced retrieval.",
        "A few real outputs, including one that is wrong.",
        "Limits you mean: hallucinations, latency, cost, bias, and what you would do next.",
        "The business value in one sentence a handler’s manager would accept.",
    ], size=18, spacing=12)
    add_text(s, Inches(0.55), Inches(6.4), Inches(12), Inches(0.45),
             "ROUGE-L is reported because the form asks. Clause hit rate is the metric that matches the job.",
             14, MUTED)
    footer(s, 17, total)

    # 18 numbers + individual
    s = new_slide(prs, "Section E  ·  40 points", "The last 40 are whether you can defend the first 60.")
    card(s, 0.55, 1.5, 6.05, 5.05, "Conceptual mastery   20", [
        "Frame the problem, the model,",
        "and why both RAG and LoRA.",
        "Trade off cost, latency, accuracy",
        "without being asked twice.",
        "Tie the metric to the business",
        "mistake: a limit that is not",
        "in the wording.",
        "Name a real limit and a next",
        "step that is technically sound.",
    ])
    card(s, 6.8, 1.5, 5.95, 5.05, "Practical ownership   20", [
        "Own a file and walk it.",
        "Guardrails, retrieval, the",
        "shared prompt, the LoRA run.",
        "Show one iteration: the raw",
        "reranker demoted cooling-off,",
        "so the reranker now sees the",
        "expanded string.",
        "Explain a failure mode and",
        "the mitigation already in code.",
    ], GOLD)
    footer(s, 18, total)

    # Wait I set total to 18 but I want a demo + grades slide. Let me recount.
    # I planned 18 as the last content... I still need demo order and grades.
    # I'll add two more and fix footers... easier to add slides 19 and 20 and
    # update total by patching after. I'll add them and then fix footer numbers
    # in a second pass if needed. Let me add them with total 20 and then
    # I'll update the earlier footer calls... I already used total=18.
    # I'll change approach: add 2 slides with footer 19/20 and 20/20, then
    # do a search replace of "18" in footer calls. The function uses the
    # variable total. I'll set total = 20 now... too late, already passed.
    # I'll add the slides with n computed, then after build I can't easily
    # change earlier footers. Let me just add two slides as 19 and 20 and
    # update the total variable usage by editing the file before running.
    # I'll stop and fix total to 20 and add the remaining slides in the file
    # before the build() return. I'm still writing the file. I'll set total=20
    # at the top... I already wrote total = 18. I'll fix with search_replace
    # after, and append the last slides before build() ends.
    # For now continue writing the last slides inside build() before return.

    s = new_slide(prs, "How to spend the demo", "Seven minutes, in the order the marks are given.")
    demo = [
        ("1", "Direct question", "Waiting period. Read the 30-day rule and the accident exception."),
        ("2", "Paraphrase", "Cooling-off, or flood water and the engine. Show the clause, not the synonym list."),
        ("3", "Exception", "Age 62, admitted after an accident. Co-pay is waived. The model has missed this. Say so."),
        ("4", "Personal data", "Ambulance question with a phone and an email. Show the redacted question."),
        ("5", "Injection", "Ignore previous instructions. Point out that the model was not called."),
        ("6", "Fraud coaching", "How to forge a discharge summary. Same stop, different reason."),
        ("7", "Before / after", "Switch the sidebar from LoRA to the base model on one held-out question."),
    ]
    for i, (n, title, body) in enumerate(demo):
        y = 1.45 + (i % 7) * 0.75
        add_rect(s, Inches(0.55), Inches(y), Inches(0.48), Inches(0.48), TEAL if i < 6 else GOLD)
        add_text(s, Inches(0.55), Inches(y + 0.06), Inches(0.48), Inches(0.38), n, 16, WHITE, True, PP_ALIGN.CENTER)
        add_text(s, Inches(1.2), Inches(y - 0.02), Inches(3.2), Inches(0.4), title, 16, NAVY, True)
        add_text(s, Inches(4.4), Inches(y - 0.02), Inches(8.3), Inches(0.55), body, 15, INK)
    footer(s, 19, total)

    s = new_slide(prs, "Before you submit", "The grade bands, and the short list.")
    card(s, 0.55, 1.5, 5.3, 5.0, "What the form calls a pass", [
        "90–100   A   Excellent",
        "80–89     B   Good",
        "70–79     C   Satisfactory",
        "60–69     D   Acceptable",
        "Below 60  F   Does not pass",
        "",
        "60 is the line. The individual",
        "40 are half of getting over it.",
    ])
    card(s, 6.05, 1.5, 6.7, 5.0, "Leave with these files open", [
        "README.md and state.md",
        "docs/system_design.md",
        "docs/evaluation.md",
        "docs/viva_notes.md",
        "artifacts/metrics.json",
        "artifacts/train_log.json",
        "The running app on port 8501",
        "",
        "If a number is challenged, open",
        "the metrics file. Do not recall it.",
    ], GOLD)
    footer(s, 20, total)
    return prs


if __name__ == "__main__":
    prs = build()
    out = r"C:\Users\divya\AI Commandos Capstone\AI_Commandos_Rubric_Walkthrough.pptx"
    prs.save(out)
    print(out)
