# from prompts.upload_resume_prompts.metadata_extraction_prompt import RESUME_METADATA_PROMPT
# from routers.upload_file_router.models.resume_metadata import ResumeMetadata

# from services.llm_initialization import metadata_extraction_llm_model


# metadata_chain = (
#     RESUME_METADATA_PROMPT | 
#     metadata_extraction_llm_model.with_structured_output(
#         ResumeMetadata,
#         method="json_schema",
#         strict=True
#     )
#     )