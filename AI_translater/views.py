# type: ignore
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_protect
from src.AI_translater.translator import initialize_model, translate_text
from src.AI_translater.utils import read_docx, write_docx


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

            # Read the content
            input_text = read_docx(temp_file_path)

            # Initialize model
            model = initialize_model("gpt-4o")

            # Translate the text
            translated_text = translate_text(
                input_text,
                model=model,
                source_lang=source_lang,
                target_lang=target_lang,
            )

            # Save translated file
            output_file_path = f"temp/translated_{target_lang}_{uploaded_file.name}"
            write_docx(translated_text, output_file_path)

            # Return file for download
            with open(output_file_path, "rb") as f:
                response = HttpResponse(
                    f.read(),
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
