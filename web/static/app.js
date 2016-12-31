(function() {
    var ws = new WebSocket('ws://localhost:8888/ws');
    ws.onopen = function() {
        console.log('ws opened');
    };
    ws.onmessage = function(evt) {
        console.log(JSON.parse(evt.data));
    };
    ws.onclose = function() {
        console.log('ws closed');
    }
    window.ws = ws;

})();
