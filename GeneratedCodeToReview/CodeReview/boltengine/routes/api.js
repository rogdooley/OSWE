const express = require('express');
const router = express.Router();
const _ = require('lodash');

let config = {
    theme: 'light',
    features: {
        registration: true,
        comments: true
    }
};

router.post('/update-config', (req, res) => {
    _.merge(config, req.body);
    res.send({ message: 'Configuration updated', config });
});

router.get('/config', (req, res) => {
    res.send(config);
});

module.exports = router;
