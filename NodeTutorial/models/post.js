var mongoose = require("mongoose");

var postSchema = mongoose.Schema({
    title: {type: String, required:true},
    content: {type: String, required:false},
    createdAt: {type: Date, default:Date.now},
    image: {type: mongoose.Schema.Types.ObjectId, required:false, unique:flase}, // reference to the ID of another object
    userID: {type:mongoose.Schema.Types.ObjectId, required:false, unique, flase}, // userID is used to refer to the post's user
    public: {type:Boolean, default:false, required:false, unique:false}
});

var Post = mongoose.model("Post", postSchema);

module.exports = Post;