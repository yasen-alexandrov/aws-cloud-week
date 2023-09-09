const express = require('express');

const app = express();

app.get('/', function (req, res){
    res.send("Hello World from Pulumi and AWS! ONCE MORE!");
});

app.listen(80);
