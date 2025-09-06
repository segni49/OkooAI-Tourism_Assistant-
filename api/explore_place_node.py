from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from api.adaptive_retriever import get_adaptive_retriever
import logging

explore_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a tourism expert for Ethiopia.
Explore the location mentioned in the user's query using ONLY the provided context.
Summarize its geography, history, culture, attractions, and travel tips.

If the context is insufficient, say 'I don't know based on the documents.'"""),
    ("system", "Context: {context}"),
    ("human", "{input}")
])

def explore_place(state):
    query = state["input"]
    model = state.get("model", "qwen:0.5b")
    retriever = get_adaptive_retriever(query)
    docs = retriever.invoke(query)

    llm = Ollama(model=model)
    chain = explore_prompt | llm

    result = chain.invoke({
        "input": query,
        "context": "\n\n".join([doc.page_content for doc in docs])
    })

    logging.info(f"🗺️ Exploration result: {result}")
    return {**state, "answer": result, "source_documents": docs}