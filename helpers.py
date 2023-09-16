from typing import Dict


def revision_quiz_json_builder(source_text: str) -> str:
    """
    Generate a revision quiz in JSON form.
    :param source_text: The source text to be used.
    :return: The generated quiz; should be parsable into valid JSON.
    """
    prompt = """
        Write a set of multiple-choice quiz questions with three to four options each 
        to review and internalise the following information.

        The quiz should be returned in a JSON format so that it can be displayed and undertaken by the user.
        The answer should be a list of integers corresponding to the indices of the correct answers.
        If there is only one correct answer, the answer should be a list of one integer.
        Also return an explanation for each answer, and a quote from the source text to support the answer.

        The goal of the quiz is to provide a revision exercise, 
        so that the user can internalise the information presented in this passage.
        The quiz questions should only cover information explicitly presented in this passage. 
        The number of questions can be anything from one to 10, depending on the volume of information presented.     

        Sample quiz question:

        {
            "question": "What is the capital of France?",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "answer": [0],
            "explanation": "Paris is the capital of France",
            "source passage": "SOME PASSAGE EXTRACTED FROM THE INPUT TEXT"
        }

        Sample quiz set:

        [
            {
                "question": "What is the capital of France?",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "answer": [0],
                "explanation": "Paris is the capital of France",
                "source passage": "SOME PASSAGE EXTRACTED FROM THE INPUT TEXT"
            },
            {
                "question": "What is the capital of Spain?",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "answer": [3],
                "explanation": "Madrid is the capital of Spain",
                "source passage": "SOME PASSAGE EXTRACTED FROM THE INPUT TEXT"
            }
        ]

        ======= Source Text =======

        """ + source_text + """

        ======= Questions =======

    """
    return prompt


def plaintext_summary_builder(source_text: str) -> str:
    """
    Generate a plaintext summary of the source text.
    :param source_text: The source text to be used.
    :return: The summary.
    """
    prompt = f"""
    Summarize the following into bullet points that presents the core concepts.
    This should be in plain language that will help the reader best understand the core concepts,
    so that they can internalise the ideas presented in this passage.

    The bullet points should start at a high level,
    and nested to go into further details if necessary

    ==============

    {source_text}

    ==============

    Summary:

    """
    return prompt


def get_glossary_builder(source_text: str) -> str:
    prompt = f"""
    Return a glossary of key terms or jargon from the source text
    to help someone reading this material understand the text.
    Each explanation should be in as plain and clear language as possible.
    For this task, it is acceptable to rely on information outside of the source text.

    The output should be in the following Markdown format:

    - **TERM A**: EXPLANATION A 
    - **TERM B**: EXPLANATION B
    - ...

    ====== Source text =======

    {source_text}

    ====== Glossary =======

    """
    return prompt


def question_json_to_markdown(quiz_question: Dict) -> str:
    md_return = ""
    for key in quiz_question:
        if key not in ['question', 'options', 'answer', 'explanation', 'source passage']:
            raise ValueError(f"Quiz question has unexpected key {key}")
        if key == 'question':
            md_return += f"\n\n**{quiz_question[key]}**\n"
        elif key == 'options':
            for i, option in enumerate(quiz_question[key]):
                md_return += f"- [ ] {i+1}: {option}\n"

    return md_return


def answer_json_to_markdown(quiz_question: Dict) -> str:
    md_return = ""
    for key in quiz_question:
        if key not in ['question', 'options', 'answer', 'explanation', 'source passage']:
            raise ValueError(f"Quiz question has unexpected key {key}")
        if key == 'question':
            md_return += f"\n\n**{quiz_question[key]}**"
        elif key == 'answer':
            answers_str = [str(i+1) for i in quiz_question[key]]
            md_return += f"\n\n**Correct answer(s)**:" + ','.join(answers_str)
        elif key == 'explanation':
            md_return += f"\n\n**Explanation**: {quiz_question[key]}"
        elif key == 'source passage':
            md_return += f"\n\n**Source passage**: {quiz_question[key]}"

    return md_return


def quiz_set_json_to_markdown(quiz_set: Dict) -> (str, str):
    questions_md_return = ""
    for quiz_question in quiz_set:
        questions_md_return += question_json_to_markdown(quiz_question)
        questions_md_return += "\n"

    answers_md_return = ""
    for quiz_question in quiz_set:
        answers_md_return += answer_json_to_markdown(quiz_question)
        answers_md_return += "\n"

    return questions_md_return, answers_md_return
