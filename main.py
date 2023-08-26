from enum import Enum
import openai
import streamlit as st
import os
import db


openai.api_key = os.environ["OPENAI_APIKEY"]


class CollectionNames(Enum):
    SUMMARY = 'Summary'


class CollectionProperties(Enum):
    SOURCE_PATH = 'source_path'
    BODY_TEXT = 'body_text'


def call_chatgpt(prompt: str, use_gpt_4: bool = False) -> str:
    if use_gpt_4 is False:
        model_name = "gpt-3.5-turbo"
    else:
        model_name = "gpt-4"

    completion = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system",
             "content": """
                You are a helpful, intelligent, thoughtful assistant who is a great communicator.
                 
                You can communicate complex ideas and concepts in clear, concise language 
                without resorting to domain-specific jargon unless it is entirely necessary.
                
                When you do are not sure of what the answer should be, or whether it is grounded in fact,
                you communicate this to the user to help them make informed decisions
                about how much to trust your outputs. 
                """
             },
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message["content"]


def fetch_current_data(collection_name: str, source_path: str):
    if len(source_path) > 0:
        current_data = db.get(collection_name, source_path)
        if current_data is not None:
            return current_data['data']['Get'][collection_name][0][CollectionProperties.BODY_TEXT]
    else:
        return None


def get_plaintext_summary(source_path: str, source_text: str, use_gpt_4: bool = False) -> str:
    current_data = fetch_current_data(CollectionNames.SUMMARY.value, source_path)
    if current_data is not None:
        return current_data
    else:
        task_prompt = f"""
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
        summary = call_chatgpt(task_prompt, use_gpt_4)

        if len(source_path) > 0:
            data_object = {
                CollectionProperties.SOURCE_PATH.value: source_path,
                CollectionProperties.BODY_TEXT.value: summary
            }

            db.add_object(
                CollectionNames.SUMMARY.value,
                data_object
            )

        return summary


def get_revision_quiz(source_path: str, source_text: str, use_gpt_4: bool = False) -> str:
    task_prompt = f"""
    Write a set of multiple-choice quiz questions with three to four options each to review and internalise the following information.
    The quiz should be written into Markdown so that it can be displayed and undertaken by the user.
    
    The goal of the quiz is to provide a revision exercise, 
    so that the user can internalise the information presented in this passage.
    The quiz questions should only cover information explicitly presented in this passage. 
    The number of questions can be anything from one to 10, depending on the volume of information presented. 
    
    The output should be in markdown format, and should not include answers. It might look like:
    
    QUESTION TEXT
    - [ ] Option 1
    - [ ] Option 2
    - [ ] Option 3
    ...

    ======= Source Text =======

    {source_text}

    ======= Questions =======
    
    """
    return call_chatgpt(task_prompt, use_gpt_4)


def get_quiz_answers(source_path: str, quiz_questions: str, source_text: str, use_gpt_4: bool = False) -> str:
    task_prompt = f"""
    Return the correct answers to all of the following quiz questions, based on the source text
    Each answer should be in the following Markdown format

    - QUESTION 1: 
        - Answer: 
        - Reason: Explain why
        - Source: Quote the minimum relevant source text
    - QUESTION 2:
    ...
    
    ====== Quiz Questions =======
    
    {quiz_questions}

    ====== Source text =======

    {source_text}

    ====== Answers =======

    """
    return call_chatgpt(task_prompt, use_gpt_4)


def get_glossary(source_path: str, source_text: str, use_gpt_4: bool = False) -> str:
    task_prompt = f"""
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
    return call_chatgpt(task_prompt, use_gpt_4)


def get_data(source_path: str):
    if source_path == '1':
        return None
    else:
        st.write("asfadsfs")


def add_to_database(source_path: str, source_text: str):
    if len(source_path) == 0 or len(source_text) == 0:
        pass
    else:
        print(f"Source path: {source_path}")
        print(f"Source text: {source_text}")


def main():
    st.set_page_config(layout="wide")
    st.title('StudyBuddAI')
    use_gpt_4 = st.checkbox('Use GPT-4')
    st.text("Note that much of this is LLM-generated and may contain errors.")
    source_path = st.text_input('Page name in DB (use URL):')
    st.button('Get data from DB', on_click=get_data, args=[source_path])
    col1, col2 = st.columns([2, 2])



    # if objects is None:
    #     source_text = st.text_area('Input text here:')
    #     st.button('Add to database', on_click=add_to_database, args=[source_path, source_text])
    # else:
    #     col1, col2 = st.columns([2, 2])
    #     with col1:
    #         st.header("Revision material")

    # if len(source_text) > 10:
    #     col1, col2 = st.columns([2, 2])
    #
    #     with col1:
    #         st.header("Revision material")
    #         plaintext_summary = get_plaintext_summary(source_path, source_text, use_gpt_4)
    #         with st.expander("Plaintext summary", expanded=True):
    #             st.write(plaintext_summary)
    #         with st.expander("Revision quiz"):
    #             quiz_text = get_revision_quiz(source_path, source_text, use_gpt_4)
    #             st.markdown(quiz_text)
    #
    #     with col2:
    #         st.header("Study aids")
    #         with st.expander("Glossary", expanded=True):
    #             glossary = get_glossary(source_path, source_text, use_gpt_4)
    #             st.write(glossary)
    #         with st.expander("See answers"):
    #             answers = get_quiz_answers(source_path, quiz_text, source_text, use_gpt_4)
    #             st.write(answers)
    #         with st.expander("Source text"):
    #             st.write(source_text)
    #
    # else:
    #     placeholder_text = "Please enter text here"
    #     st.write(placeholder_text)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
