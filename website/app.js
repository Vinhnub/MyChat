/* ====== CONFIG ====== */
const WS_URL = "ws://26.253.176.29:5555";

/* ====== STATE ====== */
let socket = null;
let me = null;            // { username, userFullName }
let groups = {};          // từ server: { [groupName]: { listMsg, members, lastReadMessageID } }
let currentGroup = null;  // string groupName
let unread = {};          // { [groupName]: number }

/* ====== HELPERS ====== */
const $ = (sel) => document.querySelector(sel);
const el = (tag, cls) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  return e;
};

function fmtDate(d = new Date()) {
  // server đang lưu cột "date" dạng text; gửi ISO cho chắc
  // Bạn có thể đổi sang "YYYY/MM/DD HH:mm:ss" nếu muốn:
  // const p = (n) => String(n).padStart(2, "0");
  // return `${d.getFullYear()}/${p(d.getMonth()+1)}/${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
  return new Date(d).toISOString();
}

function saveSession() {
  localStorage.setItem("chat_me", JSON.stringify(me));
}

function loadSession() {
  try {
    const raw = localStorage.getItem("chat_me");
    if (!raw) return null;
    return JSON.parse(raw);
  } catch { return null; }
}

function clearSession() {
  localStorage.removeItem("chat_me");
}

/* ====== UI BINDINGS ====== */
const authWrapper = $("#auth-wrapper");
const appRoot = $("#app");

// auth tabs
const tabSignin = $("#tab-signin");
const tabSignup = $("#tab-signup");
const formSignin = $("#form-signin");
const formSignup = $("#form-signup");
const signinMsg = $("#signin-msg");
const signupMsg = $("#signup-msg");

// signin fields
const siUser = $("#signin-username");
const siPass = $("#signin-password");

// signup fields
const suFull = $("#signup-fullname");
const suUser = $("#signup-username");
const suPass = $("#signup-password");

// app ui
const meFullname = $("#me-fullname");
const meUsername = $("#me-username");
const btnLogout = $("#btn-logout");

const groupList = $("#group-list");
const memberList = $("#member-list");

const currentGroupName = $("#current-group-name");
const messagesBox = $("#messages");

const msgForm = $("#message-form");
const msgInput = $("#message-input");

/* ====== TABS ====== */
tabSignin.addEventListener("click", () => {
  tabSignin.classList.add("active");
  tabSignup.classList.remove("active");
  formSignin.classList.add("active");
  formSignup.classList.remove("active");
  signinMsg.textContent = ""; signupMsg.textContent = "";
});

tabSignup.addEventListener("click", () => {
  tabSignup.classList.add("active");
  tabSignin.classList.remove("active");
  formSignup.classList.add("active");
  formSignin.classList.remove("active");
  signinMsg.textContent = ""; signupMsg.textContent = "";
});

/* ====== SOCKET ====== */
function connectSocket() {
  socket = new WebSocket(WS_URL);

  socket.addEventListener("open", () => {
    // Nếu đã có phiên → thử đăng nhập luôn (silent)
    const cached = loadSession();
    if (cached?.username && cached?.userFullName) {
      // không có API "resume", nên gọi signIn lại nếu biết password
      // Ở đây vì không lưu password => không auto sign-in.
      // Bạn có thể lưu password (không khuyến nghị) để tự đăng nhập lại.
      console.log("Socket connected.");
    }
  });

  socket.addEventListener("message", (ev) => {
    let data;
    try { data = JSON.parse(ev.data); } catch { return; }
    handleServerMessage(data);
  });

  socket.addEventListener("close", () => {
    console.warn("Socket closed.");
    // Có thể tự reconnect, nhưng tạm thời hiển thị thông báo
  });

  socket.addEventListener("error", (e) => {
    console.error("Socket error", e);
  });
}

function send(data) {
  if (socket?.readyState === 1) {
    socket.send(JSON.stringify(data));
  } else {
    alert("WebSocket chưa sẵn sàng.");
  }
}

/* ====== AUTH FLOW ====== */
formSignup.addEventListener("submit", (e) => {
  e.preventDefault();
  signupMsg.textContent = "";
  const payload = {
    type: "signUp",
    fullname: suFull.value.trim(),
    username: suUser.value.trim(),
    password: suPass.value
  };
  if (!payload.fullname || !payload.username || !payload.password) {
    signupMsg.textContent = "Please fill all fields.";
    return;
  }
  send(payload);
});

formSignin.addEventListener("submit", (e) => {
  e.preventDefault();
  signinMsg.textContent = "";
  const payload = {
    type: "signIn",
    username: siUser.value.trim(),
    password: siPass.value
  };
  if (!payload.username || !payload.password) {
    signinMsg.textContent = "Please fill all fields.";
    return;
  }
  send(payload);
});

btnLogout.addEventListener("click", () => {
  if (!me) return;
  send({ type: "logout", username: me.username });
});

/* ====== CHAT FLOW ====== */
msgForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const content = msgInput.value.trim();
  if (!content || !me || !currentGroup) return;

  const message = {
    mesID: null, // server sẽ gán trong DB; ở client không cần
    mesContent: content,
    date: fmtDate(),
    userName: me.username,
    groupName: currentGroup
  };

  send({ type: "sendMessage", message });
  msgInput.value = "";
});

function switchGroup(name) {
  if (!groups[name]) return;
  currentGroup = name;
  currentGroupName.textContent = name;
  unread[name] = 0;
  renderGroups();
  renderMembers(groups[name].members || []);
  renderMessages(groups[name].listMsg || []);
  scrollMessagesToEnd();
}

function scrollMessagesToEnd() {
  requestAnimationFrame(() => {
    messagesBox.scrollTop = messagesBox.scrollHeight;
  });
}

/* ====== RENDERERS ====== */
function renderMe() {
  meFullname.textContent = me.userFullName || "—";
  meUsername.textContent = `@${me.username || "—"}`;
}

function renderGroups() {
  groupList.innerHTML = "";
  Object.keys(groups).forEach((gName) => {
    const li = el("li", "group-item" + (gName === currentGroup ? " active" : ""));
    const left = el("div");
    const right = el("div", "unread");

    const title = el("div", "group-name");
    title.textContent = gName;
    left.appendChild(title);

    const count = unread[gName] || 0;
    right.textContent = count > 0 ? `${count} new` : "";

    li.appendChild(left);
    li.appendChild(right);

    li.addEventListener("click", () => switchGroup(gName));
    groupList.appendChild(li);
  });
}

function renderMembers(members) {
  memberList.innerHTML = "";
  members.forEach(([username, fullName]) => {
    const li = el("li", "member");
    li.innerHTML = `<div class="name">${fullName}</div><div class="username">@${username}</div>`;
    memberList.appendChild(li);
  });
}

function renderMessages(list) {
  messagesBox.innerHTML = "";
  list.forEach(addMessageBubble);
  scrollMessagesToEnd(); 
}

function addMessageBubble(msg) {
  // msg: { mesID, mesContent, date, userName, groupName }
  const row = el("div", "msg-row" + (msg.userName === me.username ? " me" : ""));
  const bubble = el("div", "msg" + (msg.userName === me.username ? " me" : ""));
  const who = msg.userName === me.username ? "You" : `@${msg.userName}`;

  const content = el("div");
  content.textContent = msg.mesContent;

  const meta = el("div", "meta");
  meta.textContent = `${who} • ${msg.date}`;

  bubble.appendChild(content);
  bubble.appendChild(meta);
  row.appendChild(bubble);
  messagesBox.appendChild(row);
}

/* ====== SERVER MESSAGE HANDLER ====== */
function handleServerMessage(packet) {
  const { type } = packet;

  if (type === "signUp") {
    if (packet.status) {
      signupMsg.textContent = "Sign up success. Please sign in.";
      tabSignin.click();
    } else {
      signupMsg.textContent = "Username already exists.";
    }
    return;
  }

  if (type === "signIn") {
    if (packet.status === "error") {
      signinMsg.textContent = "This user is already online.";
      return;
    }
    if (packet.status === false) {
      signinMsg.textContent = "Wrong username or password.";
      return;
    }
    if (packet.status === true && packet.data) {
      // packet.data: { username, userFullName, groups }
      me = { username: packet.data.username, userFullName: packet.data.userFullName };
      groups = packet.data.groups || {};
      unread = Object.fromEntries(Object.keys(groups).map(k => [k, 0]));

      // Show app UI
      authWrapper.classList.add("hidden");
      appRoot.classList.remove("hidden");

      // Render
      renderMe();
      renderGroups();

      // chọn group đầu tiên nếu có
      const first = Object.keys(groups)[0];
      if (first) switchGroup(first);

      // Clear form
      siPass.value = "";
      saveSession();
    }
    return;
  }

  if (type === "recvMessage") {
    const msg = packet.message;
    const g = msg.groupName;
    if (!groups[g]) return; // không thuộc nhóm mình

    // push vào bộ nhớ local
    groups[g].listMsg = groups[g].listMsg || [];
    groups[g].listMsg.push(msg);

    // Nếu đang ở group này → render & scroll
    if (currentGroup === g) {
      addMessageBubble(msg);
      scrollMessagesToEnd();
    } else {
      unread[g] = (unread[g] || 0) + 1;
      renderGroups();
    }
    return;
  }

  if (type === "logout") {
    if (packet.status) {
      // server xác nhận logout của chính mình
      clearSession();
      me = null; groups = {}; currentGroup = null; unread = {};
      appRoot.classList.add("hidden");
      authWrapper.classList.remove("hidden");
      signinMsg.textContent = "Logged out.";
    } else {
      // logout failed (không online)
      signinMsg.textContent = "Logout failed.";
    }
    return;
  }
}

/* ====== INIT ====== */
connectSocket();
