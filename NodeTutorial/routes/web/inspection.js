var express = require("express");
var passport = require("passport");
//var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;

var Audit = require("../../models/audits");
var Agent = require("../../models/agents");
var router = express.Router();
//router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated
var found_agents;
var agent;
// how do I talk to the routes in this page??
router.get("/", function(req, res){ // implicit /post before each of these routes
    Agent.find({}).exec(function(err, agents){ // find all agents in database
        if(err){console.log(err);}
        found_agents = agents;
        res.render("inspections/inspections", {agents:agents}); // passing on the posts that were found matching the userID
    });
 });

router.get("/:agent_name", function(req,res){ // :postID represents a variable parameter as a route
    // find all audits done by a particular agent and sort by date accending
    Audit.find({agent_name:req.params.agent_name}).sort({date: 1}).exec(function(err, audits){ 
        if(err){console.log(err);}
        // do all calcs in here. Yes, because backend does all the heavy lifting
        var agent_data = {};
        var i;
        var day_labels = [];
        for (i=0; i<found_agents.length; i++){
            if (found_agents[i].agent_name === req.params.agent_name){
                agent = found_agents[i]; // the agent in the URL
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

        // generate date labels counting backwards since today
        for (var i = agent.time_series[0].length; i > 0; i--){
            var now = new Date();
            var previous_day = new Date();
            previous_day.setTime(now.getTime() - 1000*60*60*24*i); // milliseconds since 1970
            day_labels.push(previous_day.toISOString().slice(5,10));
            //console.log(day_labels);

            //.toISOString().slice(0,10);
        }
        // get GPS data for each audit
        var audit_GPS_data = [];
        for (i = 0; i<audits.length; i++){
            var long = audits[i]['location']['long']; 
            var lat = audits[i]['location']['lat'];
            var addr = audits[i]['location']['text'].replace(/,/g, "-"); // turn , into -
            audit_GPS_data[i] = [long, lat,  addr];
        }
        
        agent_data['GPS_data'] = audit_GPS_data;
        //console.log('audit_GPS_data', JSON.stringify(agent_data['GPS_data']));
        agent_data['day_labels'] = day_labels;
        agent_data['number_of_audits_per_day'] = agent.time_series[1];
        agent_data['audit_score_per_day'] = agent.time_series[0];

        res.render("inspections/view",{audits:audits, agent_data:JSON.stringify(agent_data), agents:found_agents});
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