#type: ignore
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_protect
from src.translater.translator import initialize_model, translate_text
from src.translater.utils import (
    read_docx,
    write_docx,
    read_pptx,
    write_pptx,
    read_excel,
    write_excel,
    calculate_metric,
)
import os
import json


@csrf_protect
def upload_and_translate(request):
    if request.method == "POST" and request.FILES.get("document"):
        try:
            # Get form data
            uploaded_file = request.FILES["document"]
            ground_truth = request.POST.get("ground_truth_text")
            glossary_file = request.FILES.get("glossary")
            source_lang = request.POST.get("source_language", "auto")
            target_lang = request.POST.get("target_language", "en")

            # Validate file size (10MB limit)
            if uploaded_file.size > 10 * 1024 * 1024:
                return JsonResponse(
                    {"error": "File size exceeds 10MB limit"}, status=400
                )

            # Save the uploaded file and get the absolute path
            temp_file_name = "temp/" + uploaded_file.name
            temp_file_path = default_storage.save(temp_file_name, uploaded_file)
            temp_file_full_path = default_storage.path(temp_file_path)

            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            # Initialize model
            model = initialize_model("gpt-4o")

            if glossary_file:
                glossary = json.load(glossary_file)
            else:
                glossary = None

            # Initialize variable to hold translated output
            translated_output = None

            # Process based on file type
            if file_extension == ".docx":
                # Read .docx content using the absolute path
                input_text = read_docx(temp_file_full_path)

                # Translate the text
                translated_text = translate_text(
                    input_text,
                    model=model,
                    glossary=glossary,
                    source_lang=source_lang,
                    target_lang=target_lang,
                )
                translated_output = translated_text

                # Save translated .docx file under MEDIA_ROOT
                output_file_name = f"translated_{target_lang}_{uploaded_file.name}"
                output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_name)
                write_docx(translated_text, output_file_path)

            elif file_extension == ".pptx":
                # Read .pptx content slide by slide
                slides_content = read_pptx(temp_file_full_path)

                # Translate each slide individually
                translated_content = [
                    translate_text(
                        slide_text,
                        model=model,
                        glossary=glossary,
                        source_lang=source_lang,
                        target_lang=target_lang,
                    )
                    for slide_text in slides_content
                ]
                translated_output = "\n".join(translated_content)

                # Save translated .pptx file under MEDIA_ROOT
                output_file_name = f"translated_{target_lang}_{uploaded_file.name}"
                output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_name)
                write_pptx(translated_content, output_file_path, temp_file_full_path)

            elif file_extension == ".xlsx":
                # Read .xlsx content
                excel_content = read_excel(temp_file_full_path)

                # Translate each row individually
                translated_content = translate_text(
                    excel_content,
                    model=model,
                    glossary=glossary,
                    source_lang=source_lang,
                    target_lang=target_lang,
                )
                translated_output = translated_content  # Adjust as needed

                # Save translated .xlsx file under MEDIA_ROOT
                output_file_name = f"translated_{target_lang}_{uploaded_file.name}"
                output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_name)
                write_excel(translated_content, output_file_path)

            else:
                return JsonResponse({"error": "Unsupported file format"}, status=400)

            # Prepare context for the template
            if ground_truth and ground_truth.strip():
                score = calculate_metric(ground_truth, translated_output)
            else:
                score = None

            translated_file_url = settings.MEDIA_URL + output_file_name

            context = {
                "translated_file_url": translated_file_url,
                "score": score,
                "message": "The document has been translated.",
            }

            # Clean up temporary files
            default_storage.delete(temp_file_path)
            # Note: Do not delete output_file_path yet, as it's needed for download

            return render(request, "llm_translator/translation_complete.html", context)

        except Exception as e:
            # Log the exception (optional)
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("An error occurred during file upload and translation.")

            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "llm_translator/upload.html")
