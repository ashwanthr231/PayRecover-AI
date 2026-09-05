/* =========================================================
   PAYRECOVER AI
   Frontend Application Logic
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const API_URL = window.PAYRECOVER_API_URL || "http://127.0.0.1:8000";


/* =========================================================
   GLOBAL VARIABLES
========================================================= */

let recoveryChart = null;
let failureChart = null;

/*
   Stores all payment history received from backend.
   Filtering is performed on this array without
   repeatedly calling the backend.
*/
let allPayments = [];


/* =========================================================
   HELPER FUNCTIONS
========================================================= */


/*
   Format currency amount
*/
function formatAmount(amount) {

    const value = Number(amount) || 0;

    return "₹" + value.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}


/*
   Format percentage
*/
function formatPercentage(value) {

    const percentage = Number(value) || 0;

    return `${(percentage * 100).toFixed(0)}%`;
}


/*
   Escape HTML to prevent unwanted HTML injection
*/
function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/*
   Convert text into a readable label

   Example:
   CUSTOMER_ACTION
   ->
   Customer Action
*/
function formatLabel(value) {

    if (!value) {
        return "-";
    }

    return String(value)
        .toLowerCase()
        .split("_")
        .map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        )
        .join(" ");
}


/* =========================================================
   ANALYTICS
========================================================= */

async function loadAnalytics() {

    try {

        const response = await fetch(
            `${API_URL}/analytics`
        );

        if (!response.ok) {
            throw new Error(
                `Analytics request failed: ${response.status}`
            );
        }

        const data = await response.json();


        /*
           Update metric cards
        */

        const totalPayments =
            document.getElementById("totalPayments");

        const failedPayments =
            document.getElementById("failedPayments");

        const recoveredPayments =
            document.getElementById("recoveredPayments");

        const recoveryRate =
            document.getElementById("recoveryRate");

        const failedAmount =
            document.getElementById("failedAmount");

        const recoveredAmount =
            document.getElementById("recoveredAmount");


        if (totalPayments) {
            totalPayments.textContent =
                data.total_payments ?? 0;
        }


        if (failedPayments) {
            failedPayments.textContent =
                data.failed_payments ?? 0;
        }


        if (recoveredPayments) {
            recoveredPayments.textContent =
                data.recovered_payments ?? 0;
        }


        if (recoveryRate) {
            recoveryRate.textContent =
                `${data.recovery_rate ?? 0}%`;
        }


        if (failedAmount) {
            failedAmount.textContent =
                formatAmount(data.total_failed_amount);
        }


        if (recoveredAmount) {
            recoveredAmount.textContent =
                formatAmount(data.total_recovered_amount);
        }


        /*
           Update charts
        */

        updateRecoveryChart(data);

        await loadFailureChart();

    }

    catch (error) {

        console.error(
            "Failed to load analytics:",
            error
        );

    }
}


/* =========================================================
   RECOVERY CHART
========================================================= */

function updateRecoveryChart(data) {

    const canvas =
        document.getElementById("recoveryChart");

    if (!canvas) {
        return;
    }


    const ctx =
        canvas.getContext("2d");


    /*
       Destroy previous chart
       before creating a new one.
    */

    if (recoveryChart) {

        recoveryChart.destroy();

        recoveryChart = null;
    }


    recoveryChart = new Chart(ctx, {

        type: "doughnut",

        data: {

            labels: [
                "Recovered",
                "Not Recovered"
            ],

            datasets: [{

                data: [

                    Number(
                        data.recovered_payments
                    ) || 0,

                    Math.max(
                        (
                            Number(
                                data.total_payments
                            ) || 0
                        ) -
                        (
                            Number(
                                data.recovered_payments
                            ) || 0
                        ),
                        0
                    )

                ]

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom"

                }

            }

        }

    });

}


/* =========================================================
   FAILURE ANALYTICS CHART
========================================================= */

async function loadFailureChart() {

    const canvas =
        document.getElementById("failureChart");

    if (!canvas) {
        return;
    }


    try {

        const response = await fetch(
            `${API_URL}/payments`
        );

        if (!response.ok) {
            throw new Error(
                `Payment history request failed: ${response.status}`
            );
        }


        const payments =
            await response.json();


        /*
           Count payments by failure class
        */

        const failureCounts = {

            TRANSIENT: 0,

            CUSTOMER_ACTION: 0,

            RISK: 0,

            PERMANENT: 0

        };


        payments.forEach(payment => {

            const failureClass =
                payment.failure_class;


            if (
                Object.prototype.hasOwnProperty.call(
                    failureCounts,
                    failureClass
                )
            ) {

                failureCounts[failureClass]++;

            }

        });


        const ctx =
            canvas.getContext("2d");


        if (failureChart) {

            failureChart.destroy();

            failureChart = null;
        }


        failureChart = new Chart(ctx, {

            type: "bar",

            data: {

                labels: [

                    "Transient",

                    "Customer Action",

                    "Risk",

                    "Permanent"

                ],

                datasets: [{

                    label: "Payments",

                    data: [

                        failureCounts.TRANSIENT,

                        failureCounts.CUSTOMER_ACTION,

                        failureCounts.RISK,

                        failureCounts.PERMANENT

                    ],

                    borderWidth: 1

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {

                            precision: 0

                        }

                    }

                },

                plugins: {

                    legend: {

                        display: false

                    }

                }

            }

        });

    }

    catch (error) {

        console.error(
            "Failed to load failure chart:",
            error
        );

    }

}


/* =========================================================
   ANALYZE PAYMENT
========================================================= */

async function analyzePayment(event) {

    event.preventDefault();


    /*
       Get form fields
    */

    const paymentId =
        document.getElementById("payment_id");

    const merchantId =
        document.getElementById("merchant_id");

    const customerId =
        document.getElementById("customer_id");

    const amount =
        document.getElementById("amount");

    const paymentMethod =
        document.getElementById("payment_method");

    const failureCode =
        document.getElementById("failure_code");

    const attemptNumber =
        document.getElementById("attempt_number");


    /*
       Make sure fields exist
    */

    if (
        !paymentId ||
        !merchantId ||
        !customerId ||
        !amount ||
        !paymentMethod ||
        !failureCode ||
        !attemptNumber
    ) {

        console.error(
            "One or more form elements are missing."
        );

        return;

    }


    /*
       Read values
    */

    const paymentIdValue =
        paymentId.value.trim();

    const merchantIdValue =
        merchantId.value.trim();

    const customerIdValue =
        customerId.value.trim();

    const amountValue =
        Number(amount.value);

    const paymentMethodValue =
        paymentMethod.value;

    const failureCodeValue =
        failureCode.value;

    const attemptNumberValue =
        Number(attemptNumber.value);


    /*
       Basic validation
    */

    if (!paymentIdValue) {

        alert("Please enter Payment ID.");

        paymentId.focus();

        return;
    }


    if (!merchantIdValue) {

        alert("Please enter Merchant ID.");

        merchantId.focus();

        return;
    }


    if (!customerIdValue) {

        alert("Please enter Customer ID.");

        customerId.focus();

        return;
    }


    if (
        !Number.isFinite(amountValue) ||
        amountValue <= 0
    ) {

        alert("Please enter a valid payment amount.");

        amount.focus();

        return;
    }


    if (!paymentMethodValue) {

        alert("Please select a payment method.");

        paymentMethod.focus();

        return;
    }


    if (!failureCodeValue) {

        alert("Please select a failure code.");

        failureCode.focus();

        return;
    }


    if (
        !Number.isInteger(attemptNumberValue) ||
        attemptNumberValue <= 0
    ) {

        alert("Attempt number must be a positive integer.");

        attemptNumber.focus();

        return;
    }


    /*
       Request body
    */

    const paymentData = {

        payment_id: paymentIdValue,

        merchant_id: merchantIdValue,

        customer_id: customerIdValue,

        amount: amountValue,

        payment_method: paymentMethodValue,

        failure_code: failureCodeValue,

        attempt_number: attemptNumberValue,

        status: "FAILED"

    };


    /*
       Find analyze button
    */

    const submitButton =
        document.querySelector(
            "#paymentForm button[type='submit']"
        );


    const originalButtonText =
        submitButton
            ? submitButton.innerHTML
            : "";


    try {

        /*
           Loading state
        */

        if (submitButton) {

            submitButton.disabled = true;

            submitButton.innerHTML =
                "⏳ Analyzing Payment...";

        }


        /*
           Send payment to FastAPI
        */

        const response = await fetch(
            `${API_URL}/payments`,
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify(paymentData)

            }
        );


        if (!response.ok) {

            let errorMessage =
                `Server error: ${response.status}`;


            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {

                    errorMessage =
                        errorData.detail;

                }

            }

            catch (_) {

                /*
                   Ignore JSON parsing failure
                */

            }


            throw new Error(errorMessage);

        }


        const data =
            await response.json();


        /*
           Display AI result
        */

        displayAnalysis(data);


        /*
           Refresh dashboard
        */

        await loadAnalytics();

        await loadPayments();


        /*
           Reset form after successful analysis
        */
        /*
        const form =
            document.getElementById("paymentForm");

        if (form) {

            form.reset();

        }
        */

        /*
           Keep attempt number at 1
        */

        if (attemptNumber) {

            attemptNumber.value = 1;

        }

    }

    catch (error) {

        console.error(
            "Payment analysis failed:",
            error
        );


        alert(
            `Payment analysis failed.\n\n${error.message}`
        );

    }

    finally {

        /*
           Restore button
        */

        if (submitButton) {

            submitButton.disabled = false;

            submitButton.innerHTML =
                originalButtonText ||
                "✦ Analyze Payment";

        }

    }

}


/* =========================================================
   DISPLAY ANALYSIS
========================================================= */

function displayAnalysis(data) {

    const container =
        document.getElementById(
            "analysisResult"
        );


    if (!container) {
        return;
    }


    const diagnosis =
        data.diagnosis || {};


    const policy =
        data.policy || {};


    const safety =
        data.safety || {};


    const strategy =
        data.recovery_strategy || {};


    const recovery =
        data.recovery || {};


    /*
       AI values
    */

    const confidence =
        Math.max(
            0,
            Math.min(
                Number(diagnosis.confidence) || 0,
                1
            )
        );


    const recoveryProbability =
        Math.max(
            0,
            Math.min(
                Number(
                    diagnosis.recovery_probability
                ) || 0,
                1
            )
        );


    const confidencePercent =
        Math.round(
            confidence * 100
        );


    const recoveryPercent =
        Math.round(
            recoveryProbability * 100
        );


    /*
       Status values
    */

    const failureClass =
        diagnosis.failure_class ||
        "UNKNOWN";


    const recommendedAction =
        diagnosis.recommended_action ||
        "ESCALATE";


    const policyDecision =
        policy.decision ||
        "UNKNOWN";


    const safetyStatus =
        safety.status ||
        "UNKNOWN";


    const strategyName =
        strategy.strategy ||
        strategy.action ||
        recommendedAction ||
        "UNKNOWN";


    const recoveryStatus =
        recovery.status ||
        "NOT_EXECUTED";


    const amountRecovered =
        Number(
            recovery.amount_recovered
        ) || 0;


    /*
       Determine overall result
    */

    let overallStatus =
        "BLOCKED";


    if (
        safetyStatus === "APPROVED" &&
        recoveryStatus === "SUCCESS"
    ) {

        overallStatus =
            "SUCCESS";

    }

    else if (
        safetyStatus === "APPROVED"
    ) {

        overallStatus =
            "APPROVED";

    }


    /*
       Reasoning
    */

    const reason =
        diagnosis.reason ||
        "The payment requires further evaluation.";


    /*
       Message
    */

    const recoveryMessage =
        recovery.message ||
        recovery.reason ||
        "No recovery message available.";


    /*
       CSS-safe status classes
    */

    const statusClass =
        String(overallStatus)
            .toLowerCase()
            .replace(/[^a-z0-9_-]/g, "");


    const safetyClass =
        String(safetyStatus)
            .toLowerCase()
            .replace(/[^a-z0-9_-]/g, "");


    const recoveryClass =
        String(recoveryStatus)
            .toLowerCase()
            .replace(/[^a-z0-9_-]/g, "");


    /*
       Render result
    */

    container.innerHTML = `

        <div class="analysis-result-wrapper">


            <!-- OVERALL DECISION -->

            <div class="decision-banner ${statusClass}">

                <div class="decision-main">

                    <span class="decision-label">
                        AI Decision
                    </span>

                    <strong>
                        ${escapeHTML(
                            overallStatus
                        )}
                    </strong>

                </div>


                <div class="decision-description">

                    ${escapeHTML(
                        reason
                    )}

                </div>

            </div>


            <!-- AI METRICS -->

            <div class="ai-metrics">


                <!-- CONFIDENCE -->

                <div class="ai-metric-card">

                    <div class="ai-metric-header">

                        <span>
                            ML Confidence
                        </span>

                        <strong>
                            ${confidencePercent}%
                        </strong>

                    </div>


                    <div class="progress-bar">

                        <div
                            class="progress-fill"
                            style="width: ${confidencePercent}%"
                        ></div>

                    </div>

                </div>


                <!-- RECOVERY PROBABILITY -->

                <div class="ai-metric-card">

                    <div class="ai-metric-header">

                        <span>
                            Recovery Probability
                        </span>

                        <strong>
                            ${recoveryPercent}%
                        </strong>

                    </div>


                    <div class="progress-bar">

                        <div
                            class="progress-fill"
                            style="width: ${recoveryPercent}%"
                        ></div>

                    </div>

                </div>

            </div>


            <!-- RESULT GRID -->

            <div class="result-grid">


                <!-- FAILURE CLASS -->

                <div class="result-card">

                    <span>
                        Failure Class
                    </span>

                    <strong>
                        ${escapeHTML(
                            formatLabel(
                                failureClass
                            )
                        )}
                    </strong>

                </div>


                <!-- RECOMMENDED ACTION -->

                <div class="result-card">

                    <span>
                        Recommended Action
                    </span>

                    <strong>
                        ${escapeHTML(
                            formatLabel(
                                recommendedAction
                            )
                        )}
                    </strong>

                </div>


                <!-- POLICY -->

                <div class="result-card">

                    <span>
                        Policy Decision
                    </span>

                    <strong>
                        ${escapeHTML(
                            formatLabel(
                                policyDecision
                            )
                        )}
                    </strong>

                </div>


                <!-- SAFETY -->

                <div class="result-card">

                    <span>
                        Safety Status
                    </span>

                    <strong
                        class="${safetyClass}"
                    >
                        ${escapeHTML(
                            formatLabel(
                                safetyStatus
                            )
                        )}
                    </strong>

                </div>


                <!-- STRATEGY -->

                <div class="result-card">

                    <span>
                        Recovery Strategy
                    </span>

                    <strong>
                        ${escapeHTML(
                            formatLabel(
                                strategyName
                            )
                        )}
                    </strong>

                </div>


                <!-- RECOVERY STATUS -->

                <div class="result-card">

                    <span>
                        Recovery Status
                    </span>

                    <strong
                        class="${recoveryClass}"
                    >
                        ${escapeHTML(
                            formatLabel(
                                recoveryStatus
                            )
                        )}
                    </strong>

                </div>


                <!-- RECOVERED AMOUNT -->

                <div class="result-card highlight">

                    <span>
                        Amount Recovered
                    </span>

                    <strong>
                        ${formatAmount(
                            amountRecovered
                        )}
                    </strong>

                </div>


                <!-- REASON -->

                <div class="result-card wide">

                    <span>
                        AI Reasoning
                    </span>

                    <strong>
                        ${escapeHTML(
                            reason
                        )}
                    </strong>

                </div>


                <!-- RECOVERY MESSAGE -->

                <div class="result-card wide">

                    <span>
                        Recovery Engine
                    </span>

                    <strong>
                        ${escapeHTML(
                            recoveryMessage
                        )}
                    </strong>

                </div>

            </div>

        </div>

    `;

}


/* =========================================================
   PAYMENT HISTORY
========================================================= */

async function loadPayments() {

    const tableBody =
        document.getElementById(
            "paymentTable"
        );


    if (!tableBody) {
        return;
    }


    try {

        /*
           Show loading state
        */

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="9"
                    style="text-align:center;"
                >

                    Loading payments...

                </td>

            </tr>

        `;


        /*
           Get payment history
        */

        const response =
            await fetch(
                `${API_URL}/payments`
            );


        if (!response.ok) {

            throw new Error(
                `Payment history request failed: ${response.status}`
            );

        }


        const payments =
            await response.json();


        /*
           Make sure we received an array
        */

        allPayments =
            Array.isArray(payments)
                ? payments
                : [];


        /*
           Apply current filters
        */

        applyPaymentFilters();

    }

    catch (error) {

        console.error(
            "Failed to load payment history:",
            error
        );


        allPayments = [];


        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="9"
                    style="text-align:center;"
                >

                    Unable to load payment history.

                </td>

            </tr>

        `;


        updateHistoryCount(0);

    }

}


/* =========================================================
   RENDER PAYMENT HISTORY
========================================================= */

function renderPaymentHistory(payments) {

    const tableBody =
        document.getElementById(
            "paymentTable"
        );


    if (!tableBody) {
        return;
    }


    /*
       No results
    */

    if (
        !Array.isArray(payments) ||
        payments.length === 0
    ) {

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="9"
                    style="text-align:center;"
                >

                    No payments found.

                </td>

            </tr>

        `;


        updateHistoryCount(0);

        return;

    }


    /*
       Render rows
    */

    tableBody.innerHTML =
        payments.map(payment => {


            /*
               Payment values
            */

            const paymentId =
                payment.payment_id || "-";


            const amount =
                formatAmount(
                    payment.amount
                );


            const method =
                payment.payment_method || "-";


            const failureCode =
                payment.failure_code || "-";


            const failureClass =
                payment.failure_class || "-";


            const policy =
                payment.policy_decision || "-";


            const safety =
                payment.safety_status || "-";


            const recovered =
                Boolean(
                    payment.recovered
                );


            const recoveryStatus =
                recovered
                    ? "SUCCESS"
                    : "NOT RECOVERED";


            const amountRecovered =
                formatAmount(
                    payment.amount_recovered
                );


            /*
               Status CSS classes
            */

            const recoveryStatusClass =
                recovered
                    ? "success"
                    : "blocked";


            const safetyStatusClass =
                String(safety)
                    .toLowerCase()
                    .replace(
                        /[^a-z0-9_-]/g,
                        ""
                    );


            const policyStatusClass =
                String(policy)
                    .toLowerCase()
                    .replace(
                        /[^a-z0-9_-]/g,
                        ""
                    );


            return `

                <tr>


                    <!-- PAYMENT ID -->

                    <td>

                        <strong>
                            ${escapeHTML(
                                paymentId
                            )}
                        </strong>

                    </td>


                    <!-- AMOUNT -->

                    <td>

                        ${amount}

                    </td>


                    <!-- METHOD -->

                    <td>

                        ${escapeHTML(
                            formatLabel(
                                method
                            )
                        )}

                    </td>


                    <!-- FAILURE -->

                    <td>

                        <div class="table-primary">

                            ${escapeHTML(
                                formatLabel(
                                    failureCode
                                )
                            )}

                        </div>

                        <div class="table-secondary">

                            ${escapeHTML(
                                formatLabel(
                                    failureClass
                                )
                            )}

                        </div>

                    </td>


                    <!-- DIAGNOSIS -->

                    <td>

                        <span class="status-badge">

                            ${escapeHTML(
                                formatLabel(
                                    failureClass
                                )
                            )}

                        </span>

                    </td>


                    <!-- POLICY -->

                    <td>

                        <span
                            class="status-badge ${policyStatusClass}"
                        >

                            ${escapeHTML(
                                formatLabel(
                                    policy
                                )
                            )}

                        </span>

                    </td>


                    <!-- SAFETY -->

                    <td>

                        <span
                            class="status-badge ${safetyStatusClass}"
                        >

                            ${escapeHTML(
                                formatLabel(
                                    safety
                                )
                            )}

                        </span>

                    </td>


                    <!-- RECOVERY -->

                    <td>

                        <span
                            class="status-badge ${recoveryStatusClass}"
                        >

                            ${recoveryStatus}

                        </span>

                    </td>


                    <!-- RECOVERED AMOUNT -->

                    <td>

                        <strong
                            class="${recovered ? "success" : ""}"
                        >

                            ${amountRecovered}

                        </strong>

                    </td>


                </tr>

            `;

        }).join("");


    /*
       Update result count
    */

    updateHistoryCount(
        payments.length
    );

}


/* =========================================================
   APPLY PAYMENT FILTERS
========================================================= */

function applyPaymentFilters() {

    /*
       Get filter elements
    */

    const searchInput =
        document.getElementById(
            "paymentSearch"
        );


    const recoveryFilter =
        document.getElementById(
            "recoveryFilter"
        );


    const failureFilter =
        document.getElementById(
            "failureFilter"
        );


    const methodFilter =
        document.getElementById(
            "methodFilter"
        );


    /*
       Read filter values
    */

    const searchValue =
        searchInput
            ? searchInput.value
                .trim()
                .toLowerCase()
            : "";


    const recoveryValue =
        recoveryFilter
            ? recoveryFilter.value
            : "ALL";


    const failureValue =
        failureFilter
            ? failureFilter.value
            : "ALL";


    const methodValue =
        methodFilter
            ? methodFilter.value
            : "ALL";


    /*
       Filter payments
    */

    const filteredPayments =
        allPayments.filter(payment => {


            /* ---------------------------------------------
               SEARCH FILTER
            ---------------------------------------------- */

            if (searchValue) {

                const paymentId =
                    String(
                        payment.payment_id || ""
                    ).toLowerCase();


                const customerId =
                    String(
                        payment.customer_id || ""
                    ).toLowerCase();


                const merchantId =
                    String(
                        payment.merchant_id || ""
                    ).toLowerCase();


                const matchesSearch =

                    paymentId.includes(
                        searchValue
                    ) ||

                    customerId.includes(
                        searchValue
                    ) ||

                    merchantId.includes(
                        searchValue
                    );


                if (!matchesSearch) {

                    return false;

                }

            }


            /* ---------------------------------------------
               RECOVERY STATUS FILTER
            ---------------------------------------------- */

            if (
                recoveryValue !== "ALL"
            ) {

                const isRecovered =
                    Boolean(
                        payment.recovered
                    );


                if (
                    recoveryValue === "SUCCESS" &&
                    !isRecovered
                ) {

                    return false;

                }


                if (
                    recoveryValue === "NOT RECOVERED" &&
                    isRecovered
                ) {

                    return false;

                }

            }


            /* ---------------------------------------------
               FAILURE CLASS FILTER
            ---------------------------------------------- */

            if (
                failureValue !== "ALL"
            ) {

                const failureClass =
                    String(
                        payment.failure_class || ""
                    ).toUpperCase();


                if (
                    failureClass !==
                    failureValue
                ) {

                    return false;

                }

            }


            /* ---------------------------------------------
               PAYMENT METHOD FILTER
            ---------------------------------------------- */

            if (
                methodValue !== "ALL"
            ) {

                const paymentMethod =
                    String(
                        payment.payment_method || ""
                    ).toUpperCase();


                if (
                    paymentMethod !==
                    methodValue
                ) {

                    return false;

                }

            }


            return true;

        });


    /*
       Render filtered results
    */

    renderPaymentHistory(
        filteredPayments
    );

}


/* =========================================================
   HISTORY COUNT
========================================================= */

function updateHistoryCount(count) {

    const historyCount =
        document.getElementById(
            "historyCount"
        );


    if (historyCount) {

        historyCount.textContent =
            count;

    }

}


/* =========================================================
   INITIALIZE PAYMENT HISTORY FILTERS
========================================================= */

function initializePaymentFilters() {

    const searchInput =
        document.getElementById(
            "paymentSearch"
        );


    const recoveryFilter =
        document.getElementById(
            "recoveryFilter"
        );


    const failureFilter =
        document.getElementById(
            "failureFilter"
        );


    const methodFilter =
        document.getElementById(
            "methodFilter"
        );


    const resetButton =
        document.getElementById(
            "resetFilters"
        );


    /*
       Search
    */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            applyPaymentFilters
        );

    }


    /*
       Recovery filter
    */

    if (recoveryFilter) {

        recoveryFilter.addEventListener(
            "change",
            applyPaymentFilters
        );

    }


    /*
       Failure filter
    */

    if (failureFilter) {

        failureFilter.addEventListener(
            "change",
            applyPaymentFilters
        );

    }


    /*
       Payment method filter
    */

    if (methodFilter) {

        methodFilter.addEventListener(
            "change",
            applyPaymentFilters
        );

    }


    /*
       Reset button
    */

    if (resetButton) {

        resetButton.addEventListener(
            "click",
            () => {


                if (searchInput) {

                    searchInput.value = "";

                }


                if (recoveryFilter) {

                    recoveryFilter.value =
                        "ALL";

                }


                if (failureFilter) {

                    failureFilter.value =
                        "ALL";

                }


                if (methodFilter) {

                    methodFilter.value =
                        "ALL";

                }


                /*
                   Show all payments again
                */

                applyPaymentFilters();

            }
        );

    }

}


/* =========================================================
   REFRESH PAYMENT HISTORY
========================================================= */

function initializeRefreshButton() {

    const refreshButton =
        document.getElementById(
            "refreshPayments"
        );


    /*
       Fallback for older HTML
    */

    const oldRefreshButton =
        document.querySelector(
            ".refresh-button"
        );


    const button =
        refreshButton ||
        oldRefreshButton;


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        async () => {


            const originalText =
                button.innerHTML;


            try {

                button.disabled = true;

                button.innerHTML =
                    "⟳ Refreshing...";


                await loadAnalytics();

                await loadPayments();

            }

            catch (error) {

                console.error(
                    "Refresh failed:",
                    error
                );

            }

            finally {

                button.disabled = false;

                button.innerHTML =
                    originalText;

            }

        }
    );

}


/* =========================================================
   PAYMENT FORM INITIALIZATION
========================================================= */

function initializePaymentForm() {

    const form =
        document.getElementById(
            "paymentForm"
        );


    if (!form) {
        return;
    }


    form.addEventListener(
        "submit",
        analyzePayment
    );

}


/* =========================================================
   APPLICATION INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        /*
           Initialize form
        */

        initializePaymentForm();


        /*
           Initialize payment history filters
        */

        initializePaymentFilters();


        /*
           Initialize refresh button
        */

        initializeRefreshButton();


        /*
           Load dashboard data
        */

        await loadAnalytics();

        await loadPayments();

    }
);
