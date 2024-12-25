const dotenv = require("dotenv");
dotenv.config();
const express = require('express');

const app = express();
const { createProxyMiddleware } = require('http-proxy-middleware');

const port = process.env.PORT || 3000;

app.use('/gen', createProxyMiddleware({ target: 'http://localhost:5000', changeOrigin: true }));
app.use('/user', createProxyMiddleware({ target: 'http://localhost:3001', changeOrigin: true }));

app.listen(port, () => {
    console.log(`server is running on port http://localhost:${port}`);
});