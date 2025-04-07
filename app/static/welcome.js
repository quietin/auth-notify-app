let socket;
let reconnectInterval = 3000;
let notificationVisible = false;
let detailsVisible = false;
let unread = false;

function connectWebSocket() {
    socket = new WebSocket(`ws://${window.location.host}/ws/notifications`);

    socket.onopen = () => {
        console.log("🔌 WebSocket connected");
    };

    socket.onmessage = (event) => {
        const msg = event.data;

        const bar = document.getElementById("notification");
        const label = document.getElementById("notification-label");
        const list = document.getElementById("notification-list");

        // 显示通知栏（初次）
        if (!notificationVisible) {
            bar.style.display = "block";
            notificationVisible = true;
        }

        // 有未读消息，变黄+修改文案
        if (!unread) {
            bar.classList.add("unread");
            label.innerText = "🔔 You have new notifications!";
            unread = true;
        }

        const li = document.createElement("li");
        li.innerText = msg;
        list.prepend(li);
    };

    socket.onclose = (event) => {
        console.warn("⚠️ WebSocket closed, retrying in 3s...", event.reason);
        setTimeout(connectWebSocket, reconnectInterval);
    };

    socket.onerror = (err) => {
        console.error("❌ WebSocket error", err);
        socket.close();
    };
}

function toggleDetails() {
    const details = document.getElementById("notification-details");
    const bar = document.getElementById("notification");
    const label = document.getElementById("notification-label");

    detailsVisible = !detailsVisible;
    details.style.display = detailsVisible ? "block" : "none";

    // 用户点击展开 → 视为已读
    if (detailsVisible && unread) {
        bar.classList.remove("unread");
        label.innerText = "📭 No unread notifications.";
        unread = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("notification").style.display = "block";
    document.getElementById("notification-label").innerText = "📭 No unread notifications.";
    connectWebSocket();
    window.toggleDetails = toggleDetails;
});





//let shown = false;
//
//function toggleDetails() {
//    shown = !shown;
//    const details = document.getElementById("notification-details");
//    details.style.display = shown ? "block" : "none";
//}
//
//// Example of populating dummy notifications
////document.addEventListener("DOMContentLoaded", () => {
////    const list = document.getElementById("notification-list");
////    list.innerHTML = `
////        <li>📩 New user registered: abc@gmail.com</li>
////        <li>📩 New user registered: hello@example.com</li>
////    `;
////});
//
//
//document.addEventListener("DOMContentLoaded", () => {
//    const socket = new WebSocket(`ws://${window.location.host}/ws/notifications`);
//    const notificationArea = document.getElementById("notification");
//
//    socket.onmessage = function (event) {
//        const msg = event.data;
//        const el = document.createElement("div");
//        el.className = "notification";
//        el.innerText = msg;
//        notificationArea.prepend(el);
//    };
//});
