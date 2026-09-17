const api = async (url, options = {}) => {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...(options.headers || {})
        }
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
};

const setMessage = (id, message) => {
    const element = document.getElementById(id);
    if (element) element.textContent = message || "";
};

const saveToken = (token) => {
    document.cookie = `access_token=${encodeURIComponent(token)}; Path=/; Max-Age=3600; SameSite=Lax`;
};

const clearToken = () => {
    document.cookie = "access_token=; Path=/; Max-Age=0; SameSite=Lax";
};

const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const button = loginForm.querySelector("button[type=submit]");
        button.disabled = true;
        setMessage("loginMessage", "");
        try {
            const response = await fetch("/auth/token", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams(new FormData(loginForm))
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.detail || "Incorrect username or password");
            saveToken(data.access_token);
            window.location.assign("/todos/todo-page");
        } catch (error) {
            setMessage("loginMessage", error.message);
            button.disabled = false;
        }
    });
}

const registerForm = document.getElementById("registerForm");
if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const values = Object.fromEntries(new FormData(registerForm));
        const confirmation = values.password2;
        delete values.password2;
        if (values.password !== confirmation) {
            setMessage("registerMessage", "Passwords do not match.");
            return;
        }
        const button = registerForm.querySelector("button[type=submit]");
        button.disabled = true;
        setMessage("registerMessage", "");
        try {
            await api("/auth/", {
                method: "POST",
                body: JSON.stringify({ ...values, role: "member", phone_number: "" })
            });
            window.location.assign("/auth/login-page");
        } catch (error) {
            setMessage("registerMessage", error.message);
            button.disabled = false;
        }
    });
}

const logoutButton = document.getElementById("logoutButton");
if (logoutButton) {
    logoutButton.addEventListener("click", () => {
        clearToken();
        window.location.assign("/auth/login-page");
    });
}

const todoForm = document.getElementById("todoForm");
if (todoForm) {
    const list = document.getElementById("todoList");
    let todos = [];
    let filter = "all";

    const render = () => {
        const visible = todos.filter((todo) => filter === "all" || (filter === "done" ? todo.complete : !todo.complete));
        list.innerHTML = visible.map((todo) => `<article class="todo-item ${todo.complete ? "is-done" : ""}" data-id="${todo.id}"><input class="todo-check" type="checkbox" ${todo.complete ? "checked" : ""}><div class="todo-copy"><div class="todo-title">${todo.title}</div><div class="todo-description">${todo.description}</div></div><div class="todo-actions"><button class="text-button delete-todo" type="button">Delete</button></div></article>`).join("");
        document.getElementById("allCount").textContent = todos.length;
        document.getElementById("openCount").textContent = todos.filter((todo) => !todo.complete).length;
        document.getElementById("doneCount").textContent = todos.filter((todo) => todo.complete).length;
        document.getElementById("progressValue").textContent = `${todos.length ? Math.round(todos.filter((todo) => todo.complete).length / todos.length * 100) : 0}%`;
        document.getElementById("emptyState").hidden = visible.length > 0;
    };

    const load = async () => {
        try {
            const user = await api("/auth/me");
            document.getElementById("userGreeting").textContent = `Hi, ${user.first_name}`;
            todos = await api("/todos");
            render();
        } catch {
            clearToken();
            window.location.assign("/auth/login-page");
        }
    };

    todoForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const values = Object.fromEntries(new FormData(todoForm));
        try {
            todos.unshift(await api("/todos", { method: "POST", body: JSON.stringify({ ...values, complete: false }) }));
            todoForm.reset();
            render();
        } catch (error) { window.alert(error.message); }
    });

    list.addEventListener("change", async (event) => {
        if (!event.target.classList.contains("todo-check")) return;
        const todo = todos.find((item) => item.id === Number(event.target.closest(".todo-item").dataset.id));
        try {
            const updated = await api(`/todos/${todo.id}`, { method: "PUT", body: JSON.stringify({ title: todo.title, description: todo.description, complete: event.target.checked }) });
            todos = todos.map((item) => item.id === updated.id ? updated : item);
            render();
        } catch (error) { window.alert(error.message); }
    });

    list.addEventListener("click", async (event) => {
        if (!event.target.classList.contains("delete-todo")) return;
        const id = Number(event.target.closest(".todo-item").dataset.id);
        try { await api(`/todos/${id}`, { method: "DELETE" }); todos = todos.filter((todo) => todo.id !== id); render(); }
        catch (error) { window.alert(error.message); }
    });

    document.querySelectorAll(".filter-tab").forEach((button) => button.addEventListener("click", () => {
        document.querySelectorAll(".filter-tab").forEach((item) => item.classList.remove("is-active"));
        button.classList.add("is-active");
        filter = button.dataset.filter;
        render();
    }));
    load();
}
