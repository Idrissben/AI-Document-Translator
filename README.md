# Office_translator
An AI-based translator that can translate a given Word, Excel, or Powerpoint document in any given language. 
It accepts .docx, .xlsx, or .pptx files of up to 10 mb, and contains the fellow features:

- You can upload a glossary in the form of a .json file in order to translate some specific terms to a given word.
- You can upload a target translated document in order to evaluate the quality of the translation using the METEOR_SCORE metric.
- You can track the cost and number of token of each generation through Langfuse (currently limited to OpenAI models due to LangChain limitations).

By default, this llm-translator only accepts OpenAI models, but it can easily be modified to use any LLM supported by langchain through the modification of the "initialize_model" function with the desired model.

It is a django application with a single endpoint "upload/" which is currently being received through an html interface.

# Changelog

This documents the list of functionalities already implemented as well as the planned improvements.

## [1.2.0] - 2024-03-11

### Added
- Tests to ensure the app is working

### Improved
- More front improvements
- Fixed a bug on pptx files where the text would be translated twice in each slide
- Renamed folder names to be more explicit


## [1.1.0] - 2024-01-11
### Added
- Token and cost tracking with langfuse
- Addition of other office formats besides word
- Addition of Glossary
- Addition of translation quality metrics

### Improved
- Current front


## [1.0.0] - 2024-01-11
### Added
- Initial release of the project.
- Word Translation with the possibility to select the incoming language and the desired language
- Basic HTML front coded with Claude.ai
- Support Upload of files up to 10 MB

# Instructions to run the repository

Ensure you have a version of python that is compatible with the project
You also need to have a .env with the following variables "OPENAI_API_KEY", "LANGFUSE_SK", "LANGFUSE_PK", and "LANGFUSE_HOST"

Here are my Langfuse credentials if needed, otherwise head to langfuse.com to create an account:

LANGFUSE_SECRET_KEY=sk-lf-b868a424-a2e5-4a40-ad7b-54695811dbb4
LANGFUSE_PUBLIC_KEY=pk-lf-9bcf4095-35f8-43c4-883d-5da1968e4e0a
LANGFUSE_HOST="https://cloud.langfuse.com"

```bash
poetry install

django manage.py migrate

django manage.py runserver
```

then head to your URL followed by "upload/"

Finally, after having translated the document, you can head to cloud.langfuse.com to observe the tracking of the total costs of the API calls and the number of tokens inputted or generated.