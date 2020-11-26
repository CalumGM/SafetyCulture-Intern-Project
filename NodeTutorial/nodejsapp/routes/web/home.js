var express = require("express");

var router = express.Router();


router.get("/", function(req, res) {
 res.render("home/"); // default view
 });
 
 router.get("/home", function(req,res){
     res.render("home/home"); // home view
 });

 router.get("/about", function(req, res){
    res.render("home/about"); // about view
 });

 router.get("/login", function(req, res){
    res.render("home/login"); // Log In view
 });

 router.get("/signup", function(req, res){
    res.render("home/signup"); // Log In view
 });

 module.exports = router;