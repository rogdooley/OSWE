const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const jwt = require('jsonwebtoken');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const SECRET = "hardcodedsecret";

app.get('/token', (req, res) => {
    const user = req.query.user || "guest";
    const token = jwt.sign({ user: user }, SECRET);
    res.send(token);
});

wss.on('connection', (ws, req) => {
    const token = req.url.split("token=")[1];
    try {
        const payload = jwt.verify(token, SECRET);
        ws.send(`Hello ${payload.user}`);
    } catch (e) {
        ws.close();
    }

    ws.on('message', (msg) => {
        const data = JSON.parse(msg);
        if (data.type === "log") {
            console.log("Log:", data.content);
        }
    });
});

server.listen(8080, () => {
    console.log("halcyonfeed running");
});
