"""Streamlit demo. Run from the project root: streamlit run app.py"""

from __future__ import annotations

EXAMPLES = [
    "What is the initial waiting period for an illness?",
    "Is the co-pay different when someone is admitted after an accident?",
    "What depreciation applies when a plastic bumper is replaced?",
    "What is the road ambulance limit?",
    "How soon should I notify the insurer after an incident?",
]

PAGE_STYLES = """
<style>
:root {
  --ink: #edf2ed;
  --muted: #a4b0a7;
  --accent: #b4d2b5;
  --line: rgba(201, 222, 204, 0.13);
  --surface: rgba(24, 34, 28, 0.82);
  --surface-soft: rgba(21, 30, 24, 0.72);
  --border: rgba(201, 222, 204, 0.15);
}

.stApp {
  background:
    radial-gradient(ellipse at 88% 0%, rgba(65, 105, 75, 0.2), transparent 34%),
    radial-gradient(ellipse at 5% 22%, rgba(87, 71, 48, 0.12), transparent 30%),
    #0d1410;
  color: var(--ink);
}
[data-testid="stHeader"] {
  background: rgba(13, 20, 16, 0.76);
  backdrop-filter: blur(16px);
}
[data-testid="stMain"] {
  background: transparent;
}
.block-container {
  max-width: 1080px;
  padding-top: 4rem;
  padding-bottom: 5rem;
}
body, [data-testid="stAppViewContainer"] {
  font-family: "Inter", "SF Pro Text", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--ink);
}

.brand-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0 1.5rem;
  border-bottom: 1px solid var(--line);
}
.brand-lockup {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
.brand-mark {
  display: grid;
  width: 2.45rem;
  height: 2.45rem;
  place-items: center;
  border-radius: 0.85rem;
  background: #a8c6a9;
  color: #142017;
  font: 700 1.1rem/1 "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.brand-name {
  color: #edf2ed;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}
.brand-subtitle {
  margin-top: 0.12rem;
  color: #9caaa0;
  font-size: 0.68rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}
.local-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.48rem;
  padding: 0.5rem 0.78rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: rgba(25, 36, 29, 0.72);
  color: #c0cec2;
  font-size: 0.75rem;
}
.local-dot {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 50%;
  background: #9ac69d;
  box-shadow: 0 0 0 3px rgba(154, 198, 157, 0.13);
}

.hero {
  position: relative;
  min-height: 340px;
  padding: 3.2rem 0 2rem;
}
.hero-copy-column {
  position: relative;
  z-index: 1;
  max-width: 660px;
}
.eyebrow, .section-kicker {
  color: #9eafa2;
  font-size: 0.69rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.hero h1 {
  margin: 0.9rem 0 0.85rem;
  color: #f1f4ef;
  font: 700 clamp(2.45rem, 5vw, 3.9rem)/1.08 "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  letter-spacing: -0.055em;
}
.hero h1 em {
  color: var(--accent);
  font-style: italic;
  font-weight: 600;
}
.hero-copy {
  max-width: 570px;
  margin: 0;
  color: #b3beb5;
  font-size: 1.04rem;
  line-height: 1.7;
}
.demo-note {
  margin-top: 1rem;
  color: #89978d;
  font-size: 0.78rem;
  line-height: 1.6;
}
.hero-art {
  position: absolute;
  inset: -1rem -3rem -1rem 30%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
  opacity: 0.72;
  mask-image: linear-gradient(90deg, transparent 0%, #000 25%, #000 82%, transparent 100%);
}
.hero-art svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}
.line-mesh {
  transform-box: fill-box;
  transform-origin: center;
  animation: mesh-drift 18s ease-in-out infinite alternate;
}
.contour {
  fill: none;
  stroke: rgba(164, 204, 167, 0.2);
  stroke-width: 1;
}
.contour-highlight {
  fill: none;
  stroke: url(#contour-light);
  stroke-linecap: round;
  stroke-width: 1.5;
  stroke-dasharray: 105 1120;
  animation: line-travel 18s linear infinite;
}
.contour-highlight--slow {
  stroke-dasharray: 72 1120;
  animation-duration: 27s;
  animation-direction: reverse;
}
.contour-glow {
  fill: none;
  stroke: rgba(156, 207, 159, 0.16);
  stroke-linecap: round;
  stroke-width: 5;
  stroke-dasharray: 105 1120;
  filter: blur(4px);
  animation: line-travel 18s linear infinite;
}
@keyframes mesh-drift {
  from { transform: translate3d(-1.5%, 1%, 0) rotateY(-8deg) rotateX(2deg); }
  to { transform: translate3d(1.5%, -1%, 0) rotateY(5deg) rotateX(-2deg); }
}
@keyframes line-travel {
  to { stroke-dashoffset: -1225; }
}

[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--border);
  border-radius: 1.45rem;
  background: var(--surface);
  box-shadow: 0 22px 65px rgba(0, 0, 0, 0.2), 0 2px 10px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(24px);
}
.question-heading {
  margin: 0.15rem 0 0.3rem;
  color: #eef3ee;
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}
.question-help {
  margin: 0 0 1.15rem;
  color: #a3afa6;
  font-size: 0.88rem;
  line-height: 1.55;
}
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label {
  color: #c4cec5;
  font-size: 0.78rem;
  font-weight: 650;
}
[data-testid="stTextArea"] textarea {
  min-height: 7rem;
  border: 1px solid rgba(187, 211, 191, 0.2) !important;
  border-radius: 1rem !important;
  background: rgba(13, 20, 16, 0.76) !important;
  color: #edf2ed !important;
  font-size: 0.98rem;
  line-height: 1.6;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}
[data-testid="stTextArea"] textarea::placeholder {
  color: #85938a !important;
  opacity: 1;
}
[data-testid="stTextArea"] textarea:focus {
  border-color: rgba(166, 203, 169, 0.72) !important;
  box-shadow: 0 0 0 3px rgba(166, 203, 169, 0.13) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-color: rgba(187, 211, 191, 0.2) !important;
  border-radius: 0.8rem !important;
  background: rgba(13, 20, 16, 0.76) !important;
  color: #edf2ed !important;
}
[data-testid="stSelectbox"] [role="combobox"] {
  color: #edf2ed !important;
}
[data-testid="stBaseButton-primary"] {
  min-height: 2.85rem;
  padding: 0.15rem 1.25rem;
  border: 1px solid #a8c6a9;
  border-radius: 999px;
  background: #a8c6a9;
  color: #142017;
  font-weight: 700;
  transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
}
[data-testid="stBaseButton-primary"]:hover {
  border-color: #c2dbc2;
  background: #c2dbc2;
  box-shadow: 0 7px 20px rgba(137, 183, 142, 0.19);
  transform: translateY(-1px);
}
[data-testid="stAlert"] {
  border: 1px solid var(--border);
  border-radius: 1rem;
  background: rgba(34, 45, 37, 0.86);
}
[data-testid="stExpander"] {
  overflow: hidden;
  border: 1px solid rgba(201, 222, 204, 0.13);
  border-radius: 1rem;
  background: var(--surface-soft);
}
[data-testid="stExpander"] summary p {
  color: #e3ebe3;
  font-size: 0.9rem;
  font-weight: 650;
}
[data-testid="stCaptionContainer"] {
  color: #9ba99f;
}

.answer-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.answer-title {
  margin: 0;
  color: #f0f4ef;
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.grounded-badge {
  padding: 0.4rem 0.7rem;
  border: 1px solid rgba(169, 204, 172, 0.24);
  border-radius: 999px;
  background: rgba(114, 157, 119, 0.15);
  color: #c1ddc2;
  font-size: 0.72rem;
  font-weight: 650;
  white-space: nowrap;
}
.source-intro {
  margin: -0.25rem 0 1rem;
  color: #a3afa6;
  font-size: 0.87rem;
  line-height: 1.55;
}
.source-title {
  margin: 0.2rem 0 0.35rem;
  color: #edf2ed;
  font-size: 1.55rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

section[data-testid="stSidebar"] {
  border-right: 1px solid rgba(201, 222, 204, 0.1);
  background: rgba(14, 21, 17, 0.94);
  backdrop-filter: blur(24px);
}
section[data-testid="stSidebar"] h2 {
  color: #edf2ed;
  font-size: 1.42rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label p {
  color: #d3ddd4;
  font-size: 0.84rem;
}
.sidebar-note {
  margin-top: 1rem;
  padding: 0.9rem 1rem;
  border: 1px solid rgba(201, 222, 204, 0.13);
  border-radius: 1rem;
  background: rgba(27, 38, 31, 0.78);
  color: #aeb9b0;
  font-size: 0.78rem;
  line-height: 1.6;
}

@media (max-width: 640px) {
  .block-container {
    padding: 3rem 1rem 3rem;
  }
  .hero {
    min-height: 340px;
    padding: 2.3rem 0 1.5rem;
  }
  .hero-art {
    inset: 0 -1rem 0 4%;
    opacity: 0.42;
    mask-image: linear-gradient(90deg, transparent 0%, #000 36%, #000 100%);
  }
  .local-badge {
    padding: 0.42rem 0.58rem;
    font-size: 0.68rem;
  }
  .answer-heading {
    align-items: flex-start;
    flex-direction: column;
  }
}
@media (prefers-reduced-motion: reduce) {
  .line-mesh,
  .contour-highlight,
  .contour-glow {
    animation: none !important;
  }
}
</style>
"""


def main() -> None:
    import streamlit as st

    from policyguard.config import DISCLAIMER, GEN_MODEL, LORA_DIR
    from policyguard.generation import AdapterNotFoundError
    from policyguard.indexing import IndexNotBuiltError
    from policyguard.pipeline import answer

    st.set_page_config(page_title="PolicyGuard | Northwind", page_icon="N", layout="wide")
    st.markdown(PAGE_STYLES, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="brand-row">
          <div class="brand-lockup">
            <div class="brand-mark">N</div>
            <div>
              <div class="brand-name">Northwind Assurance</div>
              <div class="brand-subtitle">Claims desk</div>
            </div>
          </div>
          <div class="local-badge"><span class="local-dot"></span>Private demo · local wording</div>
        </div>
        <section class="hero">
          <div class="hero-copy-column">
            <div class="eyebrow">PolicyGuard · a little more clarity</div>
            <h1>Good answers begin<br>with <em>the wording.</em></h1>
            <p class="hero-copy">
              Get a thoughtful first read of a policy question, with the clause beside the draft
              so you can check the details for yourself.
            </p>
            <p class="demo-note">{DISCLAIMER}</p>
          </div>
          <div class="hero-art" aria-hidden="true">
            <svg viewBox="0 0 760 360" preserveAspectRatio="xMidYMid slice">
              <defs>
                <linearGradient id="contour-light" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0" stop-color="#a8c6a9" stop-opacity="0"></stop>
                  <stop offset="0.48" stop-color="#d8efd1" stop-opacity="0.92"></stop>
                  <stop offset="1" stop-color="#a8c6a9" stop-opacity="0"></stop>
                </linearGradient>
              </defs>
              <g class="line-mesh">
                <path class="contour" d="M-50 250 C90 28 190 44 300 142 S500 294 810 74"></path>
                <path class="contour" d="M-55 274 C93 54 196 70 306 168 S507 320 815 99"></path>
                <path class="contour" d="M-60 298 C96 80 202 96 312 194 S513 344 820 124"></path>
                <path class="contour" d="M-30 98 C130 260 231 280 354 170 S556 34 790 230"></path>
                <path class="contour" d="M-35 122 C132 284 236 304 359 194 S561 58 795 254"></path>
                <path class="contour-glow" d="M-50 250 C90 28 190 44 300 142 S500 294 810 74"></path>
                <path class="contour-highlight" d="M-50 250 C90 28 190 44 300 142 S500 294 810 74"></path>
                <path class="contour-highlight contour-highlight--slow" d="M-30 98 C130 260 231 280 354 170 S556 34 790 230"></path>
              </g>
            </svg>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="section-kicker">YOUR WORKSPACE</div>', unsafe_allow_html=True)
        st.header("Answer settings")
        st.caption("Choose how to find and phrase the relevant wording.")
        model_kind = st.radio(
            "Draft style",
            options=["lora", "base"],
            index=0 if LORA_DIR.exists() else 1,
            format_func=lambda value: "Adapted draft" if value == "lora" else "Base model",
        )
        mode = st.radio(
            "Clause search",
            options=["advanced", "hybrid", "dense"],
            format_func=lambda value: {
                "advanced": "Recommended · hybrid + rerank",
                "hybrid": "Hybrid search",
                "dense": "Meaning-based search",
            }[value],
        )
        st.caption(f"Local model: `{GEN_MODEL}`")
        st.markdown(
            '<div class="sidebar-note">Blocked or unrelated requests are declined. '
            'Detected phone numbers, email addresses and government IDs are redacted before '
            'search. Please do not enter real customer information.</div>',
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        st.markdown(
            '<div class="section-kicker">START WITH A QUESTION</div>'
            '<div class="question-heading">What would you like to clarify?</div>'
            '<p class="question-help">Ask in your own words. We’ll look for the closest clause '
            'and show you the source.</p>',
            unsafe_allow_html=True,
        )

        if "loaded_example" not in st.session_state:
            st.session_state.loaded_example = "(write my own)"
            st.session_state.question = ""
        picked = st.selectbox("Or start with a common question", ["(write my own)", *EXAMPLES])
        if picked != st.session_state.loaded_example:
            st.session_state.loaded_example = picked
            st.session_state.question = "" if picked == "(write my own)" else picked

        question = st.text_area(
            "Your question",
            key="question",
            height=120,
            placeholder="For example: does the waiting period apply after an accident?",
        )
        st.caption("This demo uses synthetic policy wording. Leave out names and policy numbers.")
        asked = st.button("Find the clause", type="primary")

    if asked and not question.strip():
        st.error("Write a question first, and I’ll look for the wording that speaks to it.")
    elif asked:
        try:
            with st.spinner("Reading the wording and checking the relevant clauses…"):
                st.session_state.result = answer(question, mode=mode, model_kind=model_kind)
        except IndexNotBuiltError as exc:
            st.error(str(exc))
            return
        except AdapterNotFoundError as exc:
            st.error(str(exc))
            return

    result = st.session_state.get("result")
    if result is None:
        return

    st.markdown('<div class="section-kicker">A CAREFUL FIRST READ</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            '<div class="answer-heading"><h2 class="answer-title">Here’s what the wording says</h2>'
            f'<span class="grounded-badge">{"Needs your review" if result.refused else "Clause checked"}</span>'
            "</div>",
            unsafe_allow_html=True,
        )
        if result.refused:
            st.warning(result.answer)
        else:
            st.write(result.answer)

        meta = [
            f"Ready in {result.latency_ms / 1000:.1f}s",
            {
                "advanced": "Careful search",
                "hybrid": "Hybrid search",
                "dense": "Meaning-based search",
            }.get(result.mode, result.mode),
            "Adapted draft" if result.model_kind == "lora" else "Base model",
        ]
        st.caption(" · ".join(meta))
        if result.redacted_question != question.strip():
            st.caption(f"Personal details removed before processing: {result.redacted_question}")

    st.markdown(
        '<div class="section-kicker">THE SOURCE</div>'
        '<div class="source-title">Read the wording for yourself.</div>'
        '<p class="source-intro">The passages below are the basis for this draft. '
        'Please check the full wording before advising a customer.</p>',
        unsafe_allow_html=True,
    )
    if not result.hits:
        st.info("No matching clause was found, so there’s no source passage to show.")
    for rank, hit in enumerate(result.hits, start=1):
        label = f"{rank:02d}  ·  {hit.clause_id}  ·  {hit.title}"
        with st.expander(label, expanded=rank == 1):
            st.write(hit.text)
            st.caption(f"{hit.product} · {hit.source}")
            rerank = "not used" if hit.rerank_score is None else f"{hit.rerank_score:.2f}"
            st.caption(f"Relevance details · dense {hit.dense_score:.2f} · rerank {rerank}")

    if result.expanded_query or result.model_clause_ids or result.events:
        with st.expander("How this answer was checked"):
            if result.model_clause_ids:
                st.caption("Clause references in the draft: " + ", ".join(result.model_clause_ids))
            if result.expanded_query and result.expanded_query != result.redacted_question:
                st.caption("Expanded search terms: " + result.expanded_query)
            if result.events:
                st.caption("Safety checks: " + ", ".join(result.events))


if __name__ == "__main__":
    main()
