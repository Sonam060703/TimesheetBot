from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.slack_service import SlackService
from app.services.timesheet_service import TimesheetService
from app.utils.block_builder import BlockBuilder
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class InteractionHandler:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.slack_service = SlackService()
        self.block_builder = BlockBuilder()
    
    async def handle_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action_id = payload.get('actions', [{}])[0].get('action_id', '')
        
        logger.info(f"🎯 Handling action: {action_id}")
        logger.debug(f"Payload: {payload}")
        
        if action_id == 'show_entry_forms':
            return await self._handle_show_forms(payload)
        elif action_id == 'submit_timesheet':
            return await self._handle_submit(payload)
        elif action_id == 'entry_count_select':
            # Dropdown selection - just acknowledge, no action needed
            logger.info("📝 Dropdown selection received (no action required)")
            return {}
        
        logger.warning(f"⚠️ Unknown action: {action_id}")
        return {"text": "Unknown action"}
    
    async def _handle_show_forms(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("📝 Processing show_entry_forms action")
            
            # Get selected number of entries
            state_values = payload.get('state', {}).get('values', {})
            logger.debug(f"State values: {state_values}")
            
            entry_count_block = state_values.get('entry_count_block', {})
            selected = entry_count_block.get('entry_count_select', {}).get('selected_option', {})
            num_entries = int(selected.get('value', 1))
            
            logger.info(f"✅ Building form for {num_entries} entries")
            
            # Build entry forms
            blocks = self.block_builder.build_entry_forms(num_entries)
            
            logger.info(f"📤 Returning {len(blocks)} blocks")
            
            # For ephemeral messages (which /timesheet creates), we need to replace via the response
            # Return the blocks directly - FastAPI JSONResponse will handle it
            return {
                "blocks": blocks,
                "replace_original": "true",  # String, not boolean for JSON
                "response_type": "ephemeral"
            }
            
        except Exception as e:
            logger.error(f"❌ Error showing forms: {str(e)}", exc_info=True)
            return {
                "text": f"❌ Error: {str(e)}\n\nPlease try again.",
                "response_type": "ephemeral"
            }
    

    # async def _handle_submit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    # try:
    #     user_id = payload['user']['id']
    #     user_name = payload['user'].get('username', payload['user'].get('name', 'Unknown'))
    #     channel_id = payload.get('channel', {}).get('id', 'unknown')
    #     state_values = payload.get('state', {}).get('values', {})
    #     message_ts = payload.get('message', {}).get('ts')  # Added safely

    #     # Parse entries
    #     entries = []
    #     i = 0
    #     while f'client_block_{i}' in state_values:
    #         client_name = state_values[f'client_block_{i}'][f'client_input_{i}']['value']
    #         hours_value = state_values[f'hours_block_{i}'][f'hours_input_{i}'].get('value', '0')
    #         hours = float(hours_value)

    #         # Get proof file if uploaded
    #         proof_url = None
    #         proof_data = state_values.get(f'proof_block_{i}', {}).get(f'proof_input_{i}', {})
    #         files = proof_data.get('files', [])
    #         if files:
    #             file_id = files[0]['id']
    #             file_info = self.slack_service.get_file_info(file_id)
    #             if file_info:
    #                 proof_url = file_info.get('url_private')

    #         # Save to database
    #         TimesheetService.create_entry(
    #             db=self.db,
    #             user_id=user_id,
    #             username=user_name,
    #             channel_id=channel_id,
    #             client_name=client_name,
    #             hours=hours,
    #             proof_url=proof_url
    #         )

    #         entries.append({'client': client_name, 'hours': hours})
    #         i += 1

    #     # Send confirmation message
    #     confirmation_text = "✅ Timesheet submitted successfully!\n\n"
    #     for idx, entry in enumerate(entries, 1):
    #         confirmation_text += f"{idx}. {entry['client']} - {entry['hours']} hours\n"

    #     self.slack_service.send_dm(
    #         user_id,
    #         [{
    #             "type": "section",
    #             "text": {"type": "mrkdwn", "text": confirmation_text}
    #         }],
    #         "Timesheet submitted"
    #     )

    #     # Confirmation blocks for update
    #     confirmation_blocks = [
    #         {
    #             "type": "section",
    #             "text": {
    #                 "type": "mrkdwn",
    #                 "text": "✅ *Timesheet Submitted Successfully!*"
    #             }
    #         },
    #         # Optionally show submitted entries
    #     ]

    #     # Update message with confirmation
    #     if channel_id and message_ts:
    #         self.slack_service.update_message(
    #             channel_id,
    #             message_ts,
    #             confirmation_blocks,
    #             "Timesheet submitted"
    #         )

    #     return {"response_action": "update", "blocks": confirmation_blocks}

    # except Exception as e:
    #     logger.error(f"Error submitting timesheet: {str(e)}")
    #     return {
    #         "response_action": "errors",
    #         "errors": {"hours_block_0": f"Submission failed: {str(e)}"}
    #     }

    # async def _handle_submit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    # try:
    #     user_id = payload['user']['id']
    #     user_name = payload['user'].get('username', payload['user'].get('name', 'Unknown'))
    #     channel_id = payload.get('channel', {}).get('id', 'unknown')
    #     state_values = payload.get('state', {}).get('values', {})
    #     message_ts = payload.get('message', {}).get('ts')  # Added safely

    #     # Parse entries
    #     entries = []
    #     i = 0
    #     while f'client_block_{i}' in state_values:
    #         client_name = state_values[f'client_block_{i}'][f'client_input_{i}']['value']
    #         hours_value = state_values[f'hours_block_{i}'][f'hours_input_{i}'].get('value', '0')
    #         hours = float(hours_value)

    #         # Get proof file if uploaded
    #         proof_url = None
    #         proof_data = state_values.get(f'proof_block_{i}', {}).get(f'proof_input_{i}', {})
    #         files = proof_data.get('files', [])
    #         if files:
    #             file_id = files[0]['id']
    #             file_info = self.slack_service.get_file_info(file_id)
    #             if file_info:
    #                 proof_url = file_info.get('url_private')

    #         # Save to database
    #         TimesheetService.create_entry(
    #             db=self.db,
    #             user_id=user_id,
    #             username=user_name,
    #             channel_id=channel_id,
    #             client_name=client_name,
    #             hours=hours,
    #             proof_url=proof_url
    #         )

    #         entries.append({'client': client_name, 'hours': hours})
    #         i += 1

    #     # Send confirmation message
    #     confirmation_text = "✅ Timesheet submitted successfully!\n\n"
    #     for idx, entry in enumerate(entries, 1):
    #         confirmation_text += f"{idx}. {entry['client']} - {entry['hours']} hours\n"

    #     self.slack_service.send_dm(
    #         user_id,
    #         [{
    #             "type": "section",
    #             "text": {"type": "mrkdwn", "text": confirmation_text}
    #         }],
    #         "Timesheet submitted"
    #     )

    #     # Confirmation blocks for update
    #     confirmation_blocks = [
    #         {
    #             "type": "section",
    #             "text": {
    #                 "type": "mrkdwn",
    #                 "text": "✅ *Timesheet Submitted Successfully!*"
    #             }
    #         }
    #     ]

    #     # Update message with confirmation
    #     if channel_id and message_ts:
    #         self.slack_service.update_message(
    #             channel_id,
    #             message_ts,
    #             confirmation_blocks,
    #             "Timesheet submitted"
    #         )

    #     return {"response_action": "update", "blocks": confirmation_blocks}

    # except Exception as e:
    #     logger.error(f"Error submitting timesheet: {str(e)}")
    #     return {
    #         "response_action": "errors",
    #         "errors": {"hours_block_0": f"Submission failed: {str(e)}"}
    #     }

    
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
