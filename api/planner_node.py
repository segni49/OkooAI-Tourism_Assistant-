from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
import logging

# ✅ Prompt for itinerary generation
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a travel itinerary planner for Ethiopia.
Based on the user's request, generate a detailed multi-day itinerary.
Include activities, locations, and travel tips. Format clearly by day.

If the request is vague, make reasonable assumptions and explain them."""), 
    ("human", "{input}")
])

# ✅ Guarded itinerary planner
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

    # ✅ Proceed with itinerary generation
    llm = Ollama(model=model)
    chain = planner_prompt | llm
    result = chain.invoke({"input": query})

    logging.info(f"🧳 Planned itinerary: {result}")
    return {
        **state,
        "answer": result,
        "source_documents": []
    }