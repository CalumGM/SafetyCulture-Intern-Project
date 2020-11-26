var express = require("express");
var path = require("path");
var routes = require("./routes")

var app = express();

console.log("Working");

app.set("port", process.env.PORT || 80);
app.set("views", path.join(__dirname, "views")); // views are located in the "views" folder
app.set("view engine", "ejs"); // which views engine is being used
app.use(routes)

app.listen(app.get("port"), function(){ // connection callback
    console.log("Server started on port " + app.get("port"));
});