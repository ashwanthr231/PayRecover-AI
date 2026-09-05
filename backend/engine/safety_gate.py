def safety_check(payment, diagnosis, policy):

    # Policy must allow the action
    if policy["decision"] != "ALLOW_RETRY":
        return {
            "status": "BLOCKED",
            "reason": "Policy engine did not approve the recovery action."
        }

    # AI confidence threshold
    if diagnosis["confidence"] < 0.80:
        return {
            "status": "BLOCKED",
            "reason": "AI confidence is below the safety threshold."
        }

    # Recovery probability threshold
    if diagnosis["recovery_probability"] < 0.50:
        return {
            "status": "BLOCKED",
            "reason": "Recovery probability is too low."
        }

    # Final amount protection
    if payment.amount > 10000:
        return {
            "status": "BLOCKED",
            "reason": "Payment amount exceeds the safety limit."
        }

    return {
        "status": "APPROVED",
        "reason": "Payment passed all safety checks."
    }