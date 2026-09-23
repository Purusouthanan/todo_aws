// DOM Elements
const todoForm = document.getElementById('todoForm');
const todoInput = document.getElementById('todoInput');
const todoTime = document.getElementById('todoTime');
const todoList = document.getElementById('todoList');
const emptyState = document.getElementById('emptyState');
const filterBtns = document.querySelectorAll('.filter-btn');
const progressCircle = document.querySelector('.progress-ring__circle');
const progressText = document.getElementById('progressText');

// State
let tasks = JSON.parse(localStorage.getItem('todo_tasks')) || [];
let currentFilter = 'all';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set up progress circle circumference
    const radius = progressCircle.r.baseVal.value;
    const circumference = radius * 2 * Math.PI;
    progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
    progressCircle.style.strokeDashoffset = circumference;

    renderTasks();
});

// Event Listeners
todoForm.addEventListener('submit', addTask);
todoList.addEventListener('click', handleTaskAction);
todoList.addEventListener('keypress', handleEditKeypress);
filterBtns.forEach(btn => btn.addEventListener('click', handleFilterChange));

// Functions

function saveTasks() {
    localStorage.setItem('todo_tasks', JSON.stringify(tasks));
    updateProgress();
}

function addTask(e) {
    e.preventDefault();
    const text = todoInput.value.trim();
    const timeValue = todoTime.value;
    
    if (text) {
        const newTask = {
            id: Date.now().toString(),
            text: text,
            time: timeValue,
            completed: false
        };
        
        tasks.push(newTask);
        saveTasks();
        todoInput.value = '';
        todoTime.value = '';
        renderTasks();
    }
}

function handleTaskAction(e) {
    const item = e.target.closest('.task-item');
    if (!item) return;
    
    const id = item.dataset.id;
    
    // Toggle Complete
    if (e.target.closest('.checkbox-wrapper')) {
        toggleTask(id);
    }
    
    // Delete
    if (e.target.closest('.delete-btn')) {
        deleteTask(id, item);
    }
    
    // Edit (Enter edit mode)
    if (e.target.closest('.edit-btn')) {
        enterEditMode(item);
    }
}

function toggleTask(id) {
    tasks = tasks.map(task => 
        task.id === id ? { ...task, completed: !task.completed } : task
    );
    saveTasks();
    renderTasks();
}

function deleteTask(id, element) {
    // Add deleting animation class
    element.classList.add('deleting');
    
    // Wait for animation to finish before actually removing
    setTimeout(() => {
        tasks = tasks.filter(task => task.id !== id);
        saveTasks();
        renderTasks();
    }, 300);
}

function enterEditMode(element) {
    element.classList.add('editing');
    const input = element.querySelector('.task-input-edit');
    input.focus();
    
    // Move cursor to end of text
    const val = input.value;
    input.value = '';
    input.value = val;
    
    // Handle blur (save on click outside)
    input.addEventListener('blur', function onBlur() {
        saveEdit(element.dataset.id, this.value);
        input.removeEventListener('blur', onBlur);
    }, { once: true });
}

function handleEditKeypress(e) {
    if (e.target.classList.contains('task-input-edit') && e.key === 'Enter') {
        e.preventDefault();
        e.target.blur(); // This will trigger the blur event listener above
    }
}

function saveEdit(id, newText) {
    const text = newText.trim();
    if (text) {
        tasks = tasks.map(task => 
            task.id === id ? { ...task, text: text } : task
        );
        saveTasks();
    } else {
        // If empty, delete the task
        tasks = tasks.filter(task => task.id !== id);
        saveTasks();
    }
    renderTasks();
}

function handleFilterChange(e) {
    filterBtns.forEach(btn => btn.classList.remove('active'));
    e.target.classList.add('active');
    currentFilter = e.target.dataset.filter;
    renderTasks();
}

function renderTasks() {
    // Filter tasks
    let filteredTasks = tasks;
    if (currentFilter === 'active') {
        filteredTasks = tasks.filter(task => !task.completed);
    } else if (currentFilter === 'completed') {
        filteredTasks = tasks.filter(task => task.completed);
    }

    // Render HTML
    todoList.innerHTML = '';
    
    if (filteredTasks.length === 0) {
        emptyState.classList.add('active');
    } else {
        emptyState.classList.remove('active');
        
        filteredTasks.forEach(task => {
            const li = document.createElement('li');
            li.className = `task-item ${task.completed ? 'completed' : ''}`;
            li.dataset.id = task.id;
            
            let timeHtml = '';
            if (task.time) {
                const dateObj = new Date(task.time);
                const isOverdue = !task.completed && dateObj < new Date();
                const formattedTime = dateObj.toLocaleString('en-US', { 
                    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
                });
                timeHtml = `<span class="task-time ${isOverdue ? 'overdue' : ''}">
                    <i class="ph ph-clock"></i> ${escapeHTML(formattedTime)}
                </span>`;
            }
            
            li.innerHTML = `
                <label class="checkbox-wrapper">
                    <input type="checkbox" ${task.completed ? 'checked' : ''}>
                    <div class="custom-checkbox">
                        <i class="ph ph-check"></i>
                    </div>
                </label>
                <div class="task-content">
                    <span class="task-text">${escapeHTML(task.text)}</span>
                    ${timeHtml}
                    <input type="text" class="task-input-edit" value="${escapeHTML(task.text)}">
                </div>
                <div class="task-actions">
                    <button class="action-btn edit-btn" title="Edit">
                        <i class="ph ph-pencil-simple"></i>
                    </button>
                    <button class="action-btn delete-btn" title="Delete">
                        <i class="ph ph-trash"></i>
                    </button>
                </div>
            `;
            todoList.appendChild(li);
        });
    }
    
    updateProgress();
}

function updateProgress() {
    if (tasks.length === 0) {
        setProgress(0);
        return;
    }
    
    const completedTasks = tasks.filter(task => task.completed).length;
    const percentage = Math.round((completedTasks / tasks.length) * 100);
    setProgress(percentage);
}

function setProgress(percent) {
    const radius = progressCircle.r.baseVal.value;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (percent / 100) * circumference;
    
    progressCircle.style.strokeDashoffset = offset;
    progressText.textContent = `${percent}%`;
    
    // Change color based on completion
    if (percent === 100) {
        progressCircle.style.stroke = 'var(--success)';
    } else {
        progressCircle.style.stroke = 'var(--accent-primary)';
    }
}

// Utility to prevent XSS
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
