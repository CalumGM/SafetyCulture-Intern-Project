var bcrypt = require("bcryptjs");
var mongoose = require("mongoose");

const SALT_FACTOR = 10; // what is this?

var userSchema = mongoose.Schema({ // database entry format
    username:{type:String, required:true},
    email:{type:String, required:true, unique:true},
    password:{type:String, required:false},
    createdAt:{type:Date, default:Date.now}
});

userSchema.pre("save", function(done){ // pre function executes before 
    var user = this;

    if(!user.isModified("password")){
        return done();
    }

    bcrypt.genSalt(SALT_FACTOR, function(err,salt){
        if(err){return done(err);}
        bcrypt.hash(user.password, salt, function(err, hashedPassword){
            if(err) {return done(err);}
            user.password = hashedPassword;
            done();
        });
    });

});

userSchema.methods.checkPassword = function(guess, done){
      if(this.password != null){
          bcrypt.compare(guess,this.password, function(err, isMatch){
             done(err, isMatch);
          });
      }
}

var User = mongoose.model("User", userSchema); // compiles the schema into a models

module.exports = User;