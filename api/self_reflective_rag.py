from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from typing import Callable, Dict
import logging

# Prompt to evaluate the quality of the answer
reflection_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a critical evaluator of AI-generated answers."),
    ("human", """Evaluate the following answer to a user question. 
Is it vague, hallucinated, or unsupported by the context? 
Respond with one of: 'good', 'retry', or 'unknown'.

Question: {question}
Answer: {answer}""")
])

def reflect_on_answer(llm: Ollama, question: str, answer: str) -> str:
    reflection_chain = reflection_prompt | llm
    result = reflection_chain.invoke({"question": question, "answer": answer})
    verdict = result.strip().lower()
    logging.info(f"🧠 Reflection verdict: {verdict}")
    return verdict

def wrap_with_reflection(rag_chain: Callable[[Dict], Dict], model: str = "qwen:0.5b") -> Callable:
    llm = Ollama(model=model)

    def wrapped(inputs: Dict) -> Dict:
        result = rag_chain(inputs)
        answer = result["answer"]
        question = inputs["input"]

        verdict = reflect_on_answer(llm, question, answer)

        if verdict == "retry":
            logging.info("🔁 Retrying RAG query due to weak answer...")
            result = rag_chain(inputs)  # Re-run once
        elif verdict == "unknown":
            logging.info("🤷‍♂️ Answer deemed unsupported. Returning fallback.")
            result["answer"] = "I don't know based on the documents."

        return result

    return wrapped