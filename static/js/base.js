const express = require('express');
const app = express();
const httpServer = require('https').createServer(app);
const io = require('socket.io')(httpServer);

// Настройка CORS для socket.io
io.origins('*:*');  // Разрешить доступ со всех доменов

// Другие настройки и маршруты вашего сервера

httpServer.listen(process.env.PORT || 3000, () => {
    console.log('Server is running');
});
