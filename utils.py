# utils.py
from random import shuffle

def shuffle_options(questions):
    """Shuffle the options of each question"""
    for q in questions:
        shuffle(q["options"])
    return questions

def check_answer(selected, correct):
    """Check if selected answer is correct"""
    return selected == correct
