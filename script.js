document.addEventListener("DOMContentLoaded", function() {
    // LOGIN FUNCTIONALITY
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", function(event) {
            event.preventDefault();

            let email = document.getElementById("email").value;
            let password = document.getElementById("password").value;

            // Simulated user data (replace with backend authentication)
            const users = {
                "student@example.com": { password: "student123", role: "student" },
                "company@example.com": { password: "company123", role: "company" }
            };

            if (users[email] && users[email].password === password) {
                alert("Login successful!");
                
                // Redirect based on role
                if (users[email].role === "student") {
                    window.location.href = "student-dashboard.html";
                } else {
                    window.location.href = "company-dashboard.html";
                }
            } else {
                alert("Invalid email or password.");
            }
        });
    }

    // JOB POSTING FUNCTIONALITY (For company dashboard)
    const jobForm = document.getElementById("jobForm");
    const jobListings = document.getElementById("jobListings");
    if (jobForm) {
        jobForm.addEventListener("submit", function(event) {
            event.preventDefault();
            
            let jobTitle = document.getElementById("jobTitle").value;
            let companyName = document.getElementById("companyName").value;
            let jobDescription = document.getElementById("jobDescription").value;
            let skillsRequired = document.getElementById("skillsRequired").value;
            let jobLocation = document.getElementById("jobLocation").value;
            let salary = document.getElementById("salary").value;

            let jobHTML = `
                <div class="job-card">
                    <h3>${jobTitle}</h3>
                    <p><strong>Company:</strong> ${companyName}</p>
                    <p><strong>Description:</strong> ${jobDescription}</p>
                    <p><strong>Skills:</strong> ${skillsRequired}</p>
                    <p><strong>Location:</strong> ${jobLocation}</p>
                    <p><strong>Salary:</strong> ${salary}</p>
                </div>
            `;

            jobListings.innerHTML += jobHTML;
            jobForm.reset(); // Clear form fields
        });
    }

    // STUDENT SLIDER FUNCTIONALITY (For company dashboard)
    const slider = document.querySelector(".student-slider");
    if (slider) {
        let scrollAmount = 0;
        setInterval(() => {
            scrollAmount += 200;
            if (scrollAmount >= slider.scrollWidth - slider.clientWidth) {
                scrollAmount = 0;
            }
            slider.scrollTo({ left: scrollAmount, behavior: "smooth" });
        }, 2000);
    }
});