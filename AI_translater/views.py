#type: ignore
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
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
)
import os


@csrf_protect
def upload_and_translate(request):
    if request.method == "POST" and request.FILES.get("document"):
        try:
            # Get form data
            uploaded_file = request.FILES["document"]
            source_lang = request.POST.get("source_language", "auto")
            target_lang = request.POST.get("target_language", "en")

            # Validate file size (10MB limit)
            if uploaded_file.size > 10 * 1024 * 1024:
                return JsonResponse(
                    {"error": "File size exceeds 10MB limit"}, status=400
                )

            # Save the uploaded file
            temp_file_path = default_storage.save(
                "temp/" + uploaded_file.name, uploaded_file
            )
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            # Initialize model
            model = initialize_model("gpt-4o")

            # Process based on file type
            if file_extension == ".docx":
                # Read .docx content
                input_text = read_docx(temp_file_path)

                # Translate the text
                translated_text = translate_text(
                    input_text,
                    model=model,
                    source_lang=source_lang,
                    target_lang=target_lang,
                )

                # Save translated .docx file
                output_file_path = f"temp/translated_{target_lang}_{uploaded_file.name}"
                write_docx(translated_text, output_file_path)

            elif file_extension == ".pptx":
                # Read .pptx content slide by slide
                slides_content = read_pptx(temp_file_path)

                # Translate each slide individually
                translated_content = [
                    translate_text(
                        slide_text,
                        model=model,
                        source_lang=source_lang,
                        target_lang=target_lang,
                    )
                    for slide_text in slides_content
                ]

                # Save translated .pptx file
                output_file_path = f"temp/translated_{target_lang}_{uploaded_file.name}"
                write_pptx(translated_content, output_file_path, temp_file_path)

            elif file_extension == ".xlsx":
                # Read .xlsx content
                excel_content = read_excel(temp_file_path)

                # Translate each row individually
                translated_content = translate_text(
                    excel_content,
                    model=model,
                    source_lang=source_lang,
                    target_lang=target_lang,
                )

                # Save translated .xlsx file
                output_file_path = f"temp/translated_{target_lang}_{uploaded_file.name}"
                write_excel(translated_content, output_file_path)

            else:
                return JsonResponse({"error": "Unsupported file format"}, status=400)

            # Return file for download
            with open(output_file_path, "rb") as f:
                response = HttpResponse(
                    f.read(),
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    if file_extension == ".docx"
                    else "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    if file_extension == ".pptx"
                    else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="translated_{uploaded_file.name}"'
                )

                # Clean up temporary files
                default_storage.delete(temp_file_path)
                default_storage.delete(output_file_path)

                return response

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "AI_translater/upload.html")
