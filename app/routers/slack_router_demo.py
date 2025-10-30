# from fastapi import APIRouter, Request, Depends
# from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.handlers.interaction_handler import InteractionHandler
# from app.handlers.command_handler import CommandHandler
# from app.utils.block_builder import BlockBuilder
# import json
# import logging

# logger = logging.getLogger(__name__)
# router = APIRouter(prefix="/demo", tags=["demo"])


# @router.post("/timesheet")
# async def demo_timesheet_command(request: Request, db: Session = Depends(get_db)):
#     """Demo endpoint - No signature verification"""
#     logger.info("📝 Demo: Timesheet command received")
    
#     handler = CommandHandler(db)
#     payload = {
#         "user_id": "U123456",
#         "channel_id": "C123456",
#         "text": ""
#     }
    
#     response = await handler.handle_timesheet_command(payload)
#     return JSONResponse(content=response)


# @router.post("/interactions")
# async def demo_interactions(request: Request, db: Session = Depends(get_db)):
#     """Demo endpoint - No signature verification"""
#     try:
#         payload = await request.json()
        
#         logger.info(f"📝 Demo: Interaction received")
#         logger.info(f"Action: {payload.get('actions', [{}])[0].get('action_id', 'unknown')}")
        
#         interaction_type = payload.get("type")
        
#         if interaction_type == "block_actions":
#             handler = InteractionHandler(db)
#             response = await handler.handle_interaction(payload)
#             logger.info(f"Response: {response}")
#             return JSONResponse(content=response)
        
#         return JSONResponse(content={"status": "ok"})
    
#     except Exception as e:
#         logger.error(f"Error: {str(e)}", exc_info=True)
#         return JSONResponse(content={"error": str(e)}, status_code=500)


# @router.post("/weekly-report")
# async def demo_weekly_report(request: Request, db: Session = Depends(get_db)):
#     """Demo endpoint for weekly report"""
#     handler = CommandHandler(db)
#     payload = {
#         "user_id": "MANAGER123",
#         "channel_id": "C123456"
#     }
    
#     response = await handler.handle_weekly_report(payload)
#     return JSONResponse(content=response)


# @router.post("/monthly-report")
# async def demo_monthly_report(request: Request, db: Session = Depends(get_db)):
#     """Demo endpoint for monthly report"""
#     handler = CommandHandler(db)
#     payload = {
#         "user_id": "MANAGER123",
#         "channel_id": "C123456"
#     }
    
#     response = await handler.handle_monthly_report(payload)
#     return JSONResponse(content=response)


# @router.get("/health")
# async def demo_health():
#     """Simple health check"""
#     return {
#         "status": "demo mode",
#         "message": "Ready for testing",
#         "database": "connected"
#     }