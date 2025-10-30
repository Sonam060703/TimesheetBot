from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.handlers.interaction_handler import InteractionHandler
from app.handlers.command_handler import CommandHandler
from app.utils.block_builder import BlockBuilder
from app.config import get_settings
import json
import hmac
import hashlib
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/slack", tags=["slack"])
settings = get_settings()


def verify_slack_signature(request: Request, body: bytes) -> bool:
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")
    
    # Prevent replay attacks
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False
    
    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = 'v0=' + hmac.new(
        settings.slack_signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, slack_signature)


@router.post("/events")
async def handle_events(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    
    # Verify signature
    if not verify_slack_signature(request, body):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    payload = await request.json()
    
    # Handle URL verification
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}
    
    # Handle events
    event = payload.get("event", {})
    
    # Log event for debugging
    logger.info(f"Received event: {event.get('type')}")
    
    return JSONResponse(content={"status": "ok"})


@router.post("/interactions")
async def handle_interactions(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    
    # Verify signature
    if not verify_slack_signature(request, body):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse payload
    form_data = await request.form()
    payload = json.loads(form_data.get("payload", "{}"))
    
    interaction_type = payload.get("type")
    
    # Handle different interaction types
    if interaction_type == "block_actions":
        handler = InteractionHandler(db)
        response = await handler.handle_interaction(payload)
        return JSONResponse(content=response)
    
    elif interaction_type == "view_submission":
        # Handle modal submission
        handler = InteractionHandler(db)
        response = await handler.handle_interaction(payload)
        return JSONResponse(content=response)
    
    return JSONResponse(content={"status": "ok"})


# @router.post("/commands/timesheet")
# async def handle_timesheet_command(request: Request, db: Session = Depends(get_db)):
#     body = await request.body()
    
#     # Verify signature
#     if not verify_slack_signature(request, body):
#         raise HTTPException(status_code=403, detail="Invalid signature")
    
#     form_data = await request.form()
#     payload = {
#         "user_id": form_data.get("user_id"),
#         "channel_id": form_data.get("channel_id"),
#         "text": form_data.get("text", "")
#     }
    
#     handler = CommandHandler(db)
#     response = await handler.handle_timesheet_command(payload)
    
#     logger.info(body)
#     logger.info(payload)
#     logger.info(response)
    
#     return JSONResponse(content=response)

@router.post("/commands/timesheet")
async def handle_timesheet_command(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    if not verify_slack_signature(request, body):
        raise HTTPException(status_code=403, detail="Invalid signature")

    form_data = await request.form()
    payload = {
        "user_id": form_data.get("user_id"),
        "channel_id": form_data.get("channel_id"),
        "text": form_data.get("text", ""),
        "trigger_id": form_data.get("trigger_id"),
    }

    handler = CommandHandler(db)
    response = await handler.handle_timesheet_command(payload)

    logger.info(body)
    logger.info(payload)
    logger.info(response)

    return JSONResponse(content=response)

@router.post("/commands/timesheetWeekly")
async def handle_weekly_report(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    
    # Verify signature
    if not verify_slack_signature(request, body):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    form_data = await request.form()
    payload = {
        "user_id": form_data.get("user_id"),
        "channel_id": form_data.get("channel_id")
    }
    
    handler = CommandHandler(db)
    response = await handler.handle_weekly_report(payload)
    
    return JSONResponse(content=response)


@router.post("/commands/timesheetMonthly")
async def handle_monthly_report(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    
    # Verify signature
    if not verify_slack_signature(request, body):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    form_data = await request.form()
    payload = {
        "user_id": form_data.get("user_id"),
        "channel_id": form_data.get("channel_id")
    }
    # Extract action information
    # action_id = payload.get('actions', [{}])[0].get('action_id', '') if payload.get('actions') else ''

    # # Log what's happening
    # logger.info(f"Received interaction - Type: {interaction_type}, Action: {action_id}")
    # logger.debug(f"Full payload: {json.dumps(payload, indent=2)}")

    # # Log response
    # logger.info(f"Returning response: {json.dumps(response, indent=2)}")

    # # Error logging
    # logger.error("Invalid signature for interaction request")
    # logger.warning(f"Unhandled interaction type: {interaction_type}")
    
    handler = CommandHandler(db)
    response = await handler.handle_monthly_report(payload)
    
    return JSONResponse(content=response)