const express = require('express');
const bodyParser = require('body-parser');
const MongoClient = require('mongodb').MongoClient;
const app = express();

let db;
MongoClient.connect("mongodb://localhost:27017", (err, client) => {
    if (err) throw err;
    db = client.db("hexstack");
});

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.post("/submit", (req, res) => {
    const { username, comment } = req.body;
    db.collection("comments").insertOne({ username, comment, flagged: false });
    res.send("Comment submitted");
});

app.get("/admin/view", (req, res) => {
    db.collection("comments").find({ flagged: false }).toArray((err, docs) => {
        if (err) return res.status(500).send("Error loading comments");
        let html = "<h1>Admin View</h1>";
        docs.forEach(doc => {
            html += `<p><b>${doc.username}</b>: ${doc.comment}</p>`;
        });
        res.send(html);
    });
});

app.post("/flag", (req, res) => {
    const filter = req.body.filter;
    db.collection("comments").updateMany(filter, { $set: { flagged: true } });
    res.send("Comments flagged.");
});

app.listen(3000, () => {
    console.log("hexstack app running on port 3000");
});
