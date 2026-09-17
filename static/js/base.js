const api = async (url, options = {}) => {
    const response = await fetch(url, { ...options, headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...(options.headers || {}) } });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
};

const escapeHtml = (value) => String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
const setMessage = (id, message = "") => { const element = document.getElementById(id); if (element) element.textContent = message; };
const saveToken = (token) => { document.cookie = `access_token=${encodeURIComponent(token)}; Path=/; Max-Age=3600; SameSite=Lax`; };
const clearToken = () => { document.cookie = "access_token=; Path=/; Max-Age=0; SameSite=Lax"; };
const showToast = (message, type = "success") => { const toast = document.getElementById("toast"); if (!toast) return; toast.textContent = message; toast.className = `toast is-visible ${type}`; window.clearTimeout(showToast.timer); showToast.timer = window.setTimeout(() => { toast.className = "toast"; }, 3200); };

const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = loginForm.querySelector("button[type=submit]");
        button.disabled = true;
        setMessage("loginMessage");
        try {
            const response = await fetch("/auth/token", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams(new FormData(loginForm)) });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.detail || "Incorrect username or password");
            saveToken(data.access_token);
            window.location.assign("/todos/todo-page");
        } catch (error) { setMessage("loginMessage", error.message); button.disabled = false; }
    });
}

const registerForm = document.getElementById("registerForm");
if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const values = Object.fromEntries(new FormData(registerForm));
        const confirmation = values.password2;
        delete values.password2;
        if (values.password !== confirmation) { setMessage("registerMessage", "Passwords do not match."); return; }
        const button = registerForm.querySelector("button[type=submit]");
        button.disabled = true;
        try { await api("/auth/", { method: "POST", body: JSON.stringify({ ...values, role: "member", phone_number: "" }) }); window.location.assign("/auth/login-page?created=1"); }
        catch (error) { setMessage("registerMessage", error.message); button.disabled = false; }
    });
}

const logoutButton = document.getElementById("logoutButton");
if (logoutButton) logoutButton.addEventListener("click", () => { clearToken(); window.location.assign("/auth/login-page"); });

const todoForm = document.getElementById("todoForm");
if (todoForm) {
    const list = document.getElementById("todoList");
    let todos = [];
    let filter = "all";
    let editingTodo = null;
    let deletingTodo = null;
    const editDialog = document.getElementById("editDialog");
    const confirmDialog = document.getElementById("confirmDialog");

    const closeDialogs = () => { editDialog.hidden = true; confirmDialog.hidden = true; editingTodo = null; deletingTodo = null; };
    document.querySelectorAll("[data-close-dialog]").forEach((button) => button.addEventListener("click", closeDialogs));
    document.querySelectorAll(".dialog-backdrop").forEach((dialog) => dialog.addEventListener("click", (event) => { if (event.target === dialog) closeDialogs(); }));
    document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeDialogs(); });

    const render = () => {
        const query = document.getElementById("searchInput").value.trim().toLowerCase();
        const visible = todos.filter((todo) => {
            const statusMatch = filter === "all" || (filter === "done" ? todo.complete : !todo.complete);
            return statusMatch && `${todo.title} ${todo.description}`.toLowerCase().includes(query);
        });
        list.innerHTML = visible.map((todo) => `<article class="todo-item ${todo.complete ? "is-done" : ""}" data-id="${todo.id}"><input class="todo-check" type="checkbox" ${todo.complete ? "checked" : ""} aria-label="Mark ${escapeHtml(todo.title)} complete"><div class="todo-copy"><div class="todo-title">${escapeHtml(todo.title)}</div><div class="todo-description">${escapeHtml(todo.description)}</div></div><div class="todo-actions"><button class="text-button edit-todo" type="button">Edit</button><button class="text-button delete-todo" type="button">Delete</button></div></article>`).join("");
        document.getElementById("allCount").textContent = todos.length;
        document.getElementById("openCount").textContent = todos.filter((todo) => !todo.complete).length;
        document.getElementById("doneCount").textContent = todos.filter((todo) => todo.complete).length;
        const done = todos.filter((todo) => todo.complete).length;
        document.getElementById("progressValue").textContent = `${todos.length ? Math.round(done / todos.length * 100) : 0}%`;
        document.getElementById("emptyState").hidden = visible.length > 0;
    };

    const load = async () => {
        try { const user = await api("/auth/me"); document.getElementById("userGreeting").textContent = `Hi, ${user.first_name}`; todos = await api("/todos"); render(); }
        catch { clearToken(); window.location.assign("/auth/login-page"); }
    };

    todoForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const values = Object.fromEntries(new FormData(todoForm));
        const title = values.title.trim();
        const description = values.description.trim();
        if (title.length < 3) { showToast("Task title must be at least 3 characters.", "error"); return; }
        if (description.length < 3) { showToast("Add a little more detail to the task.", "error"); return; }
        const button = todoForm.querySelector("button[type=submit]"); button.disabled = true;
        try { todos.unshift(await api("/todos", { method: "POST", body: JSON.stringify({ title, description, complete: false }) })); todoForm.reset(); render(); showToast("Task added"); }
        catch (error) { showToast(error.message, "error"); }
        finally { button.disabled = false; }
    });

    list.addEventListener("change", async (event) => {
        if (!event.target.classList.contains("todo-check")) return;
        const todo = todos.find((item) => item.id === Number(event.target.closest(".todo-item").dataset.id));
        try { const updated = await api(`/todos/${todo.id}`, { method: "PUT", body: JSON.stringify({ title: todo.title, description: todo.description, complete: event.target.checked }) }); todos = todos.map((item) => item.id === updated.id ? updated : item); render(); showToast(updated.complete ? "Task completed" : "Task reopened"); }
        catch (error) { event.target.checked = !event.target.checked; showToast(error.message, "error"); }
    });

    list.addEventListener("click", (event) => {
        const item = event.target.closest(".todo-item");
        if (!item) return;
        const todo = todos.find((entry) => entry.id === Number(item.dataset.id));
        if (event.target.classList.contains("edit-todo")) { editingTodo = todo; document.getElementById("editTitle").value = todo.title; document.getElementById("editDescription").value = todo.description; setMessage("editMessage"); editDialog.hidden = false; document.getElementById("editTitle").focus(); }
        if (event.target.classList.contains("delete-todo")) { deletingTodo = todo; confirmDialog.hidden = false; document.getElementById("confirmDelete").focus(); }
    });

    document.getElementById("editForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        const title = document.getElementById("editTitle").value.trim();
        const description = document.getElementById("editDescription").value.trim();
        if (title.length < 3) { setMessage("editMessage", "Task title must be at least 3 characters."); return; }
        if (description.length < 3) { setMessage("editMessage", "Details must be at least 3 characters."); return; }
        const button = event.target.querySelector("button[type=submit]"); button.disabled = true;
        try { const updated = await api(`/todos/${editingTodo.id}`, { method: "PUT", body: JSON.stringify({ title, description, complete: editingTodo.complete }) }); todos = todos.map((todo) => todo.id === updated.id ? updated : todo); closeDialogs(); render(); showToast("Task updated"); }
        catch (error) { setMessage("editMessage", error.message); }
        finally { button.disabled = false; }
    });

    document.getElementById("confirmDelete").addEventListener("click", async () => {
        const button = document.getElementById("confirmDelete"); button.disabled = true;
        try { await api(`/todos/${deletingTodo.id}`, { method: "DELETE" }); todos = todos.filter((todo) => todo.id !== deletingTodo.id); closeDialogs(); render(); showToast("Task deleted"); }
        catch (error) { showToast(error.message, "error"); }
        finally { button.disabled = false; }
    });

    document.querySelectorAll(".filter-tab").forEach((button) => button.addEventListener("click", () => { document.querySelectorAll(".filter-tab").forEach((item) => item.classList.remove("is-active")); button.classList.add("is-active"); filter = button.dataset.filter; render(); }));
    document.getElementById("searchInput").addEventListener("input", render);
    load();
}
