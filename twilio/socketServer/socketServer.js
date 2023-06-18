const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', ws => {
  console.log('Client connected');
  ws.on('message', message => {
    console.log(`Received: ${message}`);
    ws.send(`Hello, you sent -> ${message}`);
  });

  ws.send('Hello! Message from server!!');
});
