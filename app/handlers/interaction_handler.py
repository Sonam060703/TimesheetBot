from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.slack_service import SlackService
from app.services.timesheet_service import TimesheetService
from app.utils.block_builder import BlockBuilder
from typing import Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class InteractionHandler:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.slack_service = SlackService()
        self.block_builder = BlockBuilder()
    
    async def handle_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        interaction_type = payload.get('type')
        
        if interaction_type == 'view_submission':
            return await self._handle_modal_submission(payload)
        elif interaction_type == 'block_actions':
            action_id = payload.get('actions', [{}])[0].get('action_id', '')
            logger.info(f"�� Handling action: {action_id}")
            
            if action_id == 'submit_timesheet':
                return await self._handle_submit(payload)
            elif action_id == 'entry_count_select':
                logger.info("�� Dropdown selection received (no action required)")
                return {}
            
            logger.warning(f"⚠️ Unknown action: {action_id}")
            return {"text": "Unknown action"}
        
        logger.warning(f"⚠️ Unknown interaction type: {interaction_type}")
        return {"text": "Unknown interaction"}
    
    async def _handle_submit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_id = payload['user']['id']
            user_name = payload['user'].get('username', payload['user'].get('name', 'Unknown'))
            channel_id = payload.get('channel', {}).get('id', 'unknown')
            state_values = payload.get('state', {}).get('values', {})
            message_ts = payload.get('message', {}).get('ts')  # Added safely

            entries = []
            i = 0
            while f'client_block_{i}' in state_values:
                client_name = state_values[f'client_block_{i}'][f'client_input_{i}']['value']
                hours_value = state_values[f'hours_block_{i}'][f'hours_input_{i}'].get('value', '0')
                hours = float(hours_value)

                proof_url = None
                proof_data = state_values.get(f'proof_block_{i}', {}).get(f'proof_input_{i}', {})
                files = proof_data.get('files', [])
                if files:
                    file_id = files[0]['id']
                    file_info = self.slack_service.get_file_info(file_id)
                    if file_info:
                        proof_url = file_info.get('url_private')

                TimesheetService.create_entry(
                    db=self.db,
                    user_id=user_id,
                    username=user_name,
                    channel_id=channel_id,
                    client_name=client_name,
                    hours=hours,
                    proof_url=proof_url
                )

                entries.append({'client': client_name, 'hours': hours})
                i += 1

            confirmation_text = "✅ Timesheet submitted successfully!\n\n"
            for idx, entry in enumerate(entries, 1):
                confirmation_text += f"{idx}. {entry['client']} - {entry['hours']} hours\n"

            self.slack_service.send_dm(
                user_id,
                [{
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": confirmation_text}
                }],
                "Timesheet submitted"
            )

            confirmation_blocks = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "✅ *Timesheet Submitted Successfully!*"}
                }
            ]

            if channel_id and message_ts:
                self.slack_service.update_message(
                    channel_id,
                    message_ts,
                    confirmation_blocks,
                    "Timesheet submitted"
                )

            return {"response_action": "update", "blocks": confirmation_blocks}

        except Exception as e:
            logger.error(f"Error submitting timesheet: {str(e)}")
            return {
                "response_action": "errors",
                "errors": {"hours_block_0": f"Submission failed: {str(e)}"}
            }

    async def _handle_modal_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_id = payload['user']['id']
            user_name = payload['user'].get('username', payload['user'].get('name', 'Unknown'))
            channel_id = payload.get('channel', {}).get('id', 'unknown')
            state_values = payload.get('view', {}).get('state', {}).get('values', {})

            entries = []
            i = 0
            while f'client_block_{i}' in state_values:
                client_name = state_values[f'client_block_{i}'][f'client_input_{i}']['value']
                hours_value = state_values[f'hours_block_{i}'][f'hours_input_{i}'].get('value', '0')
                hours = float(hours_value)

                # Note: File inputs are not supported in modals, so we skip proof_url for now
                proof_url = None

                TimesheetService.create_entry(
                    db=self.db,
                    user_id=user_id,
                    username=user_name,
                    channel_id=channel_id,
                    client_name=client_name,
                    hours=hours,
                    proof_url=proof_url
                )

                entries.append({'client': client_name, 'hours': hours})
                i += 1

            confirmation_text = "✅ Timesheet submitted successfully!\n\n"
            for idx, entry in enumerate(entries, 1):
                confirmation_text += f"{idx}. {entry['client']} - {entry['hours']} hours\n"

            # Send confirmation DM
            self.slack_service.send_dm(
                user_id,
                [{
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": confirmation_text}
                }],
                "Timesheet submitted"
            )

            # Return success response for modal
            return {"response_action": "clear"}

        except Exception as e:
            logger.error(f"Error submitting timesheet: {str(e)}")
            return {
                "response_action": "errors",
                "errors": {"hours_block_0": f"Submission failed: {str(e)}"}
            }
