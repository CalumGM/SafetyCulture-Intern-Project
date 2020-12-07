var express = require("express");
var passport = require("passport");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;

var Audit = require("../../models/audits");
var Agent = require("../../models/agents");
var router = express.Router();
router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated
var found_agents;
var agent;
// how do I talk to the routes in this page??
router.get("/", function(req, res){ // implicit /post before each of these routes
    console.log('blah blah blah')
    Agent.find({}).exec(function(err, agents){ // find all agents in database
        if(err){console.log(err);}
        res.render("inspections/inspections", {agents:agents}); // passing on the posts that were found matching the userID
    });
 });

router.get("/:agent_name", function(req,res){ // :postID represents a variable parameter as a route
    Agent.find({}).exec(function(err, agents){ // find all agents in database
        //doesnt work without console.log
        // console.log('agents'); 
        setTimeout(function(){ found_agents = agents; }, 3000);
        found_agents = agents;
        //console.log('agents', found_agents)
        if(err){console.log(err);}
    });
    Audit.find({agent_name:req.params.agent_name}).exec(function(err, audits){ // find all audits done by a particular agent
        if(err){console.log(err);}
        // do all calcs in here. Yes, because backend does all the heavy lifting
        var agent_data = {};
        var audits_data = {};
        var i;
        var daily_audit_count = {};
        var day_labels = [];
        var daily_audit_data = [];
        for (i=0; i<found_agents.length; i++){
            if (found_agents[i].agent_name === req.params.agent_name){
                agent = found_agents[i];
            }
        };
        
        if (!agent.avg_score){ // treating the data as dirty when we know it is clean
            agent_data['avg_score'] = calculateAverageScore(audits);
            // push new calculated average (not gonna do) 
        } else{
            agent_data['avg_score'] = agent.avg_score;
        };
        agent_data['number_of_inspections'] = audits.length;
        agent_data['agent_name'] = audits[0].agent_name;

        audits.forEach(audit => {
            date_string = audit.date.getFullYear() +'-'+ audit.date.getMonth() +'-'+ audit.date.getDate()
            if (date_string in daily_audit_count) {
                daily_audit_count[date_string] += 1;
            } else {
                daily_audit_count[date_string] = 1;
                day_labels.push(date_string)
            };
        });
        for (var key in daily_audit_count) {
            if (daily_audit_count.hasOwnProperty(key)) {
                daily_audit_data.push(parseFloat(daily_audit_count[key]));
            }
        };
        agent_data['day_labels'] = day_labels; // only the days that contain atleast 1 audit
        agent_data['daily_audit_data'] = daily_audit_data; // total number of audits for each day

        res.render("inspections/view",{audits:audits, agent_data:agent_data, agents:found_agents});
    });
});

function calculateAverageScore(audits){
    var total = 0;
    var count = audits.length;
    audits.forEach(audit => {
        total += parseFloat(audit.score.percentage_score);
    });
    return total/count;
}

 module.exports = router;