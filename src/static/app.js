document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear previous activity options (keep the default option)
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsList =
          details.participants.length > 0
            ? `<ul class="participants-list">
                 ${details.participants
                   .map((participant) => `
                     <li>
                       <span class="participant-email">${participant}</span>
                       <button class="delete-participant-btn" 
                               data-activity="${name}" 
                               data-email="${participant}">
                         ×
                       </button>
                     </li>
                   `)
                   .join("")}
               </ul>`
            : '<p class="no-participants">No participants yet</p>';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p><strong>Description:</strong> ${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Capacity:</strong> ${details.participants.length}/${details.max_participants}</p>
          <div class="participants-section">
              <p><strong>Participants:</strong></p>
              ${participantsList}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners for delete buttons
      document.querySelectorAll('.delete-participant-btn').forEach(button => {
        button.addEventListener('click', handleDeleteParticipant);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    if (!email || !activity) {
      showMessage("Please fill in all fields.", "error");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: `email=${encodeURIComponent(email)}`,
        }
      );

      if (response.ok) {
        const result = await response.json();
        showMessage(result.message, "success");
        signupForm.reset();
        fetchActivities(); // Refresh the activities list
      } else {
        const error = await response.json();
        showMessage(error.detail, "error");
      }
    } catch (error) {
      console.error("Error signing up:", error);
      showMessage("Failed to sign up. Please try again.", "error");
    }
  });

  // Handle participant deletion
  async function handleDeleteParticipant(event) {
    const button = event.target;
    const activity = button.dataset.activity;
    const email = button.dataset.email;

    if (!confirm(`Are you sure you want to remove ${email} from ${activity}?`)) {
      return;
    }

    // Disable button during request
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = '...';

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/participants/${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        const result = await response.json();
        showMessage(result.message, "success");
        fetchActivities(); // Refresh the activities list
      } else {
        const error = await response.json();
        showMessage(error.detail || "Failed to remove participant", "error");
        // Re-enable button on error
        button.disabled = false;
        button.textContent = originalText;
      }
    } catch (error) {
      console.error("Error removing participant:", error);
      showMessage("Failed to remove participant. Please try again.", "error");
      // Re-enable button on error
      button.disabled = false;
      button.textContent = originalText;
    }
  }

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Initialize app
  fetchActivities();
});
