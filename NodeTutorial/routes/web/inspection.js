var express = require("express");
var passport = require("passport");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;

var Audit = require("../../models/audits");
var Agent = require("../../models/agents");
var router = express.Router();
router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated
var found_agents;
// how do I talk to the routes in this page??
router.get("/", function(req, res){ // implicit /post before each of these routes
    Agent.find({}).exec(function(err, agents){ // find all agents in database
        if(err){console.log(err);}
        res.render("inspections/inspections", {agents:agents}); // passing on the posts that were found matching the userID
    });
 });

router.get("/:agent_name", function(req,res){ // :postID represents a variable parameter as a route
    Agent.find({}).exec(function(err, agents){ // find all agents in database
        found_agents = agents;
        if(err){console.log(err);}
    });
    Audit.find({agent_name:req.params.agent_name}).exec(function(err, audits){ // find all audits done by a particular agent
        if(err){console.log(err);}
        res.render("inspections/view",{audits:audits, agents:found_agents});
    });
});

 module.exports = router;