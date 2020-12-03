var mongoose = require("mongoose");

var postSchema = mongoose.Schema({
    title: {type: String, required:true},
    content: {type: String, required:false},
    createdAt: {type: Date, default:Date.now},
    image: {type:mongoose.Schema.Types.ObjectId, required:false, unique:false}, // reference to the ID of another object
    userID: {type:mongoose.Schema.Types.ObjectId, required:false, unique:false}, // userID is used to refer to the post's user
    public: {type:Boolean, default:false, required:false, unique:false}
});

var Post = mongoose.model("Post", postSchema); // collection is named after this with an s chucked on the end

module.exports = Post;