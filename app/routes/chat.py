from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import (
    get_llm, 
    get_memory_manager, 
    get_rag_pipeline, 
    get_persona_engine
)
from personality.prompt_builder import PromptBuilder
from validators.response_validator import ResponseValidator
from explainability.explainability_engine import ExplainabilityEngine
from utils.logger import get_logger

logger = get_logger("routes_chat")

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    session_id: str
    message: str
    use_rag: bool = True
    use_memory: bool = True

@router.post("")
def chat(
    request: ChatRequest,
    llm = Depends(get_llm),
    memory_manager = Depends(get_memory_manager),
    rag_pipeline = Depends(get_rag_pipeline),
    persona_engine = Depends(get_persona_engine)
):
    try:
        query = request.message
        session_id = request.session_id

        # 1. Fetch short term chat history
        chat_history = memory_manager.get_chat_history(session_id, limit=8)

        # 2. Retrieve relevant long-term memories
        memories = []
        if request.use_memory:
            memories = memory_manager.get_relevant_facts(query)

        # 3. Retrieve relevant document chunks (RAG)
        rag_results = []
        rag_context = ""
        if request.use_rag:
            rag_results = rag_pipeline.retrieve(query, limit=3)
            # Concatenate chunk texts
            rag_context = "\n\n".join([r["text"] for r in rag_results])

        # 4. Construct prompt
        prompt = PromptBuilder.build_prompt(
            query=query,
            rag_context=rag_context,
            memories=memories,
            chat_history=chat_history
        )

        # 5. Generate content using Gemini
        system_instruction = persona_engine.get_system_instructions()
        raw_response = llm.generate(prompt=prompt, system_instruction=system_instruction)

        # 6. Response Validation Layer (Hallucination and Persona checks)
        validator = ResponseValidator()
        validation = validator.validate_response(
            query=query,
            response=raw_response,
            rag_context=rag_context,
            memories=memories,
            llm_client=llm
        )

        final_response = validation["validated_response"]
        confidence = validation["confidence"]
        validation_reason = validation["reason"]

        # 7. Save conversation to history (SQLite)
        # Store user message
        memory_manager.add_message(session_id=session_id, role="user", content=query)
        # Store AI twin response
        memory_manager.add_message(session_id=session_id, role="assistant", content=final_response)

        is_valid = validation["is_valid"]

        # 8. Generate explainability payload
        explainability = ExplainabilityEngine.create_explanation(
            query=query,
            is_valid=is_valid,
            rag_results=rag_results,
            memories=memories
        )

        return {
            "response": final_response,
            "session_id": session_id,
            "explainability": explainability
        }

    except Exception as e:
        logger.error(f"Chat execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")
