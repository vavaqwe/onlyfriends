const socket = io.connect();
const player = new Plyr('#player');

const ayButton = document.getElementById('play-button');

const chatInput = document.getElementById('chat-input');
const chatSendButton = document.getElementById('chat-send');
const chatMessages = document.getElementById('chat-messages');

chatInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    var message = chatInput.value;
    if (message.trim() !== '') {
        socket.emit('message', { data: message });
        chatInput.value = '';
    }
}
chatSendButton.addEventListener('click', function() {
    var message = chatInput.value;
    if (message.trim() !== '') {
        socket.emit('message', { data: message });
        chatInput.value = '';
    }
});

let previousTime = -1;

// Обработчик окончания перемотки (когда пользователь отпускает ползунок)
player.on('seeked', function() {
  // Получаем текущее время после перемотки
  const currentTime = player.currentTime;

  // Сравниваем с предыдущим временем
  if (Math.abs(currentTime - previousTime) >= 5) { // Здесь используется порог в 1 секунду
    // Время изменилось существенно, отправляем его на сервер
    sendCurrentTime(currentTime);
  }

  // Обновляем предыдущее время
  previousTime = currentTime;
});

// Отправка текущего времени на сервер через Socket.io
function sendCurrentTime(currentTime) {
  // Здесь вы можете использовать Socket.io для отправки currentTime на сервер
  // Пример:
  socket.emit('current_time', currentTime);
}

// Обработчик события изменения времени от сервера
socket.on('current_time', function(currentTime) {
  // Получено новое время от сервера, устанавливаем его в плеер
  setVideoTime(currentTime);
});

// Установка времени видео в плеере
function setVideoTime(newTime) {
    player.currentTime = newTime;
    player.play(); // Воспроизводить видео только если оно не на паузе
}


socket.on('message', function(data) {
    var messageElement = document.createElement('div');
    messageElement.classList.add('chat-message');
    messageElement.textContent = data.name + ': ' + data.message;
    chatMessages.appendChild(messageElement);
});

ayButton.addEventListener('click', function() {
    player.play();
    ayButton.style.display = 'none'; // Скрыть кнопку после нажатия
    socket.emit('play_video');
});

socket.on("play_video", function () {
    player.play();
});

socket.on("pause_video", function () {
    player.pause();
});

player.on("play", function () {
    socket.emit("play_video");
});


player.on("pause", function () {
    socket.emit("pause_video");
});