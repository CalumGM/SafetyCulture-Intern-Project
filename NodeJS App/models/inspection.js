var mongoose = require("mongoose");

var inspectionSchema = mongoose.Schema({
    template_id: {type: String, required:false},
    audit_id: {type: String, required:true},
    archived: {type: String, required:false},
    createdAt: {type: Date, default:Date.now},
    modifiedAt: {type: Date, default:Date.now},
    audit_data: {type:mongoose.Schema.Types.Object, required:false, unique:false},
    template_data: {type:mongoose.Schema.Types.Object, required:false, unique:false},
    header_items: {type:mongoose.Schema.Types.Array, required:false, unique:false},
    items_data: {type:mongoose.Schema.Types.Array, required:false, unique:false}, 
});

var Inspection = mongoose.model("Inspections", inspectionSchema); // collection is named after this with an s chucked on the end

module.exports = Inspection;