import streamlit as st
import json
import weaviate
import os
from ragwrangler import RAGTask, set_openai_api_key
from helpers import (
    plaintext_summary_builder, get_glossary_builder, revision_quiz_json_builder,
    quiz_set_json_to_markdown
)


def main():
    st.set_page_config(layout="wide")
    st.title('StudyBuddAI')
    st.text("Note that much of this is LLM-generated and may contain errors.")

    with st.expander("Set your API key here:"):
        api_key = st.text_input("API key:")

    if api_key != "" and len(api_key) > 32:
        set_openai_api_key(api_key)

        use_gpt4 = st.checkbox("Use GPT-4")

        if use_gpt4:
            model_name = "gpt-4"
        else:
            model_name = "gpt-3.5-turbo"

        source_text = st.text_area('Input text here:')

        col1, col2 = st.columns([2, 2])

        client = weaviate.Client(
            url=os.environ['WCS_URL'],
            auth_client_secret=weaviate.AuthApiKey(os.environ['WCS_ADMIN_KEY']),
            additional_headers={"X-OpenAI-Api-Key": api_key}
        )

        if len(source_text) > 10:
            summary_task = RAGTask(client=client, task_prompt_builder=plaintext_summary_builder)
            glossary_task = RAGTask(client=client, task_prompt_builder=get_glossary_builder)
            quiz_task = RAGTask(client=client, task_prompt_builder=revision_quiz_json_builder)

            with col1:
                st.subheader('Summary')
                with st.expander("See summary"):
                    st.write(summary_task.get_output(source_text))

                quiz_str = quiz_task.get_output(source_text, model_name=model_name)
                quiz_json = json.loads(quiz_str)
                questions_md_return, answers_md_return = quiz_set_json_to_markdown(quiz_json)
                st.subheader('Quiz')
                with st.expander("See quiz"):
                    st.write(questions_md_return)

            with col2:
                st.subheader('Glossary')
                with st.expander("See glossary"):
                    st.write(glossary_task.get_output(source_text))
                st.subheader('Answers')
                with st.expander("See quiz answers"):
                    st.write(answers_md_return)

    else:
        st.write("You need an OpenAI API key to use this app. Please enter it above.")


if __name__ == '__main__':
    main()
