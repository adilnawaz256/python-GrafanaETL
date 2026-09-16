from app.loaders.base_loader import BaseLoader

class TicketLoader(BaseLoader):
    table_name = "core_trouble_tickets"
    conflict_columns = ["issue_key"]
    update_columns = [
        "title",
        "status",
        "substatus",
        "assignee",
        "priority",
        "labels",
        "creation_time",
        "external_name_url",
        "parent_issue_link",
        "creator_name",
        "components",
        "environment",
        "assignee_group_name",
        "reported_incident_type",
        "resolution_description",
        "source_batch_id"
    ]
