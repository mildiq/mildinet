const apiRoot = "/api/v1";
const state = {
  accessToken: sessionStorage.getItem("accessToken"),
  refreshToken: sessionStorage.getItem("refreshToken"),
  currentUser: null,
  peer: null,
  socket: null,
};

let selectedFiles = [];
let selectedMediaIds = [];

const byId = (id) => document.getElementById(id);

function notify(message) {
  const notice = byId("notice");
  notice.textContent = message;
  notice.hidden = !message;
}

function persistTokens(tokens) {
  state.accessToken = tokens.access_token;
  state.refreshToken = tokens.refresh_token;
  sessionStorage.setItem("accessToken", state.accessToken);
  sessionStorage.setItem("refreshToken", state.refreshToken);
}

async function refreshAccess() {
  if (!state.refreshToken) return false;
  const response = await fetch(`${apiRoot}/auth/refresh`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({refresh_token: state.refreshToken}),
  });
  if (!response.ok) return false;
  persistTokens(await response.json());
  return true;
}

async function request(path, options = {}, retry = true) {
  const headers = new Headers(options.headers || {});
  if (state.accessToken) headers.set("Authorization", `Bearer ${state.accessToken}`);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(`${apiRoot}${path}`, {...options, headers});
  if (response.status === 401 && retry && await refreshAccess()) return request(path, options, false);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const fieldMessage = payload?.error?.fields?.[0]?.message;
    throw new Error(fieldMessage || payload?.error?.message || payload?.detail || "Ошибка запроса");
  }
  return response.status === 204 ? null : response.json();
}

function showAuthenticated(authenticated) {
  byId("auth").hidden = authenticated;
  byId("nav").hidden = !authenticated;
  if (authenticated) {
    showView("feed").catch((error) => notify(error.message));
  } else {
    byId("feed").hidden = true;
    byId("chat").hidden = true;
  }
}

async function showView(view) {
  byId("feed").hidden = view !== "feed";
  byId("chat").hidden = view !== "chat";

  if (view === "feed") {
    await loadMediaLibrary();
    await loadPosts();
  }

  if (view === "chat") {
    await loadUsers();
  }
}

function mediaNode(media) {
  console.log("RENDER MEDIA:", media);

  const type = media.media_type.toUpperCase();

  if (type === "IMAGE") {
    const image = document.createElement("img");

    image.src = media.url;
    image.alt = "Медиа";
    image.loading = "lazy";
    image.className = "post-image";

    image.onclick = () => {
        openLightbox(media.url, image.alt);
    };

    return image;
  }

  if (type === "VIDEO") {
    const video = document.createElement("video");

    video.src = media.url;
    video.controls = true;
    video.preload = "metadata";

    return video;
  }

  if (type === "AUDIO") {
    const audio = document.createElement("audio");

    audio.src = media.url;
    audio.controls = true;

    return audio;
  }

  if (type === "DOCUMENT") {
    const link = document.createElement("a");

    link.href = media.url;
    link.textContent = "Открыть файл";
    link.target = "_blank";
    link.rel = "noopener noreferrer";

    return link;
  }

  console.warn("UNKNOWN MEDIA TYPE:", media.media_type);

  return null;
}

function postNode(post) {

  const article = document.createElement("article");
  article.className = "card";

  const own = state.currentUser?.id === post.author_id;

  article.innerHTML = `
    <div class="post-meta"><strong></strong><time></time></div>
    <p class="post-content"></p>
    <div class="post-media"></div>
    <div class="post-actions">
      <button data-like>♥ <span></span></button>
      ${own ? "<button data-edit class='quiet'>Изменить</button><button data-delete class='quiet'>Удалить</button>" : ""}
    </div>`;

  article.querySelector("strong").textContent = post.author_name;
  article.querySelector("time").textContent =
    new Date(post.created_at).toLocaleString();

  article.querySelector(".post-content").textContent = post.content;

  const mediaContainer = article.querySelector(".post-media");

  for (const media of post.media) {
    mediaContainer.appendChild(mediaNode(media));
  }

  if (post.media.length === 0) {
    mediaContainer.remove();
  }
  article.querySelector("[data-like] span").textContent = post.likes_count;
  article.querySelector("[data-like]").onclick = async () => {
    try {
      const result = await request(`/posts/${post.id}/likes/toggle`, {method: "POST"});
      article.querySelector("[data-like] span").textContent = result.likes_count;
      notify("");
    } catch (error) { notify(error.message); }
  };
  const edit = article.querySelector("[data-edit]");
  if (edit) edit.onclick = async () => {
    const content = prompt("Новый текст", post.content);
    if (!content) return;
    try {
      await request(`/posts/${post.id}`, {method: "PUT", body: JSON.stringify({content})});
      await loadPosts();
      notify("");
    } catch (error) { notify(error.message); }
  };
  const remove = article.querySelector("[data-delete]");
  if (remove) remove.onclick = async () => {
    try {
      await request(`/posts/${post.id}`, {method: "DELETE"});
      await loadPosts();
      notify("");
    } catch (error) { notify(error.message); }
  };
  return article;
}

async function loadPosts(query = "") {
  const data = await request(`/posts${query ? `?q=${encodeURIComponent(query)}` : ""}`);
  byId("posts").replaceChildren(...data.items.map(postNode));
}

async function loadUsers() {
  const users = await request("/users");
  byId("users").replaceChildren(...users.map((user) => {
    const button = document.createElement("button");
    button.textContent = user.name;
    button.onclick = () => selectPeer(user);
    return button;
  }));
}

function messageNode(message) {
  const node = document.createElement("div");
  node.className = `message${message.sender_id === state.currentUser.id ? " mine" : ""}`;
  node.textContent = message.content;
  return node;
}

async function selectPeer(peer) {
  state.peer = peer;
  byId("peer-name").textContent = peer.name;
  byId("message-form").hidden = false;
  const data = await request(`/messages/${peer.id}`);
  byId("messages").replaceChildren(...data.items.map(messageNode));
}

function connectMessages() {
  state.socket?.close();
  const scheme = location.protocol === "https:" ? "wss" : "ws";
  state.socket = new WebSocket(`${scheme}://${location.host}${apiRoot}/ws/messages`);
  state.socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type !== "message.created" || !state.peer) return;
    const data = message.data;
    if ([data.sender_id, data.recipient_id].includes(state.peer.id)) {
      byId("messages").append(messageNode(data));
    }
  };
}

async function uploadMedia(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/media", {
    method: "POST",
    body: formData,
  });
}

async function loadMediaLibrary() {
  const media = await request("/media");

  mediaLibrary.innerHTML = "";

  media
    .filter((item) => item.media_type === "image")
    .forEach((item) => {
      const wrapper = document.createElement("div");
      wrapper.className = "media-library-item";

      const image = document.createElement("img");
      image.src = `${apiRoot}/media/${item.id}`;
      image.alt = item.original_filename;
      image.loading = "lazy";
      image.dataset.mediaId = item.id;

      image.onclick = () => {
        if (selectedMediaIds.includes(item.id)) {
          selectedMediaIds = selectedMediaIds.filter(
            (id) => id !== item.id
          );
        } else {
          selectedMediaIds.push(item.id);
        }

        renderMediaLibrary();
      };

      wrapper.append(image);
      mediaLibrary.append(wrapper);
    });
}

function renderMediaLibrary() {
  mediaLibrary
    .querySelectorAll(".media-library-item")
    .forEach((wrapper) => {
      const image = wrapper.querySelector("img");
      const mediaId = Number(image.dataset.mediaId);

    wrapper.classList.toggle(
      "selected",
      selectedMediaIds.includes(mediaId)
    );
  });
}

function clearSelectedMedia() {
  selectedFiles = [];
  selectedMediaIds = [];

  postMediaInput.value = "";
  mediaPreview.innerHTML = "";

  renderMediaLibrary();
}

byId("login-form").onsubmit = async (event) => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const body = new URLSearchParams({username: data.get("email"), password: data.get("password")});
  try {
    const response = await fetch(`${apiRoot}/auth/login`, {method: "POST", body});
    if (!response.ok) throw new Error("Неверный email или пароль");
    const login = await response.json();
    persistTokens(login);
    state.currentUser = login.user;
    notify("");
    showAuthenticated(true);
    connectMessages();
  } catch (error) { notify(error.message); }
};

byId("register-form").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const values = Object.fromEntries(new FormData(form));
  try {
    await request("/auth/register", {method: "POST", body: JSON.stringify(values)});
    notify("Аккаунт создан — теперь войдите");
    form.reset();
  } catch (error) { notify(error.message); }
};

const postMediaInput = byId("post-media");
const mediaPreview = byId("media-preview");
const mediaLibrary = byId("media-library");
const toggleMediaLibrary = byId("toggle-media-library");

const lightbox = byId("lightbox");
const lightboxImage = byId("lightbox-image");
const lightboxClose = byId("lightbox-close")

toggleMediaLibrary.onclick = () => {
 mediaLibrary.hidden = !mediaLibrary.hidden;

 if (mediaLibrary.hidden) {
    toggleMediaLibrary.textContent = "Выбрать из моих фото";
   } else {
    toggleMediaLibrary.textContent = "Скрыть мои фото";
 }
};

postMediaInput.onchange = () => {
  selectedFiles.push(...postMediaInput.files);

  renderMediaPreview();

  // Позволяем снова выбрать те же файлы
  postMediaInput.value = "";
};

function renderMediaPreview() {
  mediaPreview.innerHTML = "";

  selectedFiles.forEach((file, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "media-preview-item";

    const image = document.createElement("img");
    image.src = URL.createObjectURL(file);
    image.alt = file.name;

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "×";

    removeButton.onclick = () => {
      selectedFiles.splice(index, 1);
      renderMediaPreview();
    };

    wrapper.append(image, removeButton);
    mediaPreview.append(wrapper);
  });
}

function openLightbox(url, alt = "Изображение") {
    lightboxImage.src = url;
    lightboxImage.alt = alt;
    lightbox.hidden = false;
}

function closeLightbox() {
    lightbox.hidden = true;
    lightboxImage.src = "";
}

lightboxClose.onclick = closeLightbox;

lightbox.onclick = (event) => {
    if (event.target === lightbox) {
        closeLightbox();
    }
};

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !lightbox.hidden) {
        closeLightbox();
    }
});

byId("post-form").onsubmit = async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const content = new FormData(form).get("content")?.trim() || "";
  const files = selectedFiles;

  try {
    const mediaIds = [...selectedMediaIds];

    for (const file of files) {
      const media = await uploadMedia(file);
      mediaIds.push(media.id);
    }

    await request("/posts", {
      method: "POST",
      body: JSON.stringify({
        content,
        media_ids: mediaIds,
      }),
    });

    clearSelectedMedia();
    form.reset();

    await loadPosts();
    notify("");
  } catch (error) {
    notify(error.message);
  }
};

byId("search-form").onsubmit = async (event) => {
  event.preventDefault();
  try {
    await loadPosts(new FormData(event.currentTarget).get("q"));
    notify("");
  } catch (error) { notify(error.message); }
};

byId("message-form").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const content = new FormData(form).get("content");
  try {
    await request("/messages", {method: "POST", body: JSON.stringify({recipient_id: state.peer.id, content})});
    form.reset();
    notify("");
  } catch (error) { notify(error.message); }
};

byId("logout").onclick = async () => {
  if (state.refreshToken) await request("/auth/logout", {method: "POST", body: JSON.stringify({refresh_token: state.refreshToken})}).catch(() => null);
  sessionStorage.clear();
  state.socket?.close();
  state.accessToken = state.refreshToken = state.currentUser = null;
  showAuthenticated(false);
};

document.querySelectorAll("[data-view]").forEach((button) => {
  button.onclick = () => showView(button.dataset.view).catch((error) => notify(error.message));
});

if (state.accessToken) {
  request("/users/me").then((user) => {
    state.currentUser = user;
    showAuthenticated(true);
    connectMessages();
  }).catch(() => showAuthenticated(false));
}
