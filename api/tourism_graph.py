from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_community.llms import Ollama
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from typing import TypedDict, List, Optional

from api.intent_classifier import classify_intent
from api.adaptive_retriever import get_adaptive_retriever
from api.self_reflective_rag import reflect_on_answer
from api.planner_node import plan_trip
from api.hotel_comparison_node import compare_hotels
from api.explore_place_node import explore_place

import logging

# ✅ LangGraph state schema
class TourismState(TypedDict):
    input: str
    chat_history: List[str]
    model: str
    context: Optional[List[Document]]
    answer: Optional[str]
    source_documents: Optional[List[Document]]
    intent: Optional[str]

# ✅ Strict prompt for grounded answers only
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a tourism assistant for Ethiopia.
You must answer ONLY using the provided context. If the context does not contain the answer, respond exactly with:
'I do not know and it is not in the data and context provided to me'"""),
    ("system", "Context: {context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# ✅ Node: Classify user intent
def classify_node(state: TourismState) -> TourismState:
    query = state["input"]
    model = state.get("model", "qwen:0.5b")
    intent = classify_intent(query, model)
    logging.info(f"🧭 Classified intent: {intent}")
    return {**state, "intent": intent}

# ✅ Node: Retrieve relevant context
def retrieve_context(state: TourismState) -> TourismState:
    query = state["input"]
    retriever = get_adaptive_retriever(query)
    docs = retriever.invoke(query)
    logging.info(f"📚 Retrieved {len(docs)} chunks")
    return {**state, "context": docs}

# ✅ Node: Generate answer from context
def generate_answer(state: TourismState) -> TourismState:
    # ✅ Enforce strict fallback if no context is retrieved
    if not state.get("context") or len(state["context"]) == 0:
        logging.info("❌ No context available. Returning strict fallback.")
        return {
            **state,
            "answer": "I do not know and it is not in the data and context provided to me",
            "source_documents": []
        }

    # ✅ Proceed only if context exists
    llm = Ollama(model=state.get("model", "qwen:0.5b"))
    qa_chain = create_stuff_documents_chain(llm=llm, prompt=qa_prompt)
    result = qa_chain.invoke({
        "input": state["input"],
        "context": state["context"],
        "chat_history": state.get("chat_history", [])
    })

    answer = result["answer"] if isinstance(result, dict) and "answer" in result else str(result)
    logging.info(f"🗣️ Generated answer: {answer}")

    return {
        **state,
        "answer": answer,
        "source_documents": state["context"]
    }

# ✅ Node: Reflect and retry if needed
def reflect_and_retry(state: TourismState) -> TourismState:
    llm = Ollama(model=state.get("model", "qwen:0.5b"))
    verdict = reflect_on_answer(llm, state["input"], state["answer"])

    if verdict == "retry":
        logging.info("🔁 Retrying answer generation...")
        return generate_answer(state)
    elif verdict == "unknown":
        logging.info("🤷‍♂️ Answer unsupported. Returning strict fallback.")
        state["answer"] = "I do not know and it is not in the data and context provided to me"

    return state

# ✅ Node: Unsupported intent fallback
def unsupported_node(state: TourismState) -> TourismState:
    logging.info("🚫 Unsupported query detected.")
    return {
        **state,
        "answer": "I do not know and it is not in the data and context provided to me"
    }

# ✅ Routing function
def route_by_intent(state: TourismState) -> str:
    return state["intent"]

# ✅ Build the LangGraph workflow
def get_tourism_graph(model: str = "qwen:0.5b"):
    builder = StateGraph(TourismState)

    builder.add_node("classify", RunnableLambda(classify_node))
    builder.add_node("retrieve", RunnableLambda(retrieve_context))
    builder.add_node("answer", RunnableLambda(generate_answer))
    builder.add_node("reflect", RunnableLambda(reflect_and_retry))
    builder.add_node("plan", RunnableLambda(plan_trip))
    builder.add_node("compare", RunnableLambda(compare_hotels))
    builder.add_node("explore", RunnableLambda(explore_place))
    builder.add_node("unsupported", RunnableLambda(unsupported_node))

    builder.set_entry_point("classify")

    builder.add_conditional_edges("classify", route_by_intent, {
        "ask_fact": "retrieve",
        "explore_place": "explore",
        "compare_hotels": "compare",
        "plan_trip": "plan",
        "unsupported": "unsupported"
    })

    builder.add_edge("retrieve", "answer")
    builder.add_edge("answer", "reflect")
    builder.add_edge("reflect", END)
    builder.add_edge("plan", END)
    builder.add_edge("compare", END)
    builder.add_edge("explore", END)
    builder.add_edge("unsupported", END)

    graph = builder.compile()
    return lambda inputs: graph.invoke({**inputs, "model": model})