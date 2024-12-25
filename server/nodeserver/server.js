const express = require('express');
const app = express();
const port = process.env.PORT || 3001;

app.use(express.json());

app.get('/api', (req, res) => {
    res.send({ message: 'Hello from server' });
});

app.listen(port, () => {
    console.log(`server is running on port http://localhost:${port}`);
});

