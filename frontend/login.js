document.getElementById("loginForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

try {
    const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({username, password})
});


    const data = await response.json();

    if (response.ok) {
        localStorage.setItem("token", data.access_token);
        alert("Login successful!");
        window.location.href = "dashboard.html";
    } else {
        alert("Invalid credentials");
    }
} catch (error){
    alert("server not reachable.");
}
});