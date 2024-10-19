const express = require('express');
const { exec } = require('child_process');
const bodyParser = require('body-parser');
const path = require('path');
const session = require('express-session');
const app = express();
const PORT = 3000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Set up session middleware
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false }
}));

app.set('view engine', 'ejs');
app.use(express.static("views"));




app.get('/', (req, res) => {
    res.render('index');
});

app.post('/generate', (req, res) => {
    const { youtubeLink, quizNo, difficulty } = req.body;
    console.log('Request received:', { youtubeLink, quizNo, difficulty });

    // Validate input
    if (!youtubeLink || !quizNo) {
        return res.status(400).json({ error: 'youtubeLink and quizNo are required' });
    }

    const parsedQuizNo = parseInt(quizNo);
    if (isNaN(parsedQuizNo) || parsedQuizNo <= 0 || parsedQuizNo > 50) {
        return res.status(400).json({ error: 'quizNo must be a positive integer between 1 and 50.' });
    }

    const escapedLink = youtubeLink.replace(/"/g, '\\"');
    console.log(`Escaped link: ${escapedLink}`);

    const command = `python ./app.py "${escapedLink}" ${parsedQuizNo} ${difficulty}`;
    console.log(`Executing command: ${command}`);

    // Execute the command
    exec(command, { timeout: 60000 }, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing script: ${error.message}`);
            return res.status(500).json({ error: 'Internal Server Error' });
        }

        if (stderr) {
            console.error(`Script error: ${stderr}`);
            return res.status(500).json({ error: 'Script execution error' });
        }

        // console.log(stdout);

        try {
            const jsonResponse = JSON.parse(stdout);
            // const jsonResponse = stdout;
            console.log('Parsed response:', jsonResponse);

            // Handle potential error field in the JSON response
            if (jsonResponse.error) {
                return res.status(500).json({ error: jsonResponse.error });
            }

            // Store the quiz data in the session
            req.session.quizData = {
                youtube_link: youtubeLink,
                quiz_number: parsedQuizNo,
                summary: jsonResponse.summary,
                quiz: jsonResponse.questions
            };

            return res.render('result', req.session.quizData);
        } catch (parseError) {
            console.error('Failed to parse response from Python script:', parseError);
            return res.status(500).json({ error: 'Failed to parse response from Python script' });
        }
    });
});


app.get('/take-quiz', (req, res) => {
    if (!req.session.quizData) {
        return res.redirect('/');
    }
    console.log('Quiz data:', req.session.quizData.quiz);

    res.render('quiz', { quiz: req.session.quizData.quiz });
});


// Handle 404 errors
app.use((req, res) => {
    res.status(404).send('Not Found');
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}/`);
});
