document.addEventListener("DOMContentLoaded", function() {
    const join_room = document.getElementById("join_room");
    const create_room = document.getElementById("create_room");
    const createRoomText = document.getElementById("create_room_text");
    const createRoomBtn = document.getElementById("create_room_btn");
    const joinRoomText = document.getElementById("join_room_text");
    const joinRoomInput = document.getElementById("join_room_input");
    const joinRoomBtn = document.getElementById("join_room_btn");

    joinRoomText.style.display = "none";
    joinRoomInput.style.display = "none";
    joinRoomBtn.style.display = "none";
    create_room.addEventListener("click", function() {
        createRoomText.style.display = "block";
        createRoomBtn.style.display = "block";
        joinRoomText.style.display = "none";
        joinRoomInput.style.display = "none";
        joinRoomBtn.style.display = "none";
    });

    join_room.addEventListener("click", function() {
        createRoomText.style.display = "none";
        createRoomBtn.style.display = "none";
        joinRoomText.style.display = "block";
        joinRoomInput.style.display = "block";
        joinRoomBtn.style.display = "block";
    });
});