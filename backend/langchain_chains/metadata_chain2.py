from utils.log_utils import get_logger
from time import perf_counter

from prompts.upload_resume_prompts.metadata_extraction_prompt import RESUME_METADATA_PROMPT1 , RESUME_METADATA_PROMPT2
from schema.resume_metadata import ResumeMetadataPart1 , ResumeMetadataPart2 , ResumeMetadata

from services.llm_initialization import metadata_extraction_llm_model

from utils.llm_usage_log_utils import log_llm_usage

from datetime import date

from time import perf_counter

extraction_chain1 = (
    RESUME_METADATA_PROMPT1
    | metadata_extraction_llm_model.with_structured_output(
        ResumeMetadataPart1,
        method="json_schema",
        # strict=True,
        strict=False,
        include_raw = True
        )
)
 
extraction_chain2 = (
    RESUME_METADATA_PROMPT2
    | metadata_extraction_llm_model.with_structured_output(
        ResumeMetadataPart2,
        method="json_schema",
        # strict=True,
        strict=False,
        include_raw = True
        )
)




def _compute_total_experience_years(experience: list) -> float | None:
    """Overlap-aware total experience, computed from Part 1's dates rather than trusting the LLM."""
 
    def parse(d: str, end_of_period: bool = False):
        if not d:
            return None
        try:
            if len(d) == 7:
                y, m = map(int, d.split("-"))
            elif len(d) == 4:
                y, m = int(d), (12 if end_of_period else 1)
            else:
                return None
            return date(y, m, 1)
        except (ValueError, TypeError):
            return None
 
    today = date.today()
    intervals = []
    for exp in experience:
        start = parse(exp.start_date)
        if not start:
            continue
        end = today if exp.currently_working else (parse(exp.end_date, end_of_period=True) or start)
        if end >= start:
            intervals.append((start, end))
 
    if not intervals:
        return None
 
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
 
    return round(sum((e - s).days for s, e in merged) / 365.25, 1)
 
 
# def process_resume(resume_text: str , session_id:str) -> ResumeMetadata:
#     """
#     Runs Call 1, then Call 2, one after another (not concurrently), so each
#     call's token usage is counted in its own TPM window rather than stacking
#     together in the same one.
#     """

#     start = perf_counter()

#     try:

#         part1: ResumeMetadataPart1 = extraction_chain1.invoke({"resume_text": resume_text})

#         log_llm_usage(
#             operation="resume_metadata_extraction_part1",
#             response=part1["raw"],
#             latency_ms=(perf_counter() - start) * 1000,
#             session_id=session_id
#         )

#         # ADD THIS CHECK:
#         if not part1.get("parsed"):
#             error_msg = f"Part 1 validation failed. Raw output: {part1.get('raw')}"
#             logger.error(error_msg)
#             raise ValueError(error_msg)

#         logger.info(
#                 "Metadata part1 response | %s",
#                 part1
#         )

#     except Exception as e:

#         log_llm_usage(
#             operation="resume_metadata_extraction_part1",
#             response=None,
#             latency_ms=(perf_counter() - start) * 1000,
#             session_id=session_id,
#             success=False,
#             error=str(e)  
#         )

#         raise

#     # ---------------------------------------------------------------------------------

#     start = perf_counter()

#     try:

#         part2: ResumeMetadataPart2 =   extraction_chain2.invoke({"resume_text": resume_text})

#         log_llm_usage(
#             operation="resume_metadata_extraction_part2",
#             response=part2["raw"],
#             latency_ms=(perf_counter() - start) * 1000,
#             session_id=session_id
#         )

#         # ADD THIS CHECK:
#         if not part2.get("parsed"):
#             error_msg = f"Part 2 validation failed. Raw output: {part2.get('raw')}"
#             logger.error(error_msg)
#             raise ValueError(error_msg)

#         logger.info(
#                 "Metadata part2 response | %s",
#                 part2
#         )

#     except Exception as e:

#         log_llm_usage(
#             operation="resume_metadata_extraction_part2",
#             response=None,
#             latency_ms=(perf_counter() - start) * 1000,
#             session_id=session_id,
#             success=False,
#             error=str(e)  
#         )

#         raise


    

#     merged = ResumeMetadata.from_parts(part1["parsed"], part2["parsed"])
#     merged.basic_info.total_experience_years = _compute_total_experience_years(merged.experience)
#     return merged





def process_resume(resume_text: str , session_id:str , filename: str) -> ResumeMetadata:

    logger = get_logger().bind(filename=filename)
    start = perf_counter()

    # ---------------------------------------------------------------------------------
    # PART 1
    # ---------------------------------------------------------------------------------
    try:
        part1 = extraction_chain1.invoke({"resume_text": resume_text})
        part1_parsed = part1.get("parsed")

        # Fallback block: If Langchain failed to parse because of a hallucinated tool name,
        # but the LLM still provided valid arguments, we parse it manually.
        if not part1_parsed and part1.get("raw") and hasattr(part1["raw"], "tool_calls"):
            tool_calls = part1["raw"].tool_calls
            if tool_calls and "ResumeMetadataPart1" in tool_calls[0]["name"]:
                logger.info("Langchain parsing failed. Attempting manual fallback extraction for Part 1.")
                try:
                    part1_parsed = ResumeMetadataPart1(**tool_calls[0]["args"])
                except Exception as e:
                    logger.error(f"Fallback parsing for Part 1 failed: {str(e)}")

        # If it's STILL None after the fallback, we must abort cleanly.
        if not part1_parsed:
            error_msg = f"Part 1 validation failed. Parser error: {part1.get('parsing_error')}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        log_llm_usage(
            operation="resume_metadata_extraction_part1",
            response=part1["raw"],
            latency_ms=(perf_counter() - start) * 1000,
            session_id=session_id
        )

    except Exception as e:
        log_llm_usage(
            operation="resume_metadata_extraction_part1",
            response=None,
            latency_ms=(perf_counter() - start) * 1000,
            session_id=session_id,
            success=False,
            error=str(e)  
        )
        raise

    # ---------------------------------------------------------------------------------
    # PART 2
    # ---------------------------------------------------------------------------------
    start = perf_counter()

    try:
        part2 = extraction_chain2.invoke({"resume_text": resume_text})
        part2_parsed = part2.get("parsed")

        # Fallback block for Part 2
        if not part2_parsed and part2.get("raw") and hasattr(part2["raw"], "tool_calls"):
            tool_calls = part2["raw"].tool_calls
            if tool_calls and "ResumeMetadataPart2" in tool_calls[0]["name"]:
                logger.info("Langchain parsing failed. Attempting manual fallback extraction for Part 2.")
                try:
                    part2_parsed = ResumeMetadataPart2(**tool_calls[0]["args"])
                except Exception as e:
                    logger.error(f"Fallback parsing for Part 2 failed: {str(e)}")

        if not part2_parsed:
            error_msg = f"Part 2 validation failed. Parser error: {part2.get('parsing_error')}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        log_llm_usage(
            operation="resume_metadata_extraction_part2",
            response=part2["raw"],
            latency_ms=(perf_counter() - start) * 1000,
            session_id=session_id
        )

    except Exception as e:
        log_llm_usage(
            operation="resume_metadata_extraction_part2",
            response=None,
            latency_ms=(perf_counter() - start) * 1000,
            session_id=session_id,
            success=False,
            error=str(e)  
        )
        raise

    # ---------------------------------------------------------------------------------
    # MERGE
    # ---------------------------------------------------------------------------------
    # Now we pass the guaranteed valid objects (part1_parsed and part2_parsed)
    merged = ResumeMetadata.from_parts(part1_parsed, part2_parsed)
    merged.basic_info.total_experience_years = _compute_total_experience_years(merged.experience)
    return merged