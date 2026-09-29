from rag_answer import answer_with_context
from bulid_chunk import bulid_chunks

bulid_chunks()

QUESTIONS = [
    "What is this project for?",
    "What does chunker.py do?",
    "How are blank lines handled when splitting source material?",
    "What format do chunk ids use?",
    "How do I rebuild the index?",
    "Where are the split chunks saved?",
    "Which endpoint is called to turn text into a vector?",
    "Why are the vectors normalized?",
    "Where is the embedding model name configured?",
    "Where is the Ollama service address configured?",
    "How does retriever.py rank the retrieval results?",
    "What is the similarity threshold, and what happens to chunks below it?",
    "How many chunks does the retrieve function return by default?",
    "What does rag_answer.py do?",
    "What format does build_context use for each chunk?",
    "What is the QUESTIONS list for?",
    "What does the program return when retrieval finds nothing?",
]

for question in QUESTIONS:
    print("=" * 80)
    print("Q:", question)
    result = answer_with_context(question)
    print(result["answer"])
    print("sources:", result["sources"], "grounded:", result["grounded"])