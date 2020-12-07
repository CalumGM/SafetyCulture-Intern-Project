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
}

var router = express.Router();
router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated

// how do I talk to the routes in this page??
router.get("/", function(req, res){ // implicit /post before each of these routes
    AuditModel.find({}).exec(function(err, audits) { // find in database
        if(err){console.log(err);}

        var agent_data = {}
        var agent_scores = {}
        var agent_audit_totals = [];
        var agent_score_totals = [];
        var agent_names = [];
        var all_audit_count = 0;
        var all_audit_score = 0;
        var agent_scores = [];
        var daily_audit_count = {};
        var day_labels = []
        var daily_audit_data = []

        audits.forEach(audit => {
            if (audit.agent_name in agent_data) {
                agent_data[audit.agent_name] += 1;   
            } else {
                agent_data[audit.agent_name] = 1;
                agent_names.push(audit.agent_name);
            };
            if (audit.agent_name in agent_scores) {
                agent_scores[audit.agent_name] += parseFloat(audit.score.percentage_score);
            } else {
                agent_scores[audit.agent_name] = parseFloat(audit.score.percentage_score);
            };
            date_string = audit.date.getFullYear() +'-'+ audit.date.getMonth() +'-'+ audit.date.getDate()
            if (date_string in daily_audit_count) {
                daily_audit_count[date_string] += 1;
            } else {
                daily_audit_count[date_string] = 1;
                day_labels.push(date_string)
            };
        });
        for (var key in agent_data) {
            if (agent_data.hasOwnProperty(key)) {
                agent_audit_totals.push(parseFloat(agent_data[key]));
            }
        };

        for (var key in agent_scores) {
            if (agent_scores.hasOwnProperty(key)) {
                agent_score_totals.push(parseFloat(agent_scores[key]));
            }
        };
        all_audit_count = sum(agent_audit_totals)
        all_audit_score = sum(agent_score_totals)
        all_avg_audit_score = all_audit_score/all_audit_count;

        for (i = 0; i < agent_names.length; i++) {
            agent_scores.push((agent_score_totals[i] / agent_audit_totals[i] - all_avg_audit_score) / 100);
        }
        for (var key in daily_audit_count) {
            if (daily_audit_count.hasOwnProperty(key)) {
                daily_audit_data.push(parseFloat(daily_audit_count[key]));
            }
        };

        res.render(
            "dashboard/dashboard", 
            {audits: audits, agent_totals:agent_audit_totals, agent_names: agent_names, agent_rel_scores:agent_scores, day_labels: day_labels, daily_audit_count: daily_audit_data}
        );
    });
 });

 module.exports = router;