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

# === 原本的 Embedding 搜尋（初篩用）===
def search_similar_embedding(query, top_k=5):
    """用 embedding 快速篩選候選文件"""
    q_emb = embed_text(query)
    
    sims = []
    for d_emb in embeddings:
        sim = np.dot(q_emb, d_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(d_emb))
        sims.append(sim)
    
    sorted_idx = np.argsort(sims)[::-1]
    return [docs[i] for i in sorted_idx[:top_k]], sims


# === 🔥 新增：Reranker 重排序 ===
def rerank_with_gemini(query, candidates):
    """使用 Gemini 對候選文件重新打分數"""
    
    print(f"\n🔄 [Reranker] 正在重新評估 {len(candidates)} 個候選...")
    
    scores = []
    for idx, doc in enumerate(candidates):
        # 用 Gemini 直接評分：問題和答案的相關度
        prompt = f"""請評估以下「問題」和「FAQ 內容」的相關度。

問題：{query}

FAQ 內容：
{doc}

請只回答一個 0-100 的數字分數：
- 100分：完全相關，FAQ 直接回答了問題
- 50分：部分相關，有提到相關主題
- 0分：完全不相關

分數："""
        
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                prompt, 
                generation_config={"temperature": 0}
            )

            # 印出 response 的原始內容
            print(f"  候選 {idx+1} 回覆：{response.text.strip()}")

            # 提取數字分數
            score_text = response.text.strip()
            score = float(''.join(filter(str.isdigit, score_text)))
            scores.append(score)
            
            print(f"  候選 {idx+1}: {score:.0f} 分 → {doc[:50]}...")
            
        except Exception as e:
            print(f"  候選 {idx+1}: 評分失敗 ({e})")
            scores.append(0)
    
    return scores


# === 主搜尋函數（含完整 debug）===
def search_with_rerank(query, top_k=2):
    """
    兩階段檢索：
    1. Embedding 快速篩選前 5 名
    2. Reranker 精準重排序，取前 top_k 名
    """
    
    print("\n" + "="*60)
    print(f"🔍 問題：{query}")
    print("="*60)
    
    # === 階段 1：Embedding 初篩 ===
    print("\n【階段 1】Embedding 快速篩選")
    candidates, emb_scores = search_similar_embedding(query, top_k=5)
    
    print("\n📊 Embedding 相似度分數：")
    sorted_idx = np.argsort(emb_scores)[::-1][:5]
    for rank, i in enumerate(sorted_idx, 1):
        print(f"  第 {rank} 名: {emb_scores[i]:.3f} → {docs[i][:60]}...")
    
    # === 階段 2：Reranker 重排序 ===
    print("\n【階段 2】Reranker 精準重排")
    rerank_scores = rerank_with_gemini(query, candidates)
    
    # 排序
    rerank_idx = np.argsort(rerank_scores)[::-1]
    
    print("\n🏆 最終排序結果：")
    for rank, i in enumerate(rerank_idx[:top_k], 1):
        print(f"  第 {rank} 名: {rerank_scores[i]:.0f} 分")
        print(f"         → {candidates[i][:60]}...")
    
    print("\n" + "="*60)
    
    # 回傳最終結果
    return [candidates[i] for i in rerank_idx[:top_k]]


# === 主程式 ===
if __name__ == "__main__":
    question = input("\n請輸入問題：")
    
    # 使用 Reranker 檢索
    context_list = search_with_rerank(question, top_k=2)
    context = "\n".join(f"[資料來源{i+1}]\n{c}" for i, c in enumerate(context_list))
    
    # === 生成答案 ===
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
    
    print("\n💬 正在生成答案...")
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt, generation_config={"temperature": 0.2})
    
    print("\n🤖 Gemini 回覆：")
    print(response.text)
    print("\n" + "="*60)