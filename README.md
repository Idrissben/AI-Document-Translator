# Office_translator
An AI-based translator that can translate a given Word, Excel, or Powerpoint document in any given language. 
It accepts .docx, .xlsx, or .pptx files of up to 10 mb, and contains the fellow features:

- You can upload a glossary in the form of a .json file in order to translate some specific terms to a given word.
- You can upload a target translated document in order to evaluate the quality of the translation using the METEOR_SCORE metric.
- You can track the cost and number of token of each generation through Langfuse (currently limited to OpenAI models due to LangChain limitations).

By default, this llm-translator only accepts OpenAI models, but it can easily be modified to use any LLM supported by langchain through the modification of the "initialize_model" function with the desired model.

It is a django application with a single endpoint "upload/" which is currently being received through an html interface.

Incoming improvements are:
- The maintaining of the appearance of the incoming word document through the translated one.
- Optimization of the processing of large word documents.

# Changelog

This documents the list of functionalities already implemented as well as the planned improvements.

## [Unreleased]

### Added
- Tests to ensure the app is working
- User history of glossary and previous uploads

### Improved
- More front improvements
- Optimization on treatment of large files to reduce the cost of consumption


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

```bash
poetry install

django manage.py migrate

django manage.py runserver
```

then head to your URL followed by "upload/