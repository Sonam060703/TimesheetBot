from typing import List, Dict, Any


class BlockBuilder:
    @staticmethod
    def build_initial_form() -> List[Dict[str, Any]]:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📝 Timesheet Submission*\nPlease fill in your timesheet details."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "input",
                "block_id": "entry_count_block",
                "element": {
                    "type": "static_select",
                    "action_id": "entry_count_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select number of entries"
                    },
                    "options": [
                        {"text": {"type": "plain_text", "text": f"{i}"}, "value": str(i)}
                        for i in range(1, 4)  # Reduced from 5 to 3
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Number of entries"
                }
            }
        ]
        
        # Add only 3 entry forms to stay within Slack limits
        for i in range(3):
            blocks.extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Entry #{i + 1}*"
                    }
                },
                {
                    "type": "input",
                    "block_id": f"client_block_{i}",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": f"client_input_{i}",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter client name"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Client Name"
                    }
                },
                {
                    "type": "input",
                    "block_id": f"hours_block_{i}",
                    "element": {
                        "type": "number_input",
                        "action_id": f"hours_input_{i}",
                        "is_decimal_allowed": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter hours"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Hours"
                    }
                },
                {
                    "type": "input",
                    "block_id": f"description_block_{i}",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": f"description_input_{i}",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter work description"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Description"
                    },
                    "optional": True
                },
                {
                    "type": "divider"
                }
            ])
        
        return blocks
    
    @staticmethod
    def build_entry_forms(num_entries: int) -> List[Dict[str, Any]]:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📋 Fill in your timesheet entries*"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for i in range(num_entries):
            blocks.extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Entry #{i + 1}*"
                    }
                },
                {
                    "type": "input",
                    "block_id": f"client_block_{i}",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": f"client_input_{i}",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter client name"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Client Name"
                    }
                },
                {
                    "type": "input",
                    "block_id": f"hours_block_{i}",
                    "element": {
                        "type": "number_input",
                        "action_id": f"hours_input_{i}",
                        "is_decimal_allowed": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter hours"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Hours"
                    }
                },
                {
                    "type": "input",
                    "block_id": f"proof_block_{i}",
                    "element": {
                        "type": "file_input",
                        "action_id": f"proof_input_{i}",
                        "filetypes": ["jpg", "jpeg", "png", "pdf"],
                        "max_files": 1
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Proof (Image/PDF)"
                    },
                    "optional": True
                },
                {
                    "type": "divider"
                }
            ])
        
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Submit Timesheet"
                    },
                    "action_id": "submit_timesheet",
                    "style": "primary"
                }
            ]
        })
        
        return blocks
    
    @staticmethod
    def build_report_blocks(entries: List[Dict[str, Any]], title: str) -> List[Dict[str, Any]]:
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            },
            {
                "type": "divider"
            }
        ]
        
        if not entries:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_No timesheet entries found for this period._"
                }
            })
            return blocks
        
        for entry in entries:
            proof_text = f"<{entry['proof_url']}|View Proof>" if entry.get('proof_url') else "_No proof attached_"
            blocks.extend([
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*User:*\n{entry['username']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Client:*\n{entry['client_name']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Hours:*\n{entry['hours']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Date:*\n{entry['submission_date']}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Proof:* {proof_text}"
                    }
                },
                {
                    "type": "divider"
                }
            ])
        
        total_hours = sum(entry['hours'] for entry in entries)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Total Hours:* {total_hours}"
            }
        })
        
        return blocks