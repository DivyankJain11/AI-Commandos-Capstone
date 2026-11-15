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
  --ink: #1d2924;
  --muted: #6f7b74;
  --green: #2e5b46;
  --line: rgba(43, 66, 54, 0.11);
}

.stApp {
  background:
    radial-gradient(ellipse at 92% 3%, rgba(206, 225, 209, 0.52), transparent 32%),
    radial-gradient(ellipse at 4% 19%, rgba(247, 229, 208, 0.48), transparent 29%),
    #f6f7f3;
  color: var(--ink);
}
[data-testid="stHeader"] {
  background: rgba(246, 247, 243, 0.62);
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
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
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
  background: #254a39;
  color: #f7f8f3;
  font: 500 1.15rem/1 "Iowan Old Style", Georgia, serif;
}
.brand-name {
  color: #26342d;
  font-size: 0.9rem;
  font-weight: 650;
  letter-spacing: 0.01em;
}
.brand-subtitle {
  margin-top: 0.12rem;
  color: var(--muted);
  font-size: 0.68rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}
.local-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.48rem;
  padding: 0.5rem 0.78rem;
  border: 1px solid rgba(46, 91, 70, 0.13);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.5);
  color: #52665a;
  font-size: 0.75rem;
}
.local-dot {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 50%;
  background: #5a956e;
  box-shadow: 0 0 0 3px rgba(90, 149, 110, 0.12);
}

.hero {
  max-width: 760px;
  padding: 3.2rem 0 2rem;
}
.eyebrow, .section-kicker {
  color: #718076;
  font-size: 0.69rem;
  font-weight: 650;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.hero h1 {
  margin: 0.9rem 0 0.85rem;
  color: #20342a;
  font: 400 clamp(2.5rem, 5vw, 4.1rem)/1.07 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  letter-spacing: -0.045em;
}
.hero h1 em {
  color: #54715c;
  font-weight: 400;
}
.hero-copy {
  max-width: 570px;
  margin: 0;
  color: #69756e;
  font-size: 1.04rem;
  line-height: 1.7;
}
.demo-note {
  margin-top: 1rem;
  color: #7b847e;
  font-size: 0.78rem;
  line-height: 1.6;
}

[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid rgba(255, 255, 255, 0.82);
  border-radius: 1.45rem;
  background: rgba(255, 255, 255, 0.59);
  box-shadow: 0 18px 55px rgba(42, 59, 48, 0.065), 0 2px 8px rgba(42, 59, 48, 0.035);
  backdrop-filter: blur(22px);
}
.question-heading {
  margin: 0.15rem 0 0.3rem;
  color: #26372e;
  font: 400 1.55rem/1.25 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  letter-spacing: -0.02em;
}
.question-help {
  margin: 0 0 1.15rem;
  color: #77827a;
  font-size: 0.88rem;
  line-height: 1.55;
}
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label {
  color: #55655b;
  font-size: 0.78rem;
  font-weight: 600;
}
[data-testid="stTextArea"] textarea {
  min-height: 7rem;
  border: 1px solid rgba(55, 79, 63, 0.16) !important;
  border-radius: 1rem !important;
  background: rgba(255, 255, 255, 0.78) !important;
  color: #26342d !important;
  font-size: 0.98rem;
  line-height: 1.6;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}
[data-testid="stTextArea"] textarea::placeholder {
  color: #8a948d !important;
  opacity: 1;
}
[data-testid="stTextArea"] textarea:focus {
  border-color: rgba(46, 91, 70, 0.62) !important;
  box-shadow: 0 0 0 3px rgba(46, 91, 70, 0.1) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-color: rgba(55, 79, 63, 0.15) !important;
  border-radius: 0.8rem !important;
  background: rgba(255, 255, 255, 0.78) !important;
  color: #26342d !important;
}
[data-testid="stBaseButton-primary"] {
  min-height: 2.85rem;
  padding: 0.15rem 1.25rem;
  border: 1px solid #254a39;
  border-radius: 999px;
  background: #254a39;
  color: #fff;
  font-weight: 600;
  transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
}
[data-testid="stBaseButton-primary"]:hover {
  border-color: #315b45;
  background: #315b45;
  box-shadow: 0 7px 18px rgba(37, 74, 57, 0.17);
  transform: translateY(-1px);
}
[data-testid="stAlert"] {
  border-radius: 1rem;
}
[data-testid="stExpander"] {
  overflow: hidden;
  border: 1px solid rgba(48, 72, 57, 0.1);
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.48);
}
[data-testid="stExpander"] summary p {
  color: #34483b;
  font-size: 0.9rem;
  font-weight: 550;
}
[data-testid="stCaptionContainer"] {
  color: #78837b;
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
  color: #26372e;
  font: 400 1.5rem/1.25 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
}
.grounded-badge {
  padding: 0.4rem 0.7rem;
  border: 1px solid rgba(46, 91, 70, 0.13);
  border-radius: 999px;
  background: rgba(235, 243, 235, 0.8);
  color: #496650;
  font-size: 0.72rem;
  white-space: nowrap;
}
.source-intro {
  margin: -0.25rem 0 1rem;
  color: #77827a;
  font-size: 0.87rem;
  line-height: 1.55;
}
.source-title {
  margin: 0.2rem 0 0.35rem;
  color: #26372e;
  font: 400 1.65rem/1.25 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
}

section[data-testid="stSidebar"] {
  border-right: 1px solid rgba(43, 66, 54, 0.09);
  background: rgba(244, 246, 241, 0.82);
  backdrop-filter: blur(22px);
}
section[data-testid="stSidebar"] h2 {
  color: #26372e;
  font: 400 1.5rem/1.25 "Iowan Old Style", "Palatino Linotype", Georgia, serif;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label p {
  color: #43544a;
  font-size: 0.84rem;
}
.sidebar-note {
  margin-top: 1rem;
  padding: 0.9rem 1rem;
  border: 1px solid rgba(46, 91, 70, 0.1);
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.55);
  color: #68766d;
  font-size: 0.78rem;
  line-height: 1.6;
}

@media (max-width: 640px) {
  .block-container {
    padding: 3rem 1rem 3rem;
  }
  .hero {
    padding: 2.3rem 0 1.5rem;
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
          <div class="eyebrow">PolicyGuard · a little more clarity</div>
          <h1>Good answers begin<br>with <em>the wording.</em></h1>
          <p class="hero-copy">
            Get a thoughtful first read of a policy question, with the clause beside the draft
            so you can check the details for yourself.
          </p>
          <p class="demo-note">{DISCLAIMER}</p>
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
