from typing import Literal
from pydantic import BaseModel

class WorkflowResponse(BaseModel):
    workflow: Literal["chat", "email"]
    referenced_candidates: list[str]



from prompts.workflow_classifier_prompt import router_prompt 
from services.llm_initialization import llm_model

workflow_router_chain = (
    router_prompt
    | llm_model.with_structured_output(WorkflowResponse)
)