from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from api.adaptive_retriever import get_adaptive_retriever
from api.self_reflective_rag import wrap_with_reflection
import logging

# Prompt to reformulate user query based on chat history
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", "Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# Prompt to answer using only retrieved context
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant for tourism in Ethiopia.
Use ONLY the provided context to answer the question. If the context is insufficient, say 'I don't know based on the documents.' Do not guess or hallucinate."""),
    ("system", "Context: {context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

def get_rag_chain(model: str = "qwen:0.5b"):
    llm = Ollama(model=model)

    def wrapped_chain(inputs):
        query = inputs["input"]
        chat_history = inputs.get("chat_history", [])

        # ✅ Use adaptive retriever based on query type
        adaptive_retriever = get_adaptive_retriever(query)

        # ✅ Make it history-aware
        history_aware_retriever = create_history_aware_retriever(
            llm=llm,
            retriever=adaptive_retriever,
            prompt=contextualize_q_prompt
        )

        # ✅ Build the QA chain
        question_answer_chain = create_stuff_documents_chain(
            llm=llm,
            prompt=qa_prompt
        )

        # ✅ Combine retriever + QA chain
        rag_chain = create_retrieval_chain(
            retriever=history_aware_retriever,
            combine_documents_chain=question_answer_chain
        )

        # ✅ Invoke the chain
        result = rag_chain.invoke({
            "input": query,
            "chat_history": chat_history
        })

        return {
            "answer": result["answer"],
            "source_documents": result.get("context", [])
        }

    # ✅ Wrap with self-reflection logic
    return wrap_with_reflection(wrapped_chain, model=model)