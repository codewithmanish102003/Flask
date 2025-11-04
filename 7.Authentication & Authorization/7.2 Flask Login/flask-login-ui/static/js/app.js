document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", function(event) {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Invalid credentials");
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            window.location.href = "/dashboard";
        })
        .catch(error => {
            alert(error.message);
        });
    });
});