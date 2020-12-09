var mongoose = require("mongoose");

var auditSchema = mongoose.Schema({
    audit_id: {type: String, required:true},
    agent_name: {type: String, required:true},
    date: {type: Date, default:Date.now},
    scores: {type:mongoose.Schema.Types.Object, required:false, unique:false},
    location: {type:mongoose.Schema.Types.Object, required:false, unique:false},
});

var Audit = mongoose.model("temp_audits", auditSchema); // collection is named after this with an s chucked on the end

module.exports = Audit;