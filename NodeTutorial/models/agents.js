var mongoose = require("mongoose");

var agentSchema = mongoose.Schema({
    agent_name: {type: String, required:true},
    avg_score: {type: String, required:false},
    time_series: {type:mongoose.Schema.Types.Array, required:false, unique:false},
});

var Agent = mongoose.model("agents", agentSchema); // collection is named after this with an s chucked on the end

module.exports = Agent;