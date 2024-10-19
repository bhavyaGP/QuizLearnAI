// Your quiz data in JSON format
// // const quizData = [
// {
//     question: 'What term is used to describe the memory space allocated for variables and functions within a Javascript code?',
//         options: [
//             'A. Execution stack',
//             'B. Variable environment',
//             'C. Memory heap',
//             'D. Control flow'
//         ],
//             answer: 'B. Variable environment'
// },
// {
//     question: "According to the tutorial, what is the nature of a function's execution context in Javascript?",
//         options: [
//             'A. It is dependent on the global execution context.',
//             'B. It shares the same memory space as the global execution context.',
//             'C. It is independent and has its own memory space.',
//             'D. It only allocates memory for variables and not for functions.'
//         ],
//             answer: 'C. It is independent and has its own memory space.'
// },
// {
//     question: 'What concept will be explained in future videos, as promised at the end of this tutorial?',
//         options: [
//             'A. Hoisting in Javascript',
//             'B. Callbacks in Javascript',
//             'C. Promises in Javascript',
//             'D. Closures in Javascript'
//         ],
//             answer: 'D. Closures in Javascript'
// }
// ];


let timeLeft = 300;
let timer;
let userAnswers = {};
const totalQuestions = quizData.length;

// Start Timer
function startTimer() {
    timer = setInterval(function () {
        timeLeft--;
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        document.getElementById('time').textContent =
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        // Auto-submit when time runs out
        if (timeLeft <= 0) {
            clearInterval(timer);
            submitQuiz();
        }
    }, 1000);
}

// Render Quiz
function renderQuiz() {
    const quizContainer = document.getElementById('quiz-container');
    quizData.forEach((question, index) => {
        const questionElement = document.createElement('div');
        questionElement.className = 'question';
        questionElement.innerHTML = `
                    <h3>Question ${index + 1}</h3>
                    <p>${question.question}</p>
                    <ul class="options">
                        ${question.options.map((option, optionIndex) => `
                            <li>
                                <label>
                                    <input type="radio" name="q${index}" value="${option}">
                                    ${option}
                                </label>
                            </li>
                        `).join('')}
                    </ul>
                `;
        quizContainer.appendChild(questionElement);
    });
}

// Update Progress Bar
function updateProgress() {
    const answeredQuestions = Object.keys(userAnswers).length;
    const progressPercentage = (answeredQuestions / totalQuestions) * 100;
    document.getElementById('progress').style.width = `${progressPercentage}%`;
}

// Submit Quiz
function submitQuiz() {
    clearInterval(timer); // Stop the timer
    document.getElementById('submit-btn').disabled = true; // Disable submit button after submission

    // Collect user answers
    quizData.forEach((_, index) => {
        const selectedOption = document.querySelector(`input[name="q${index}"]:checked`);
        userAnswers[index] = selectedOption ? selectedOption.value : null;
    });

    // Calculate score and display feedback
    let score = 0;
    quizData.forEach((question, index) => {
        const questionElement = document.querySelectorAll('.question')[index];
        const userAnswer = userAnswers[index];
        const correctAnswer = question.answer;

        if (userAnswer === correctAnswer) {
            score++;
            questionElement.classList.add('correct');
        } else {
            questionElement.classList.add('incorrect');
        }

        // Display correct and incorrect answers
        const options = questionElement.querySelectorAll('.options li');
        options.forEach((option, optionIndex) => {
            if (option.querySelector('input').value === correctAnswer) {
                option.style.fontWeight = 'bold';
                option.style.color = 'green';
            }

            if (userAnswer !== correctAnswer && option.querySelector('input').value === userAnswer) {
                option.style.textDecoration = 'line-through';
                option.style.color = 'red';
            }
        });
    });

    // Display result summary
    const resultSummary = document.createElement('div');
    resultSummary.className = 'result-summary';
    resultSummary.innerHTML = `You scored ${score} out of ${quizData.length}.`;
    document.querySelector('.container').insertBefore(resultSummary, document.getElementById('quiz-container'));
}

// Initialize Quiz
renderQuiz();
startTimer();

// Add event listeners to update progress as users answer questions
document.querySelectorAll('input[type="radio"]').forEach(input => {
    input.addEventListener('change', updateProgress);
});