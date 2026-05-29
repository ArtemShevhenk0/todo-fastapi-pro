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
    const token = localStorage.getItem('my_token');

    if (!token) {
        console.log('Нужно войти в аккаунт')
        return
    }

    const response = await fetch('/tasks/',{
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`, 
            'Accept': 'application/json'
        }
    });
    const data = await response.json();
    if(response.ok) {
        displayTasks(data)
    } else if (response.status === 401){
        localStorage.removeItem('my_token');
        toggleUI();

    } else {
        alert("Ошибка:" + data.detail)
    }
    
}

function displayTasks(data) {
    const container = document.getElementById('task-list')
    container.innerHTML = ''

    data.sort((a, b) => a.id - b.id);
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

    const response = await fetch('/tasks/',{
        method: 'POST',
        body: formData,
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    const data = await response.json();
    if (response.ok) {
        titleIn.value = '';
        descriptionIn.value = '';
        prioritySe.value = '1';
        await getTask()
    } else {
        alert(data.detail)
    }
    
}

async function deleteTask(id) {
    const token = localStorage.getItem('my_token');

    const response = await fetch (`/tasks/${id}`, {
        method: 'DELETE',
        headers: {'Authorization': `Bearer ${token}`}
    });
    const data = await response.json();

    if (response.ok) {
        await getTask();
    } else {
        alert(data.detail);
    }
}

async function toggleDone(id, isDone) {
    const token = localStorage.getItem('my_token');

    const response = await fetch (`/tasks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({done: isDone}),
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });

    const data = await response.json();
    if (response.ok) {
        await getTask();
    } else {
        alert(data.detail)
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