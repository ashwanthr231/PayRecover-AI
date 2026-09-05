def evaluate_policy(payment, diagnosis):

    # Rule 1: Never automatically retry suspected fraud
    if diagnosis["failure_class"] == "RISK":
        return {
            "decision": "BLOCK",
            "reason": "Risk-related payment failures cannot be automatically retried."
        }

    # Rule 2: Maximum 2 attempts
    if payment.attempt_number >= 2:
        return {
            "decision": "BLOCK",
            "reason": "Maximum automatic retry attempts reached."
        }

    # Rule 3: Limit automatic recovery amount
    if payment.amount > 10000:
        return {
            "decision": "ESCALATE",
            "reason": "Payment amount exceeds the automatic recovery limit."
        }

    # Rule 4: Only retry transient failures
    if (
        diagnosis["recommended_action"] == "RETRY"
        and diagnosis["failure_class"] == "TRANSIENT"
    ):
        return {
            "decision": "ALLOW_RETRY",
            "reason": "Payment satisfies automatic retry policy."
        }

    # Default
    return {
        "decision": "ESCALATE",
        "reason": "Payment does not satisfy automatic recovery rules."
    }