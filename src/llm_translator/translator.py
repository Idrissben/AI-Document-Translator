# type: ignore
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback
from langfuse import Langfuse

langfuse = Langfuse()


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
        prompt = langfuse.get_prompt("Translation_with_glossary")
        prompt_template = prompt.compile(
            source_lang=source_lang,
            target_lang=target_lang,
            input=text,
            glossary=glossary,
        )
    else:
        prompt = langfuse.get_prompt("translation_no_glossary")
        prompt_template = prompt.compile(
            source_lang=source_lang,
            target_lang=target_lang,
            input=text,
        )

    chain = model | parser
    generation = trace.generation(
        name="translation",
        model=model.model_name,
        model_parameters={
            "maxTokens": model.max_tokens,
            "temperature": model.temperature,
        },
        input=prompt_template,
    )
    with get_openai_callback() as cb:
        translated_text = chain.invoke(prompt_template)
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
