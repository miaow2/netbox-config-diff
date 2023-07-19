from utilities.choices import ChoiceSet


class ConfigComplianceStatusChoices(ChoiceSet):
    COMPLIANT = "compliant"
    PENDING = "pending"
    FAILED = "failed"
    ERRORED = "errored"

    CHOICES = (
        (COMPLIANT, "Compliant", "green"),
        (PENDING, "Pending", "cyan"),
        (FAILED, "Failed", "red"),
        (ERRORED, "Errored", "red"),
    )
