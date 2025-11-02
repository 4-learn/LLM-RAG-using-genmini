from ontology_agent_fc_level2 import chat_with_llm

if __name__ == "__main__":
    print("🚗 Ontology × LLM (Level-2 Reasoning) 交通助理啟動！")

    while True:
        q = input("\n請輸入問題（例如『ABC123 違規了嗎？』或『Alice 是高風險嗎？』，或輸入 exit 離開）：").strip()
        if q.lower() in ["exit", "quit"]:
            print("👋 再見！")
            break
        answer = chat_with_llm(q)
        print(f"🤖 {answer}")

