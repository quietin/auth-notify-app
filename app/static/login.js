
document.getElementById("login-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);

  try {
    const response = await fetch("/login", {
      method: "POST",
      body: formData,  // browser automatically handle Content-Type
    });

    if (response.status === 200) {
      window.location.href = "/welcome";
    } else {
      const errData = await response.json();
      document.getElementById("error").textContent =
        errData.detail || "Login failed.";
    }
  } catch (err) {
    console.error("Login error:", err);
    document.getElementById("error").textContent = "Network error.";
  }
});
