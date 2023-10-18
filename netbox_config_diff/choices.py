from utilities.choices import ChoiceSet


class ConfigComplianceStatusChoices(ChoiceSet):
    COMPLIANT = "compliant"
    PENDING = "pending"
    FAILED = "failed"
    ERRORED = "errored"
    DIFF = "diff"

    CHOICES = (
        (COMPLIANT, "Compliant", "green"),
        (PENDING, "Pending", "cyan"),
        (FAILED, "Failed", "red"),
        (ERRORED, "Errored", "red"),
        (DIFF, "Diff", "teal"),
    )


class ConfigurationRequestStatusChoices(ChoiceSet):
    CREATED = "created"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    FAILED = "failed"
    ERRORED = "errored"
    COMPLETED = "completed"

    CHOICES = (
        (CREATED, "Created", "cyan"),
        (APPROVED, "Approved", "indigo"),
        (SCHEDULED, "Scheduled", "teal"),
        (RUNNING, "Running", "blue"),
        (FAILED, "Failed", "red"),
        (ERRORED, "Errored", "red"),
        (COMPLETED, "Completed", "green"),
    )

    FINISHED_STATE_CHOICES = (
        FAILED,
        ERRORED,
        COMPLETED,
    )
