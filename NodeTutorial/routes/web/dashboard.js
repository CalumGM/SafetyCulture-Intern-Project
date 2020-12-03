var express = require("express");
var passport = require("passport");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;

var Inspection = require("../../models/inspection");

var router = express.Router();
router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated

// how do I talk to the routes in this page??
router.get("/", function(req, res){ // implicit /post before each of these routes
    Inspection.find({}).exec(function(err, inspections){ // find in database
        if(err){console.log(err);}
        console.log('Dashboard Accessed');
        res.render("dashboard/dashboard", {inspections:inspections}); // passing on the posts that were found matching the userID
    });
 });

 module.exports = router;