var express = require("express");
var passport = require("passport");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;

var router = express.Router();
//router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated

router.get("/", function(req, res){ // implicit /post before each of these routes
    console.log('prof')
    res.render("profile/profile");
});

module.exports = router;