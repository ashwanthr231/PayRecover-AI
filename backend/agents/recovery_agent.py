
def choose_recovery_strategy(payment, diagnosis, policy, safety):

    failure_class = diagnosis["failure_class"]
    recovery_probability = diagnosis["recovery_probability"]
    attempt_number = payment.attempt_number

    # =========================================================
    # 1. SAFETY GATE — HIGHEST PRIORITY
    # =========================================================

    if safety["status"] != "APPROVED":
        return {
            "strategy": "BLOCK",
            "priority": "CRITICAL",
            "reason": safety["reason"],
            "next_action": "Do not attempt automatic recovery."
        }


    # =========================================================
    # 2. HIGH-VALUE PAYMENT
    # =========================================================

    if payment.amount >= 10000:
        return {
            "strategy": "MANUAL_REVIEW",
            "priority": "HIGH",
            "reason": "High-value payment requires additional verification.",
            "next_action": "Send the payment for merchant review."
        }


    # =========================================================
    # 3. POLICY ENGINE DECISION
    # =========================================================

    if policy["decision"] == "BLOCK":
        return {
            "strategy": "BLOCK",
            "priority": "HIGH",
            "reason": policy["reason"],
            "next_action": "Wait for customer or merchant intervention."
        }


    # =========================================================
    # 4. RISK FAILURE
    # =========================================================

    if failure_class == "RISK":
        return {
            "strategy": "ESCALATE",
            "priority": "CRITICAL",
            "reason": "The ML model identified the payment as potentially risky.",
            "next_action": "Send the payment for manual risk review."
        }


    # =========================================================
    # 5. TRANSIENT FAILURE
    # =========================================================

    if failure_class == "TRANSIENT":

        # First attempt + high recovery probability
        if (
            attempt_number == 1
            and recovery_probability >= 0.70
        ):
            return {
                "strategy": "RETRY",
                "priority": "HIGH",
                "reason": (
                    "Temporary payment failure with high "
                    "predicted recovery probability."
                ),
                "next_action": "Retry the payment automatically."
            }


        # First attempt + medium recovery probability
        if (
            attempt_number == 1
            and 0.50 <= recovery_probability < 0.70
        ):
            return {
                "strategy": "RETRY_LATER",
                "priority": "MEDIUM",
                "reason": (
                    "Temporary failure has moderate recovery "
                    "probability, so an immediate retry is avoided."
                ),
                "next_action": "Wait before attempting another recovery."
            }


        # Multiple attempts
        if attempt_number >= 2:
            return {
                "strategy": "RETRY_LATER",
                "priority": "MEDIUM",
                "reason": (
                    "The payment has already been attempted multiple "
                    "times and should not be retried immediately."
                ),
                "next_action": "Wait before attempting another recovery."
            }


    # =========================================================
    # 6. CUSTOMER ACTION REQUIRED
    # =========================================================

    if failure_class == "CUSTOMER_ACTION":
        return {
            "strategy": "CUSTOMER_ACTION",
            "priority": "MEDIUM",
            "reason": (
                "The payment requires customer intervention "
                "before it can be recovered."
            ),
            "next_action": (
                "Notify the customer to resolve the payment issue."
            )
        }


    # =========================================================
    # 7. PERMANENT FAILURE
    # =========================================================

    if failure_class == "PERMANENT":
        return {
            "strategy": "CHANGE_METHOD",
            "priority": "MEDIUM",
            "reason": (
                "The payment is unlikely to succeed using "
                "the current payment method."
            ),
            "next_action": (
                "Ask the customer to use another payment method."
            )
        }


    # =========================================================
    # 8. FALLBACK
    # =========================================================

    return {
        "strategy": "ESCALATE",
        "priority": "LOW",
        "reason": (
            "The system could not identify a safe automatic "
            "recovery strategy."
        ),
        "next_action": "Send the payment for manual review."
    }
