let current_page = 1;
let total_pages = 1;

async function apiRequest(url, method, body = null ) {
    const token = localStorage.getItem('my_token');

    let headers = {
        'Authorization': `Bearer ${token}`
    };

    let finalBody = body;
    if(body && !(body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        finalBody = JSON.stringify(body);
    }

    const response = await fetch(url, {
            method: method,
            headers: headers,
            body: finalBody
        });

    return {
        ok: response.ok,
        status: response.status,
        data: await response.json()
    };
}
async function login() {
    const user = document.getElementById("user").value
    const password = document.getElementById("password").value

    const params = new URLSearchParams()
    params.append('username', user);
    params.append('password', password);

    const response = await fetch("/auth/login", {
        method: 'POST',
        body: params
    });

    const data = await response.json();

    if(response.ok) {
        localStorage.setItem('my_token', data.access_token);
        toggleUI();
        await getTask();
    } else {
        alert("Ошибка входа: " + data.detail);
    }
    
}

async function getTask() {
    const search = document.getElementById('search-input').value;

    const result = await apiRequest(`/tasks/?page=${current_page}&search=${search}`, 'GET');

    if(result.ok) {
        total_pages = result.data.pages;
        displayTasks(result.data.items)
    } else if (result.status === 401){
        localStorage.removeItem('my_token');
        toggleUI();

    } else {
        alert("Ошибка:" + result.data.detail)
    }

    const page_info = document.getElementById('page-info');
    document.getElementById('next-page').disabled = (current_page >= total_pages || total_pages === 0);
    document.getElementById('prev-page').disabled = (current_page === 1);
    if (page_info) page_info.innerText = `${current_page} of ${total_pages}`
    
}

function displayTasks(data) {
    const container = document.getElementById('task-list')
    container.innerHTML = ''

    let allHtml = '';
    data.forEach((task) => {
        const imgHtml = task.image_path 
        ? `<img  src="/static/uploads/tasks/${task.image_path}" 
            class="rounded shadow-sm border" 
            style="width: 120px; height: 80px; object-fit: cover; cursor: pointer;" 
            onclick="window.open(this.src)">` 
        : '';
        const html = `
        <div class="d-flex align-items-center justify-content-between border rounded p-2 mb-2 bg-white">
                
                <!-- Левая часть: текст в одну строку -->
                <div class="d-flex align-items-center gap-3" >
                    <b class="text-nowrap">Title: ${task.title}</b>
                    <span class="text-muted text-nowrap">Description: ${task.description || 'No description'}</span>
                    <span class="badge bg-secondary text-nowrap">Priority: ${task.priority}</span>
                    ${imgHtml}
                </div>

                <div >
                    <button class="btn btn-danger" data-id="${task.id}" data-action="delete">Delete</button>
                    <button class="btn ${task.done ? 'btn-success' : 'btn-danger'}" data-id="${task.id}" data-action ="done">✔</button>
                </div>
            </div>`;
    allHtml += html;
    });
    container.innerHTML = allHtml;
}

async function createTask() {
    const token = localStorage.getItem('my_token');

    const formData = new FormData();

    const titleIn = document.getElementById('title')
    const descriptionIn = document.getElementById('description')
    const prioritySe = document.getElementById('priority')
    const imageFile = document.getElementById('task-image')

    formData.append('title', titleIn.value);
    formData.append('description', descriptionIn.value);
    formData.append('priority', parseInt(prioritySe.value));
    if (imageFile.files[0]){
        formData.append('file', imageFile.files[0]);
    }

    const result = await apiRequest('/tasks/', 'POST', formData);
    
    if (result.ok) {
        titleIn.value = '';
        descriptionIn.value = '';
        prioritySe.value = '1';
        imageFile.value = '';
        await getTask()
    } else {
        alert(result.data.detail)
    }
    
}

async function deleteTask(id) {
    confirm('Are you sure?')
    const result = await apiRequest(`/tasks/${id}`, 'DELETE')

    if (result.ok) {
        await getTask();
    } else {
        alert(result.data.detail)
    }
}

async function toggleDone(id, isDone) {
    const token = localStorage.getItem('my_token');

    const result = await apiRequest(`/tasks/${id}`, 'PATCH', {done: isDone})
    if (result.ok) {
        await getTask();
    } else {
        alert(result.data.detail)
    }
    
}

function logout(){
    localStorage.removeItem('my_token');
    document.getElementById('task-list').innerHTML = '';
    return alert('You have logged out'), toggleUI();
    
}

function toggleUI(){
    const token = localStorage.getItem('my_token');
    const auth = document.getElementById('auth-section');
    const main = document.getElementById('main-section');

    if(!token) {
        auth.classList.remove('d-none');
        main.classList.add('d-none');
        localStorage.removeItem('my_token');
    } else {
        main.classList.remove('d-none');
        auth.classList.add('d-none');
    }

}

document.addEventListener('DOMContentLoaded', async ()=>{
    const token = localStorage.getItem('my_token');
    if (token) {
        await getTask();
    }
    toggleUI();
});

document.addEventListener('click', async (event)=>{
    const btn = event.target.closest('#add-task-btn');

    if(!btn) return;
    
    const btn_text = document.getElementById('btn-text');
    const btn_spinner = document.getElementById('btn-spinner');
    
    try{
        btn.disabled = true;
        btn_text.classList.add('d-none')
        btn_spinner.classList.remove('d-none')
        await createTask();
    } catch (error) {
        console.error("Ошибка при создании задачи:", error);
    } finally {
        btn.disabled = false;
        btn_text.classList.remove('d-none')
        btn_spinner.classList.add('d-none')
    }

});

document.getElementById('task-list').addEventListener('click', async (event) => {
    const btn = event.target.closest('[data-action]');
    if (!btn) return;
    
    const id = btn.dataset.id;
    const action = btn.dataset.action;
    
    const isDone = btn.classList.contains('btn-danger');
    
    if(action === 'delete'){

        await deleteTask(id);
    }
    if (action === 'done'){
        await toggleDone(id,isDone)
        
    }
    
    
});

document.getElementById('button-section').addEventListener('click', async (event)=> {
    const btn = event.target.id;
    if(btn === 'next-page'){
        current_page++
        console.log(current_page)
        await getTask()
    }
    if(btn === 'prev-page'){
        if (current_page > 1) current_page--
        await getTask()
    }
});

let timeout;

document.getElementById('search-input').addEventListener('input', async ()=>{
    clearTimeout(timeout)
    timeout = setTimeout(() => {current_page = 1;getTask();}, 500)
});