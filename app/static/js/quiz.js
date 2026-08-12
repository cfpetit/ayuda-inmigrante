document.addEventListener("DOMContentLoaded", function() {
    let currentStep = 1;
    const totalSteps = 3;
    const answers = {};

    const progressFill = document.getElementById("progressFill");

    function updateProgress() {
        const percentage = (currentStep / totalSteps) * 100;
        if (progressFill) {
            progressFill.style.width = percentage + "%";
        }
    }

    // Attach click listeners to options
    document.querySelectorAll(".quiz-option").forEach(button => {
        button.addEventListener("click", function() {
            const step = this.dataset.step;
            const key = this.dataset.key;
            const value = this.dataset.value;

            answers[key] = value;

            if (currentStep < totalSteps) {
                document.getElementById(`step-${currentStep}`).classList.remove("active");
                currentStep++;
                document.getElementById(`step-${currentStep}`).classList.add("active");
                updateProgress();
            } else {
                calculateResult();
            }
        });
    });

    function calculateResult() {
        // Hide all quiz steps
        document.querySelectorAll(".quiz-step").forEach(step => step.classList.remove("active"));
        
        const resultSection = document.getElementById("quiz-result");
        const recommendedTitle = document.getElementById("recommendedTitle");
        const recommendedDesc = document.getElementById("recommendedDesc");
        const applyBtn = document.getElementById("applyBtn");

        resultSection.classList.add("active");
        if (progressFill) progressFill.style.width = "100%";

        let category = "Work Visa";
        let desc = "Based on your criteria, standard employment authorization fits your profile.";

        if (answers.reason === 'study') {
            category = "Student Residency";
            desc = "You qualify for a Student Residency Visa to attend accredited educational institutions.";
        } else if (answers.reason === 'family') {
            category = "Family Reunification";
            desc = "You may be eligible to apply for residence under family sponsorship programs.";
        } else if (answers.reason === 'protection') {
            category = "Asylum / Protection";
            desc = "You may qualify for international protection or humanitarian asylum assistance.";
        } else if (answers.reason === 'work' && answers.hasOffer === 'no') {
            category = "Work Visa";
            desc = "You will need to secure a valid job offer before submitting your formal application.";
        }

        recommendedTitle.textContent = category;
        recommendedDesc.textContent = desc;

        // Redirect URL to case creation with pre-selected type
        applyBtn.href = `/cases/new?type=${encodeURIComponent(category)}`;
    }
});
