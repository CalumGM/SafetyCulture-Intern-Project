var express = require("express");
var passport = require("passport");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;
var AuditModel = require("../../models/audits");;

function sum(obj) {
    var sum = 0;
    for(var elem in obj ) {
      if(obj.hasOwnProperty(elem)) sum += parseFloat(obj[elem]);
    }
    return sum;
};

async function prepare_page_data(req, res, date_start, date_end) {
    var dashboard_data = {};
    if (date_start != false) {
        date_start = new Date(date_start);
        date_end = new Date(date_end);
    } else {
        date_start
        date_start = new Date('2020-11-18');
        date_end = new Date(Date.now())
    }

    AuditModel.find({"date":{ $gte:date_start, $lt:date_end}}).sort({date: 0}).exec(function(err, audits) { // find in database
        if(err){console.log(err);}

        var agent_name_to_inspection_count = {}
        var agent_name_to_total_score = {}
        var agent_names = [];
        var agent_name_to_total_score = [];
        var daily_audit_count = {};
        var day_labels = []
        var daily_audit_data = []
        var audit_location_data = []

        audits.forEach(audit => {
            audit_location_data.push([audit.location.lat,audit.location.long, 1-(audit.scores.score_percentage/100)]);
            // Create Agent_Dictionaries
            // Create Agent Name List
            if (audit.agent_name in agent_name_to_inspection_count) {
                agent_name_to_inspection_count[audit.agent_name] += 1;   
            } else {
                agent_name_to_inspection_count[audit.agent_name] = 1;
                agent_names.push(audit.agent_name);
            };
            // Create the Agent Total Score Data
            if (audit.agent_name in agent_name_to_total_score) {
                agent_name_to_total_score[audit.agent_name] += parseFloat(audit.scores.score_percentage);
            } else {
                agent_name_to_total_score[audit.agent_name] = parseFloat(audit.scores.score_percentage);
            };
            // Create the All-Agent Daily Data
            
            date_string = (audit.date.toISOString()).slice(5,10)
            if (date_string in daily_audit_count) {
                daily_audit_count[date_string] += 1;
            } else {
                daily_audit_count[date_string] = 1;
                day_labels.push(date_string)
            };
        });
        
        var agent_audit_totals = [];
        for (var key in agent_name_to_inspection_count) {
            if (agent_name_to_inspection_count.hasOwnProperty(key)) {
                agent_audit_totals.push(parseFloat(agent_name_to_inspection_count[key]));
            }
        };  
        var agent_score_totals = [];
        for (var key in agent_name_to_total_score) {
            if (agent_name_to_total_score.hasOwnProperty(key)) {
                agent_score_totals.push(parseFloat(agent_name_to_total_score[key]));
            }
        };

        var all_audit_count = 0;
        var all_audit_score = 0;
        all_audit_count = sum(agent_audit_totals)
        all_audit_score = sum(agent_score_totals)
        all_avg_audit_score = all_audit_score/all_audit_count;

        for (i = 0; i < agent_names.length; i++) {
            agent_name_to_total_score.push((agent_score_totals[i] / agent_audit_totals[i] - all_avg_audit_score)*(1+i));
        }
        for (var key in daily_audit_count) {
            if (daily_audit_count.hasOwnProperty(key)) {
                daily_audit_data.push(parseFloat(daily_audit_count[key]));
            }
        };
        all_data = {'agent_totals': agent_audit_totals, 'agent_names': agent_names, 'agent_rel_scores': agent_name_to_total_score, 'day_labels': day_labels, 'daily_audit_count': daily_audit_data, 'audit_location_data': audit_location_data}
        dashboard_data = JSON.stringify(all_data);
        res.render(
            "dashboard/dashboard", {dashboard_data}
        );
    });
    
};

var router = express.Router();
router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated

router.get("/", function(req, res){ // implicit /post before each of these routes
    prepare_page_data(req,res, false, false).catch(error => console.log(error.stack));
});

router.get('/:start/:end', function (req, res) { // Allows /YYYY-MM-DD/YYYY-MM-DD formatting for start/end date of data.
    prepare_page_data(req,res, req.params['start'],req.params['end']).catch(error => console.log(error.stack));
});

 module.exports = router;