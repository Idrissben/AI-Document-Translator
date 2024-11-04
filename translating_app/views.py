# type: ignore
import os
import json
from langfuse import Langfuse
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_protect
from src.llm_translator.translator import initialize_model
from src.llm_translator.utils import (
    read_docx,
    write_docx,
    read_pptx,
    write_pptx,
    read_excel,
    write_excel,
)
from .utils import (
    process_docx_file,
    process_pptx_file,
    process_xlsx_file,
    evaluate_translation,
)

langfuse = Langfuse()


@csrf_protect
def upload_and_translate(request):
    if request.method == "POST" and request.FILES.get("document"):
        try:
            # Get form data
            uploaded_file = request.FILES["document"]
            evaluation_method = request.POST.get("evaluation_method")
            source_lang = request.POST.get("source_language", "auto")
            target_lang = request.POST.get("target_language", "en")
            glossary_file = request.FILES.get("glossary")

            # Validate file size (10MB limit)
            if uploaded_file.size > 10 * 1024 * 1024:
                return JsonResponse(
                    {"error": "File size exceeds 10MB limit"}, status=400
                )

            # Set up temporary directory
            temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
            os.makedirs(temp_dir, exist_ok=True)

            # Save the uploaded file
            temp_file_name = os.path.join("temp", uploaded_file.name)
            temp_file_path = default_storage.save(temp_file_name, uploaded_file)
            temp_file_full_path = default_storage.path(temp_file_path)

            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            # Initialize model
            model = initialize_model("gpt-4o")

            # Load glossary if provided
            if glossary_file:
                glossary = json.load(glossary_file)
            else:
                glossary = None

            # Initialize langfuse tracing
            trace = langfuse.trace(name="AI Document Translator")

            # Process based on file type
            if file_extension == ".docx":
                translated_output, original_input = process_docx_file(
                    temp_file_full_path,
                    model,
                    glossary,
                    source_lang,
                    target_lang,
                    trace,
                )

                # Save translated .docx file
                output_file_name = f"translated_{target_lang}_{uploaded_file.name}"
                output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_name)
                write_docx(translated_output, output_file_path)

                translated_output_text = translated_output  # For evaluation

            elif file_extension == ".pptx":
                (
                    translated_content,
                    original_input,
                    translated_output_text,
                ) = process_pptx_file(
                    temp_file_full_path,
                    model,
                    glossary,
                    source_lang,
                    target_lang,
                    trace,
                )

                # Save translated .pptx file
                output_file_name = f"translated_{target_lang}_{uploaded_file.name}"
                output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_name)
                write_pptx(translated_content, output_file_path, temp_file_full_path)

            elif file_extension == ".xlsx":
                (
                    translated_content,
                    original_input,
                    translated_output_text,
                ) = process_xlsx_file(
                    temp_file_full_path,
                    model,
                    glossary,
                    source_lang,
                    target_lang,
                    trace,
                )

                # Save translated .xlsx file
                output_file_name = f"translated_{target_lang}_{uploaded_file.name}"
                output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_name)
                write_excel(translated_content, output_file_path)

            else:
                return JsonResponse({"error": "Unsupported file format"}, status=400)

            # Handle evaluation method
            reference_content = None
            if evaluation_method == "reference_file":
                reference_file = request.FILES.get("reference_file")
                if not reference_file:
                    return JsonResponse(
                        {"error": "Reference file not provided"}, status=400
                    )

                # Save and read the reference file
                ref_file_name = os.path.join("temp", reference_file.name)
                ref_file_path = default_storage.save(ref_file_name, reference_file)
                ref_file_full_path = default_storage.path(ref_file_path)
                ref_file_extension = os.path.splitext(reference_file.name)[1].lower()

                # Read reference content based on file type
                if ref_file_extension == ".docx":
                    reference_content = read_docx(ref_file_full_path)
                elif ref_file_extension == ".pptx":
                    slides_content = read_pptx(ref_file_full_path)
                    reference_texts = [
                        text for slide in slides_content for _, text in slide
                    ]
                    reference_content = "\n".join(reference_texts)
                elif ref_file_extension == ".xlsx":
                    excel_content = read_excel(ref_file_full_path)
                    reference_texts = [
                        str(cell) for row in excel_content for cell in row
                    ]
                    reference_content = "\n".join(reference_texts)
                else:
                    return JsonResponse(
                        {"error": "Unsupported reference file format"}, status=400
                    )

                # Clean up reference file
                default_storage.delete(ref_file_path)

            elif evaluation_method == "reference_text":
                reference_content = request.POST.get("reference_text")
                if not reference_content:
                    return JsonResponse(
                        {"error": "Reference text not provided"}, status=400
                    )
            elif evaluation_method == "self_evaluation":
                # No additional data needed for self-evaluation
                pass
            elif evaluation_method == "no_evaluation":
                # No evaluation needed
                pass
            else:
                return JsonResponse({"error": "Invalid evaluation method"}, status=400)

            # Evaluate translation
            score = evaluate_translation(
                evaluation_method,
                original_input,
                translated_output_text,
                source_lang,
                target_lang,
                model,
                trace,
                reference_content=reference_content,
            )

            translated_file_url = settings.MEDIA_URL + output_file_name

            context = {
                "translated_file_url": translated_file_url,
                "score": score,
                "message": "The document has been translated.",
            }

            # Clean up temporary files
            default_storage.delete(temp_file_path)
            # Note: Do not delete output_file_path yet, as it's needed for download

            return render(request, "translating_app/translation_complete.html", context)

        except Exception as e:
            # Log the exception (optional)
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("An error occurred during file upload and translation.")

            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "translating_app/upload.html")
