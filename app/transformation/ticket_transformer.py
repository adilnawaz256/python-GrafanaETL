from typing import Dict, Any, Optional
from app.transformation.base_transformer import BaseTransformer

class TicketTransformer(BaseTransformer):
    @classmethod
    def transform_row(cls, row: Dict[str, Any], batch_id: int) -> Optional[Dict[str, Any]]:
        issue_key = cls.to_str(row.get("Issue key"))

        if not issue_key:
            return None

        return {
            "issue_key": issue_key,
            "title": cls.to_str(row.get("Title")),
            "status": cls.to_str(row.get("Status")),
            "substatus": cls.to_str(row.get("Substatus")),
            "assignee": cls.to_str(row.get("Assignee")),
            "priority": cls.to_str(row.get("Priority")),
            "labels": cls.to_str(row.get("Labels")),
            "creation_time": cls.to_datetime(row.get("Creation Time")),
            "external_name_url": cls.to_str(row.get("External Name/URL")),
            "parent_issue_link": cls.to_str(row.get("Parent Issue Link")),
            "creator_name": cls.to_str(row.get("Creator Name")),
            "components": cls.to_str(row.get("Components")),
            "environment": cls.to_str(row.get("DM_TroubleTicket.dictionaries.dictionary_ENVIRONMENT") or row.get("Environment")),
            "assignee_group_name": cls.to_str(row.get("Assignee Group Name")),
            "reported_incident_type": cls.to_str(row.get("Reported Incident Type")),
            "resolution_description": cls.to_str(row.get("Resolution Description")),
            "source_batch_id": batch_id
        }
