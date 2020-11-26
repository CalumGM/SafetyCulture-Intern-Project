var express = require("express");
var path = require("path");

var app = express();

app.set("port", process.env.PORT || 3000);
app.set("views", path.join(__dirname, "views")); // views are located in the "views" folder
app.set("view engine", "ejs"); // which views engine is being used

app.use("/", require("./routes/web")); // routes are like the callbacks on each page
app.use("/", require("./routes/api"));

app.listen(app.get("port"), function(){ // connection callback
    console.log("Server started on port " + app.get("port"));
});