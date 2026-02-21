console.log("Register JS Loaded");

// ===============================
// WAIT UNTIL DOM IS READY
// ===============================
document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // PASSWORD VALIDATION FUNCTION
    // ===============================
    function validatePassword(password) {
        return (
            /.{8,}/.test(password) &&
            /[A-Z]/.test(password) &&
            /[a-z]/.test(password) &&
            /[0-9]/.test(password) &&
            /[!@#$%^&*]/.test(password)
        );
    }

    // ===============================
    // PASSWORD RULES UI
    // ===============================
    const passwordInput = document.getElementById("password");
    const toggleRulesBtn = document.getElementById("toggleRules");
    const passwordRulesDiv = document.getElementById("passwordRules");

    let rulesVisible = false;

    function showRules() {
        if (!rulesVisible) {
            rulesVisible = true;
            passwordRulesDiv.style.maxHeight = "500px";
            toggleRulesBtn.style.display = "block";
        }
    }

    function hideRules() {
        rulesVisible = false;
        passwordRulesDiv.style.maxHeight = "0px";
        toggleRulesBtn.style.display = "none";
    }

    // Hide rules initially
    hideRules();

    passwordInput.addEventListener("focus", showRules);
    passwordInput.addEventListener("blur", hideRules);

    passwordInput.addEventListener("input", function () {
        const password = passwordInput.value;

        const rules = {
            lengthRule: /.{8,}/,
            upperRule: /[A-Z]/,
            lowerRule: /[a-z]/,
            numberRule: /[0-9]/,
            specialRule: /[!@#$%^&*]/
        };

        Object.keys(rules).forEach(ruleId => {
            const ruleElement = document.getElementById(ruleId);
            if (rules[ruleId].test(password)) {
                ruleElement.innerHTML = "✅ " + ruleElement.innerText.replace("❌ ", "").replace("✅ ", "");
                ruleElement.style.color = "green";
            } else {
                ruleElement.innerHTML = "❌ " + ruleElement.innerText.replace("❌ ", "").replace("✅ ", "");
                ruleElement.style.color = "red";
            }
        });
    });

    // ===============================
    // FORM SUBMISSION
    // ===============================
    const registerForm = document.getElementById("registerForm");

    registerForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        console.log("Form submitted");

        const username = document.getElementById("username").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirmPassword").value;

        // Password validation
        if (!validatePassword(password)) {
            alert("Password does not meet security requirements.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:8000/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password,
                    interests: ["General"]
                })
            });

            const data = await response.json();
            console.log("Server response:", data);

            if (response.ok) {
                alert("Registration successful!");
                window.location.href = "login.html";
            } else {
                alert(data.detail || "Registration failed.");
            }

        } catch (error) {
            console.error("Registration error:", error);
            alert("Server connection failed.");
        }
    });

});