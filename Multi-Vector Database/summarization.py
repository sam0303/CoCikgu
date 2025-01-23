import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

os.environ["OPENAI_API_KEY"] = "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"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"

def summarization(texts, tables): 
    prompt_text = """
    You are an assistant tasked with summarizing tables and text.
    Give a concise summary of the table or text.

    Respond only with the summary, no additionnal comment.
    Do not start your message by saying "Here is a summary" or anything like that.
    Just give the summary as it is.

    Table or text chunk: {element}

    """
    model = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # Summary chain
    summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()

    # Summarize text
    text_summaries = summarize_chain.batch(texts, {"max_concurrency": 3})

    # Summarize tables
    tables_html = [table.metadata.text_as_html for table in tables]
    table_summaries = summarize_chain.batch(tables_html, {"max_concurrency": 3})

    return (text_summaries,table_summaries)

def image_summarization(images):
    prompt_template = """Describe the image in detail. For context,
                    the image is part of a English Language Content and Learning Standards document. 
                    Be specific about tables and graphs"""
    messages = [
        (
            "user",
            [
                {"type": "text", "text": prompt_template},
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,{image}"},
                },
            ],
        )
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()


    image_summaries = chain.batch(images)
    return(image_summaries)