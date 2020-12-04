var express = require("express");
var passport = require("passport");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;

var AuditModel = require("../../models/audits");
var AgentModel = require("../../models/agents");

var router = express.Router();
router.use(ensureAuthenticated);// ensures that all routes in this route are now authenticated

// how do I talk to the routes in this page??
router.get("/", function(req, res){ // implicit /post before each of these routes
    AuditModel.find({}).exec(function(err, audits){ // find in database
        AuditModel.find({}).exec(function(err, agents){ // find in database
            if(err){console.log(err);}
            console.log('Dashboard Accessed');
            var agent_data = {}
            var agent_scores = {}
            audits.forEach(audit => {
                if (audit.agent_name in agent_data) {
                    agent_data[audit.agent_name] += 1;
                } else {
                    agent_data[audit.agent_name] = 1;
                };
                if (audit.agent_name in agent_scores) {
                    agent_scores[audit.agent_name] += parseFloat(audit.score.percentage_score);
                } else {
                    agent_scores[audit.agent_name] = parseFloat(audit.score.percentage_score);
                };
            });
            
            var agent_audit_totals = [];
            var agent_score_totals = [];
            var agent_names = [];
            var all_audit_count = 0;
            var all_audit_score = 0;
            for (var key in agent_data) {
                if (agent_data.hasOwnProperty(key)) {
                    agent_audit_totals.push(parseFloat(agent_data[key]));
                    agent_names.push(key);
                }
            };
            for (var key in agent_scores) {
                if (agent_scores.hasOwnProperty(key)) {
                    agent_score_totals.push(parseFloat(agent_scores[key]));
                }
            };
            all_audit_count = (agent_audit_totals.reduce((a, b) => {
                return parseFloat(a) + parseFloat(b);
            }));
            all_audit_score = (agent_score_totals.reduce((a, b) => {
                return parseFloat(a) + parseFloat(b);
            }));
            all_avg_audit_score = all_audit_score/all_audit_count;

            agent_scores = [];
            for (i = 0; i < agent_names.length; i++) {
                agent_scores.push((agent_score_totals[i]/agent_audit_totals[i] - all_avg_audit_score) / 100);
            }
            // agent_scores = [.2,.3,-.1,-.2,.05,-.3];
            res.render(
                "dashboard/dashboard", 
                {audits:audits, agents:agents, agent_totals:agent_audit_totals, agent_names: agent_names, agent_rel_scores:agent_scores}
            );
        });
    });
 });

 module.exports = router;