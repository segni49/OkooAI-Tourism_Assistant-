from langchain_community.llms import Ollama
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from api.adaptive_retriever import get_adaptive_retriever
from typing import List, Dict
import logging

# ✅ Prompt for hotel comparison
hotel_prompt = ChatPromptTemplate.from_messages([
    ("system", "Compare hotels based on location, amenities, pricing, and reviews using ONLY the provided context. Do not guess or hallucinate."),
    ("system", "Context: {context}"),
    ("human", "{input}")
])

# ✅ Node: Compare hotels with strict fallback
def compare_hotels(state: Dict) -> Dict:
    query = state["input"]
    retriever = get_adaptive_retriever(query)
    docs: List[Document] = retriever.invoke(query)

    if not docs:
        logging.info("❌ No hotel documents found. Returning fallback.")
        return {**state, "answer": "I do not know", "source_documents": []}

    llm = Ollama(model=state.get("model", "qwen:0.5b"))
    chain = create_stuff_documents_chain(llm=llm, prompt=hotel_prompt)
    result = chain.invoke({"input": query, "context": docs})

    answer = result["answer"] if isinstance(result, dict) and "answer" in result else str(result)
    logging.info(f"🏨 Hotel comparison answer: {answer}")

    return {**state, "answer": answer, "source_documents": docs}