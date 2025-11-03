import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

# === 初始化 ===
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# === 讀入 FAQ 文件 ===
docs = []
with open("faq.txt", "r", encoding="utf-8") as f:
    chunks = f.read().strip().split("\n\n")
    for chunk in chunks:
        docs.append(chunk.strip())

# === 文字轉向量 ===
def embed_text(text: str):
    """使用 Gemini 的 embedding 模型將文字轉換為向量"""
    res = genai.embed_content(model="models/text-embedding-004", content=text)
    return np.array(res["embedding"])

embeddings = [embed_text(doc) for doc in docs]

# === 相似度搜尋 (含 debug) ===
def search_similar(query, top_k=2):
    """以 cosine similarity 搜尋最相關的 FAQ 段落（含 debug 輸出）"""
    print("\n🔍 [DEBUG] 問題內容：", query)

    # 1️⃣ 取得 query 的 embedding
    q_emb = embed_text(query)

    # 2️⃣ 計算每個段落的 cosine similarity
    sims = []
    for idx, d_emb in enumerate(embeddings):
        sim = np.dot(q_emb, d_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(d_emb))
        sims.append(sim)

    # 3️⃣ 排序後取前 k 名
    sorted_idx = np.argsort(sims)[::-1]

    print("\n📊 [DEBUG] 各 FAQ 相似度分數：")
    for i in sorted_idx:
        print(f"  ({i}) {sims[i]:.3f} → {docs[i][:60]}")

    # 4️⃣ 取前 k 名的索引
    best_idx = sorted_idx[:top_k]

    print("\n🏆 [DEBUG] 選中前 {} 名：".format(top_k))
    for rank, i in enumerate(best_idx, 1):
        print(f"  TOP {rank}: {sims[i]:.3f} → {docs[i][:60]}")

    # 5️⃣ 回傳選中的段落
    return [docs[i] for i in best_idx]


# === 問題 ===
question = input("請輸入問題：")
context_list = search_similar(question)
context = "\n".join(f"[資料來源{i+1}]\n{c}" for i, c in enumerate(context_list))

# === 強化 Prompt ===
prompt = f"""
你是一個客服助理，必須根據我提供的 FAQ 內容回答問題。
這些 FAQ 是系統已經從知識庫中查出的最相似資料來源。
請務必根據它們回答問題，即使內容部份相關，也要根據現有資料進行合理推斷。
不要說「找不到」或「未提及」。

回答時請用繁體中文。

=== 已檢索 FAQ 內容 ===
{context}

=== 使用者問題 ===
{question}
"""

# === 呼叫 Gemini ===
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(prompt, generation_config={"temperature": 0.2})

print("\n🤖 Gemini 回覆：", response.text)