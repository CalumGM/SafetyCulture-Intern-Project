var express = require("express");
var passport = require("passport");
var ensureAuthenticated = require("../../auth/auth").ensureAuthenticated;
var afterLogin = "/dashboard"
var User = require("../../models/user");

var router = express.Router();

// these functions define a route and where to redirect the user on each route
// <express.Router()>.<HTTP request method>(<path on the server>, <the function executed when the route is matched>)
router.get("/", function (req, res) {
   res.render("home/");
});

router.get("/home", function (req, res) {
   res.render("home/home"); 
});

router.get("/about", function (req, res) {
   res.render("home/about");
});

router.get("/login", function (req, res) {
   res.render("home/login")
});

router.get("/logout", function(req, res){
   req.logout();
   res.redirect("/home");
});

router.post("/login", passport.authenticate("login", {
   successRedirect: afterLogin,
   failureRedirect: "/login",
   failureFlash: true
}));

router.get("/signup", function (req, res) {
   res.render("home/signup")
});

router.post("/signup", function (req, res, next) {
   var username = req.body.username; // gets username from ...
   var email = req.body.email;
   var password = req.body.password;

   User.findOne({ email: email }, function (err, user) {
      if (err) { return next(err); }
      if (user) {
         req.flash("error", "There's already an account with this email"); // send error message to _header.ejs
         return res.redirect("/signup"); // go back to the signup page
      }

      var newUser = new User({
         username: username,
         password: password,
         email: email
      });

      newUser.save(next); // magic function that saves newUser to db??

   });

}, 
   passport.authenticate("login", {
   successRedirect: afterLogin, // after logging in, the user is sent back to index.ejs
   failureRedirect: "/signup",
   failureFlash: true
}));

module.exports = router;
