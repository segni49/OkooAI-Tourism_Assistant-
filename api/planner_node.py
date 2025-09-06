from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from api.adaptive_retriever import get_adaptive_retriever
import logging

# ✅ Prompt for grounded itinerary generation
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a travel itinerary planner for Ethiopia.
Use ONLY the provided context to generate a multi-day itinerary.
If the context does not contain enough information, respond exactly with:
'I do not know and it is not in the data and context provided to me'"""),
    ("system", "Context: {context}"),
    ("human", "{input}")
])

# ✅ Grounded itinerary planner with retrieval
def plan_trip(state):
    query = state["input"].lower()
    model = state.get("model", "qwen:0.5b")

    # ✅ Block factual queries from being processed here
    if any(kw in query for kw in ["who", "won", "what", "when", "where", "how"]):
        logging.info("🚫 Detected factual query inside plan_trip. Returning strict fallback.")
        return {
            **state,
            "answer": "I do not know and it is not in the data and context provided to me",
            "source_documents": []
        }

    # ✅ Retrieve relevant chunks from Chroma
    retriever = get_adaptive_retriever(query)
    docs = retriever.invoke(query)
    logging.info(f"📚 Retrieved {len(docs)} chunks for itinerary")

    if not docs:
        logging.info("❌ No relevant context found. Returning strict fallback.")
        return {
            **state,
            "answer": "I do not know and it is not in the data and context provided to me",
            "source_documents": []
        }

    # ✅ Generate itinerary using retrieved context
    llm = Ollama(model=model)
    chain = create_stuff_documents_chain(llm=llm, prompt=planner_prompt)
    result = chain.invoke({"input": query, "context": docs})

    answer = result["answer"] if isinstance(result, dict) else str(result)
    logging.info(f"🧳 Grounded itinerary: {answer}")

    return {
        **state,
        "answer": answer,
        "source_documents": docs
    }