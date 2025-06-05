const http = require('http');
const express = require('express');
const app = express();

app.use(express.text());

app.post('/submit', (req, res) => {
    res.send('Received: ' + req.body);
});

const server = http.createServer(app);

server.headersTimeout = 60000;
server.listen(8080, () => {
    console.log('ProxyBeam server running on port 8080');
});
