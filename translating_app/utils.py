# type: ignore
from src.llm_translator.translator import translate_text
from src.llm_translator.utils import (
    read_docx,
    read_pptx,
    read_excel,
    calculate_meteor_score,
    embedding_similarity,
)


def process_docx_file(
    input_file_path, model, glossary, source_lang, target_lang, trace
):
    # Read .docx content
    input_text = read_docx(input_file_path)

    # Translate the text
    translated_text = translate_text(
        input_text,
        model=model,
        glossary=glossary,
        source_lang=source_lang,
        target_lang=target_lang,
        trace=trace,
    )

    return translated_text, input_text


def process_pptx_file(
    input_file_path, model, glossary, source_lang, target_lang, trace
):
    # Read .pptx content
    slides_content = read_pptx(input_file_path)

    # Translate each text in each slide individually
    translated_content = []
    original_texts = []
    translated_texts = []

    for slide_texts in slides_content:
        translated_slide_texts = []
        for shape_idx, text in slide_texts:
            original_texts.append(text)
            translated_text = translate_text(
                text,
                model=model,
                glossary=glossary,
                source_lang=source_lang,
                target_lang=target_lang,
                trace=trace,
            )
            translated_slide_texts.append((shape_idx, translated_text))
            translated_texts.append(translated_text)
        translated_content.append(translated_slide_texts)

    # Flatten texts for evaluation
    original_input = "\n".join(original_texts)
    translated_output_text = "\n".join(translated_texts)

    return translated_content, original_input, translated_output_text


def process_xlsx_file(
    input_file_path, model, glossary, source_lang, target_lang, trace
):
    # Read .xlsx content as a list of lists of cell content
    excel_content = read_excel(input_file_path)

    # Flatten the Excel content into a single string, preserving row and cell structure
    flattened_text = "".join(
        ["\t".join(str(cell) if cell else "" for cell in row) for row in excel_content]
    )

    # Translate the entire content at once
    translated_text = translate_text(
        flattened_text,
        model=model,
        glossary=glossary,
        source_lang=source_lang,
        target_lang=target_lang,
        trace=trace,
    )

    # Split translated text back into rows and cells
    translated_content = [row.split("\t") for row in translated_text.split("\n")]

    # Ensure all rows have the same number of cells as the original content
    for i, row in enumerate(translated_content):
        while len(row) < len(excel_content[i]):
            row.append("")

    return translated_content, flattened_text, translated_text


def evaluate_translation(
    evaluation_method,
    original_input,
    translated_output_text,
    source_lang,
    target_lang,
    model,
    trace,
    reference_content=None,
):
    span = trace.span(
        name="Evaluating translation",
        input={
            "original_input": original_input,
            "translated_output": translated_output_text,
            "reference_content": reference_content,
            "evaluation method": evaluation_method,
        },
    )
    if evaluation_method == "reference_file":
        score = embedding_similarity(reference_content, translated_output_text)
    elif evaluation_method == "reference_text":
        # Compare translated output with reference content
        score = calculate_meteor_score(reference_content, translated_output_text)
    elif evaluation_method == "self_evaluation":
        # Back-translate the translated output
        back_translated_text = translate_text(
            translated_output_text,
            model=model,
            source_lang=target_lang,
            target_lang=source_lang,
            trace=trace,
        )
        # Compare back-translated text with original input
        score = embedding_similarity(original_input, back_translated_text)
    elif evaluation_method == "no_evaluation":
        score = None
    else:
        # Handle invalid evaluation method
        score = None
    if span:
        span.end(output=score)
    return score
