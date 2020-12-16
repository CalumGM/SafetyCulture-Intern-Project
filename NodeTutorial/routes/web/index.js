var express = require("express");

var router = express.Router();


//TODO:: add in error and info 

router.use(function(req,res, next){
    // res.locals are global variables...yuck
    res.locals.currentUser = req.user;
    res.locals.myVariable = "Test";
    res.locals.error = req.flash("error");
    res.locals.info = req.flash("info");
    next();
});


router.use("/", require("./home"));
router.use("/agents", require("./agent"));
router.use("/dashboard", require("./dashboard"));
router.use("/profile", require("./profile"));


module.exports = router;
