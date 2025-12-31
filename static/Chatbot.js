let step = "name";

/* -------------------------
   Questions
-------------------------- */
const questions = {
    dob: "May I know your date of birth? (DD/MM/YYYY)",
    retirement: "When would you like to retire? (e.g. 60)",
    monthly: "How much do you need per month during retirement? (RM)",
    epf: "May I know how much you currently have in EPF / savings? (RM)",
    phone: "Please enter your phone number so we can provide you with updates from time to time on suitable offers and packages",
    contribution: "How much would you like to contribute monthly towards your retirement plan?",
    email: "Please type your email address, we will send you an email summary of our conversation for your reference"
};

/* -------------------------
   Helpers
-------------------------- */
function addMessage(text, sender = "bot") {
    const chat = document.getElementById("chat");
    chat.innerHTML += `<div class="${sender}">${text.replace(/\n/g, "<br>")}</div>`;
    chat.scrollTop = chat.scrollHeight;
}

function showTyping(show = true) {
    document.getElementById("typing").classList.toggle("hidden", !show);
}

function setInputDisabled(disabled) {
    const input = document.getElementById("input");
    input.disabled = disabled;
    input.placeholder = disabled ? "Please select an option using the buttons" : "";
}

/* -------------------------
   Simulate bot typing delay
-------------------------- */
function botResponse(callback) {
    showTyping(true);
    setTimeout(() => {
        showTyping(false);
        callback();
    }, 3000);
}

/* -------------------------
   Send message
-------------------------- */
function send() {
    const input = document.getElementById("input");
    const value = input.value.trim();
    input.value = "";

    if (!value && step !== "contribution") return;

    addMessage(value, "user");

    if (step === "contribution") {
        addMessage("❌ Please choose a contribution using the buttons.", "bot");
        return;
    }

    let endpoint = "";
    let payload = {};

    switch (step) {
        case "name": endpoint = "/submit_name"; payload = { name: value }; break;
        case "dob": endpoint = "/submit_dob"; payload = { dob: value }; break;
        case "retirement": endpoint = "/submit_retirement"; payload = { retirement_age: value }; break;
        case "monthly": endpoint = "/submit_monthly"; payload = { monthly: value }; break;
        case "epf": endpoint = "/submit_epf"; payload = { epf: value }; break;
        case "phone": endpoint = "/submit_phone"; payload = { phone: value }; break;
        case "email": endpoint = "/submit_email"; payload = { email: value }; break;
        default: return;
    }

    botResponse(() => {
        fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                addMessage(data.error);
                return;
            }

            // Display multiple messages if returned
            if (data.messages) {
                data.messages.forEach(msg => addMessage(msg));
            } else {
                addMessage(data.message);
            }

            step = data.next;

            if (step === "contribution") {
                addMessage("Well done. That’s an excellent option to start with. Let me calculate how much you will have.");
                setTimeout(() => {
                    showContributionButtons();
                    setInputDisabled(true);
                }, 1000);
            } else {
                setInputDisabled(false);
            }

            if (questions[step]) {
                setTimeout(() => addMessage(questions[step]), 500);
            }

            if (step === "signup") showSignupButtons();
        });
    });
}

/* -------------------------
   Contribution buttons
-------------------------- */
function showContributionButtons() {
    document.getElementById("buttons").innerHTML = `
        <button onclick="selectContribution(200)">RM 200</button>
        <button onclick="selectContribution(400)">RM 400</button>
        <button onclick="selectContribution(600)">RM 600</button>
        <button onclick="selectContribution(800)">RM 800</button>
    `;
}

function selectContribution(amount) {
    addMessage(`RM ${amount}`, "user");

    botResponse(() => {
        fetch("/submit_contribution", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount })
        })
        .then(res => res.json())
        .then(data => {
            if (data.messages) {
                data.messages.forEach(msg => addMessage(msg));
            } else {
                addMessage(data.message);
            }

            step = data.next;
            document.getElementById("buttons").innerHTML = "";
            setInputDisabled(false);

            if (questions[step]) {
                setTimeout(() => addMessage(questions[step]), 500);
            }
        });
    });
}

/* -------------------------
   Signup buttons
-------------------------- */
function showSignupButtons() {
    document.getElementById("buttons").innerHTML = `
        <button onclick="selectSignup('yes')">Yes</button>
        <button onclick="selectSignup('no')">No</button>
    `;
}

function selectSignup(choice) {
    addMessage(choice.toUpperCase(), "user");

    botResponse(() => {
        fetch("/submit_signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ choice })
        })
        .then(res => res.json())
        .then(data => {
            if (data.messages) {
                data.messages.forEach(msg => addMessage(msg));
            } else {
                addMessage(data.message);
            }

            step = data.next;
            document.getElementById("buttons").innerHTML = `
                <button onclick="restartChat()">Restart Again</button>
            `;
        });
    });
}

/* -------------------------
   Restart chat
-------------------------- */
function restartChat() {
    location.reload();
}

/* -------------------------
   Enter key support
-------------------------- */
document.getElementById("input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        send();
    }
});

/* -------------------------
   Initial message
-------------------------- */
addMessage("Hello, I’m Jenny, your super agent that will guide you 😊");
addMessage("May I know your name?");
