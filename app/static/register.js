document.getElementById("register-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);
  const messageBox = document.getElementById("register-message");

  const data = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  try {
    const response = await fetch("/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      // Registration successful → redirect to login
      messageBox.innerText = "✅ Registration successful! Redirecting to login...";
        messageBox.style.color = "green";

        setTimeout(() => {
            window.location.href = "/login";
        }, 3000);
    } else {
      const errData = await response.json();
      document.getElementById("error").textContent = errData.detail || "Registration failed.";
    }
  } catch (err) {
    console.error(err);
    document.getElementById("error").textContent = "Network error.";
  }
});
