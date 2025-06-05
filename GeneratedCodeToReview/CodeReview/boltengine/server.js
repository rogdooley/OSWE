const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const apiRoutes = require('./routes/api');

app.use(bodyParser.json());
app.use('/api', apiRoutes);

app.listen(3000, () => {
    console.log('BoltEngine API listening on port 3000');
});
