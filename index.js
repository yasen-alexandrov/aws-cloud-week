const express = require('express');

const app = express();

app.get('/', function (req, res){
    res.send("Hello World from Pulumi and AWS! HOPE YOU'RE FINE!");
}); 

app.listen(80);
