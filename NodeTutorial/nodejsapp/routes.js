const e = require("express");
var express = require("express");
var router = express.Router();

router.get("/", function(req, res){
    console.log("Hello Start Page")
    res.render("index");
});

module.exports = router;