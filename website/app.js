let ws;
let username;

function connect() {
  ws = new WebSocket("ws://26.253.176.29:5555");

  ws.onopen = () => console.log("Đã kết nối server.");
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Server:", data);

    if (data.type === "signUp") {
      document.getElementById("register-status").innerText =
        data.status ? "Đăng ký thành công!" : "Tên đăng nhập đã tồn tại!";
    }

    if (data.type === "signIn") {
      if (data.status === true) {
        showChat();
        loadMessages(data.data);
      } else if (data.status === "error") {
        document.getElementById("login-status").innerText =
          "Tài khoản đã đăng nhập ở nơi khác!";
      } else {
        document.getElementById("login-status").innerText =
          "Sai mật khẩu hoặc user không tồn tại!";
      }
    }
  };

  ws.onclose = () => {
    console.log("Mất kết nối server.");
    alert("Mất kết nối server!");
  };
}

function signUp() {
  const fullname = document.getElementById("reg-fullname").value;
  const username = document.getElementById("reg-username").value;
  const password = document.getElementById("reg-password").value;
  ws.send(JSON.stringify({ type: "signUp", fullname, username, password }));
}

function signIn() {
  username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  ws.send(JSON.stringify({ type: "signIn", username, password }));
}

function loadMessages(userData) {
  const messagesDiv = document.getElementById("messages");
  messagesDiv.innerHTML = "";
  for (const groupName in userData.groups) {
    const group = userData.groups[groupName];
    messagesDiv.innerHTML += `<b>Nhóm: ${groupName}</b><br>`;
    group.lastMessages.forEach(m => {
      messagesDiv.innerHTML += `<p><b>${m.userName}:</b> ${m.mesContent} <i>(${m.date})</i></p>`;
    });
  }
}

function sendMessage() {
  const msg = document.getElementById("msgInput").value;
  if (!msg) return;
  const messagesDiv = document.getElementById("messages");
  messagesDiv.innerHTML += `<p><b>${username}:</b> ${msg}</p>`;
  document.getElementById("msgInput").value = "";
}

/* ---- Điều khiển giao diện ---- */
function showLogin() {
  hideAll();
  document.getElementById("loginForm").style.display = "block";
}

function showRegister() {
  hideAll();
  document.getElementById("registerForm").style.display = "block";
}

function showChat() {
  hideAll();
  document.getElementById("chat").style.display = "block";
}

function hideAll() {
  document.getElementById("welcome").style.display = "none";
  document.getElementById("loginForm").style.display = "none";
  document.getElementById("registerForm").style.display = "none";
  document.getElementById("chat").style.display = "none";
}

connect();
