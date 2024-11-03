# type: ignore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.callbacks import get_openai_callback


def initialize_model(model: str = "gpt-4o"):
    if model == "gpt-4o":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(temperature=0, model="gpt-4o")
    else:
        print("Model Not Supported Yet")


def translate_text(
    text, model, source_lang="French", target_lang="English", glossary=None, trace=None
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
    # creates generation
    generation = trace.generation(
        name="translation",
        model=model.model_name,
        model_parameters={
            "maxTokens": model.max_tokens,
            "temperature": model.temperature,
        },
        input=[
            {"role": "system", "content": system_template},
            {"role": "user", "content": f"{text}"},
        ],
    )
    with get_openai_callback() as cb:
        translated_text = chain.invoke({"text": text})
        generation.end(
            output=translated_text,
            usage={
                "input": cb.prompt_tokens,
                "output": cb.completion_tokens,
                "unit": "TOKENS",  # any of: "TOKENS", "CHARACTERS", "MILLISECONDS", "SECONDS", "IMAGES"
                "total_cost": cb.total_cost,
            },
        )
    generation.end()
    return translated_text.strip()
