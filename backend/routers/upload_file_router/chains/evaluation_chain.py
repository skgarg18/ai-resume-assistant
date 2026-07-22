
from routers.upload_file_router.models.resume_analysis import ResumeEvaluation
from services.llm_initialization import evaluation_llm_model
from prompts.upload_resume_prompts.upload_resume_prompt import EVALUATION_PROMPT


# evaluation_chain = (
#     EVALUATION_PROMPT
#     | evaluation_llm_model.with_structured_output(
#         ResumeEvaluation,
#         method="function_calling",
#         include_raw = True
#     )
# )

evaluation_chain = (
    EVALUATION_PROMPT
    | evaluation_llm_model.with_structured_output(
        ResumeEvaluation,
        method="json_schema",
        strict=True,
        include_raw = True
    )
)



