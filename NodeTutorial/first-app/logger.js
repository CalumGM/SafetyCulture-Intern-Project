const { EventEmitter } = require('events');

var url = 'http://mylogger.io/log';

/*
The logger class inherits all of the functionality of EventEmitter.
Which means we dont need to define the emitter objects individually
*/
class Logger extends EventEmitter{
    log(message){
        // send http request
        console.log(message)

        // triggers the event defined in app.js
        this.emit('messageLogged', {id: 1, url: 'http://...'}) // useful for passing data about the event
    }
}



module.exports = Logger;  // exports the Logger class