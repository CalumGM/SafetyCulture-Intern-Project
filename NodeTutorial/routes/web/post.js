var express = require("express");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;

var router = express.Router();

router.use(ensureAuthenticated); // ensures that all routes in this route are now authenticated

// the posts route is in this seperate file so that it can be authenticated.
router.get("/", function(req, res){
    res.render("post/posts")
});

router.get("/add", function(req, res){
    res.render("post/addpost");
});

module.exports = router;