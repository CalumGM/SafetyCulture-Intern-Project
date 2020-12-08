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
        console.log('agents', found_agents)
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
        var sorted_day_labels = [];
        var sorted_daily_audit_data = [];
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
            // console.log('audit date: ', audit.date.toISOString())
            // console.log('day', audit.date.getUTCDate());
            // console.log('month', audit.date.getMonth());
            // console.log('year', audit.date.getFullYear());
            // console.log('\n\n')
            date_string = audit.date.toISOString().slice(0,10);
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
        
        // sort parallel arrays: day_labels & daily_audit_data
        var list = [];
        for (var j = 0; j < day_labels.length; j++){
            list.push({'date': day_labels[j], 'audits': daily_audit_data[j]});
        }

        list.sort(function(a, b) {
            return ((a.date < b.date) ? -1 : ((a.date == b.date) ? 0 : 1));
            //Sort could be modified to, for example, sort on the age 
            // if the name is the same.
        });
        for (var k = 0; k < list.length; k++) {
            day_labels[k] = list[k].date;
            daily_audit_data[k] = list[k].audits;
        }

        // send sorted day data
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