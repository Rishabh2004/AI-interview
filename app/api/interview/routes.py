from fastapi import APIRouter,UploadFile, File, Depends
from app.db.prisma import get_prisma
from app.api.interview.interview import InterviewService
from app.utils.jwt_utils import verify_access_token
from app.api.interview.utils import get_loader, process_resume
from app.db.memory import retrieve_memories
prisma = get_prisma()
interview_service = InterviewService()

interview = APIRouter(
    prefix="/interview",
    tags=["interview"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        422: {"description": "Validation error"},
    },
)

@interview.post("/start")
async def start_interview(
    payload:dict = Depends(verify_access_token)
):
    try:
        user_id = payload.get("sub")
        print("User ID from token:", user_id)
        result = await interview_service.conduct_interview(user_id=user_id)
        print("Result==================================>",result)
        return result
    except Exception as e:
        return {"error": str(e)}, 500
    
@interview.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    payload:dict = Depends(verify_access_token)
):
    try:
        user_id = payload.get("sub")
        print("User ID from token:", user_id)
        content = await file.read()
        result = await process_resume(
            file_content=content,
            filename=file.filename,
            user_id=user_id
        )

        
        print("Processing result:=================>", result)
        return result
    except Exception as e:
        return {"error": str(e)}, 500
    
@interview.get("/retrieve-memories")
async def retrieve_memoriess(
    payload:dict = Depends(verify_access_token)
):
    try:
        user_id = payload.get("sub")
        print("User ID from token:", user_id)
        # Retrieve resume context from Mem0
        resume_query = "what is my name?"
        resume_data = await retrieve_memories(user_id, resume_query, limit=100)
        return resume_data
    except Exception as e:
        return {"error": str(e)}, 500

