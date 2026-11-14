"""Experiment record. Change models or thresholds here, not inside the pipeline."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
POLICY_DIR = DATA_DIR / "policies"
EVAL_PATH = DATA_DIR / "eval" / "gold.jsonl"
TRAIN_PATH = DATA_DIR / "finetune" / "train.jsonl"
ARTIFACTS = ROOT / "artifacts"
CHROMA_DIR = ARTIFACTS / "chroma"
CHUNKS_PATH = ARTIFACTS / "chunks.json"
EMBEDDINGS_PATH = ARTIFACTS / "embeddings.npy"
LORA_DIR = ARTIFACTS / "lora"
TRAIN_LOG_PATH = ARTIFACTS / "train_log.json"
METRICS_PATH = ARTIFACTS / "metrics.json"

# CPU laptop, 12 GB RAM, no NVIDIA GPU.
# Flan-T5-small is a real seq2seq model that finishes LoRA on CPU.
# Flan-T5-base is a one-line swap when a GPU or more RAM is available.
# A 7B Llama does not fit this machine, and an API model would hide the training loop.
GEN_MODEL = "google/flan-t5-small"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
COLLECTION_NAME = "policies"

# LoRA on 32 examples. Rank 8 limits how much clause text the adapter can store.
# The submitted run is 5e-4 for 12 epochs. 1e-4 for 3 epochs did not leave the zero init.
# Alpha 32 is a scale of 4, the usual pairing with a small rank.
# q and v are the standard T5 attention targets and keep the adapter CPU-sized.
LORA_R = 8
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGETS = ["q", "v"]
LEARNING_RATE = 5e-4
NUM_EPOCHS = 12
TRAIN_BATCH = 1
GRAD_ACCUM = 4
MAX_SOURCE_LEN = 384
MAX_TARGET_LEN = 96
SEED = 42

# Retrieval
RRF_K = 60
DENSE_POOL = 10
BM25_POOL = 10
RERANK_POOL = 8
FINAL_K = 3

# Grounding gate. Set from artifacts/metrics.json on this wording set.
# Answerable top-hit cosine similarity is 0.44 to 0.89.
# "CEO salary" and "capital of France" land at 0.14 and 0.00, with rerank
# scores near -11. 0.35 sits in that gap. The rerank bar is a backstop for a
# high cosine that is still obviously off-topic; genuine clauses in this set
# stay above it or clear the cosine bar.
DENSE_MIN = 0.35
RERANK_MIN = -8.0

MAX_QUESTION_CHARS = 1000
GENERATE_MAX_NEW_TOKENS = 80
GENERATE_BEAMS = 2

DISCLAIMER = (
    "Synthetic Northwind Assurance wording for a proof of concept. "
    "Not an insurance offer and not a claim decision."
)
