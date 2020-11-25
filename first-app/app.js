const Logger = require('./logger'); //imports the exported objects from logger
//var HTTP = require('htttp');
const { emit } = require('process');

function pathModule(){  // working with filepaths
    const path = require('path');

    var pathObj = path.parse(__filename);

    console.log(pathObj)
}

function osModule(){ // gather information about the machine
    const os = require('os')
    var totalMem = os.totalmem();
    var freeMem = os.freemem();

    console.log(`Total Memory: ${totalMem}`) // string formatting
    console.log(`Free Memory:  ${freeMem}`)
}

function fileSystemModule(){
    const fs = require('fs');
    // not recommended to use Synchronous methods, as they are less efficient
    const files= fs.readdirSync('./') // all of the files in the current folder
    console.log(files)

    // Asynchronous methods take a second argument that is a function
    const asyncFiles = fs.readdir('./', function(err, files){
        if (err) console.log('Error', err); // displays error if no file or dir is found
        else console.log('Results', files)  
    })
}

function eventsModule(){ 
    /*
        previously, there were events emitted here for example purposes, but its more 
        appropriate to put these in a seperate file, i.e. logger.js
        We have already handled importing the exports of logger.js on line 1
    */
    const logger = new Logger(); // makes an instance of the custom class that extends EventEmitter

     // Register a listener
     logger.on('messageLogged', function(arg){
        console.log('Listener called', arg) // when we raise an event, this callback is triggered
    })

    logger.log('message'); 
}

function httpModule(){
    var http = require('http');
    var portNumber = 80;
    const server = http.createServer(function(req, res){
        if (req.url === '/'){ // base url
            res.write('Hello World');
            res.end();
        }
    }); // this server has all the capabilities of EventEmitter and more
    
    /*
    // callback on connection
    server.on('connection', function(socket){
        console.log('new connection');
    })
    */

    server.listen(portNumber); // listen on port 3000
    console.log('Listening on port ', portNumber)
}

httpModule();