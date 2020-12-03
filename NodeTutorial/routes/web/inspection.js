var express = require("express");
var passport = require("passport");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;

var Inspection = require("../../models/inspection");
var Agent = require("../../models/agents");
var router = express.Router();
router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated

// how do I talk to the routes in this page??
router.get("/", function(req, res){ // implicit /post before each of these routes
    Agent.find({}).exec(function(err, agents){ // find in database
        if(err){console.log(err);}
        res.render("inspections/inspections", {agents:agents}); // passing on the posts that were found matching the userID
    });
 });

 module.exports = router;