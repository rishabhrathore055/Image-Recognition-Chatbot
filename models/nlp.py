from transformers import pipeline

def load_nlp_model():
    return pipeline("question-answering", model="deepset/roberta-base-squad2")

def answer_question(model, question, context):
    result = model(question=question, context=context)
    return result['answer']
