def simulate_recovery(payment, strategy):
    """Simulate the outcome of the selected recovery strategy.

    This project is a decision/recovery simulator; it does not call a real
    payment gateway. Only an approved RETRY is modeled as a successful
    automatic recovery.
    """

    strategy_name = strategy.get("strategy")

    if strategy_name == "BLOCK":
        return {
            "status": "NOT_EXECUTED",
            "recovered": False,
            "amount_recovered": 0,
            "message": "Recovery was blocked by the safety gate."
        }

    if strategy_name == "RETRY":
        return {
            "status": "SUCCESS",
            "recovered": True,
            "amount_recovered": payment.amount,
            "message": "Payment successfully recovered on simulated retry."
        }

    if strategy_name == "RETRY_LATER":
        return {
            "status": "SCHEDULED",
            "recovered": False,
            "amount_recovered": 0,
            "message": "Recovery is deferred to avoid an immediate repeated attempt."
        }

    if strategy_name == "CUSTOMER_ACTION":
        return {
            "status": "NOT_EXECUTED",
            "recovered": False,
            "amount_recovered": 0,
            "message": "Customer action is required before recovery."
        }

    if strategy_name == "CHANGE_METHOD":
        return {
            "status": "NOT_EXECUTED",
            "recovered": False,
            "amount_recovered": 0,
            "message": "A different payment method is required."
        }

    if strategy_name in {"ESCALATE", "MANUAL_REVIEW"}:
        return {
            "status": "NOT_EXECUTED",
            "recovered": False,
            "amount_recovered": 0,
            "message": "Payment requires manual review."
        }

    return {
        "status": "NOT_EXECUTED",
        "recovered": False,
        "amount_recovered": 0,
        "message": "Recovery was not executed."
    }
