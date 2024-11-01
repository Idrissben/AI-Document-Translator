from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def initialize_model(model: str = "gpt-4o"):
    if model == "gpt-4o":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(temperature=0, model="gpt-4o")
    else:
        print("Model Not Supported Yet")


def translate_text(
    text,
    model,
    source_lang="English",
    target_lang="French",
    glossary=None,
):
    parser = StrOutputParser()

    if glossary:
        glossary_terms = "\n".join(
            [f"{key}: {value}" for key, value in glossary.items()]
        )
        system_template = f"""
                            You are a translation assistant that translates text from {source_lang} to {target_lang}.
                            Please use the following glossary for specific terms:
                            {glossary_terms}

                            Translate the following text preserving the formatting:

                            """
    else:
        system_template = f"""
                        Translate the following text from {source_lang} to {target_lang}, preserving the formatting:

                        """
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text}")]
    )
    chain = prompt_template | model | parser
    translated_text = chain.invoke({"text": text})
    return translated_text.strip()
