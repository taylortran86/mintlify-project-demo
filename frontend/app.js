// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// State
let currentTaskFilter = 'all';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadEvents();
});

// Modal Functions
function showTaskModal() {
    document.getElementById('taskModal').classList.add('active');
}

function closeTaskModal() {
    document.getElementById('taskModal').classList.remove('active');
    document.getElementById('taskForm').reset();
}

function showEventModal() {
    document.getElementById('eventModal').classList.add('active');
}

function closeEventModal() {
    document.getElementById('eventModal').classList.remove('active');
    document.getElementById('eventForm').reset();
}

// Close modal when clicking outside
window.onclick = (event) => {
    const taskModal = document.getElementById('taskModal');
    const eventModal = document.getElementById('eventModal');
    if (event.target === taskModal) {
        closeTaskModal();
    }
    if (event.target === eventModal) {
        closeEventModal();
    }
};

// Task Functions
async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks`);
        const tasks = await response.json();
        displayTasks(tasks);
        displayTaskStats(tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
        showError('Failed to load tasks');
    }
}

function displayTasks(tasks) {
    const tasksList = document.getElementById('tasksList');

    // Filter tasks based on current filter
    let filteredTasks = tasks;
    if (currentTaskFilter === 'active') {
        filteredTasks = tasks.filter(task => !task.completed);
    } else if (currentTaskFilter === 'completed') {
        filteredTasks = tasks.filter(task => task.completed);
    }

    if (filteredTasks.length === 0) {
        tasksList.innerHTML = '<p class="empty-state">No tasks found.</p>';
        return;
    }

    tasksList.innerHTML = filteredTasks.map(task => `
        <div class="item-card ${task.completed ? 'completed' : ''}">
            <div class="item-header">
                <div>
                    <div class="checkbox-container">
                        <input
                            type="checkbox"
                            ${task.completed ? 'checked' : ''}
                            onchange="toggleTaskComplete(${task.id}, ${!task.completed})"
                        >
                        <div class="item-title">${escapeHtml(task.title)}</div>
                    </div>
                    ${task.description ? `<div class="item-description">${escapeHtml(task.description)}</div>` : ''}
                </div>
                <div class="item-actions">
                    <button class="btn btn-danger" onclick="deleteTask(${task.id})">Delete</button>
                </div>
            </div>
            <div class="item-meta">
                ${task.due_date ? `<span>Due: ${formatDateTime(task.due_date)}</span>` : '<span>No due date</span>'}
                ${task.completed ? '<span class="badge badge-success">Completed</span>' : '<span class="badge badge-warning">Pending</span>'}
            </div>
        </div>
    `).join('');
}

function displayTaskStats(tasks) {
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(task => task.completed).length;
    const activeTasks = totalTasks - completedTasks;
    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    document.getElementById('totalTasks').textContent = totalTasks;
    document.getElementById('activeTasks').textContent = activeTasks;
    document.getElementById('completedTasks').textContent = completedTasks;
    document.getElementById('completionRate').textContent = `${completionRate}%`;
}

async function createTask(event) {
    event.preventDefault();

    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    const dueDate = document.getElementById('taskDueDate').value;

    const taskData = {
        title,
        description,
        item_type: 'task',
        due_date: dueDate || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            closeTaskModal();
            loadTasks();
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to create task');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showError('Failed to create task');
    }
}

async function toggleTaskComplete(taskId, completed) {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ completed })
        });

        if (response.ok) {
            loadTasks();
        } else {
            showError('Failed to update task');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showError('Failed to update task');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadTasks();
        } else {
            showError('Failed to delete task');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showError('Failed to delete task');
    }
}

function filterTasks(filter) {
    currentTaskFilter = filter;

    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    loadTasks();
}

// Event Functions
async function loadEvents() {
    try {
        const response = await fetch(`${API_BASE_URL}/events`);
        const events = await response.json();
        displayEvents(events);
    } catch (error) {
        console.error('Error loading events:', error);
        showError('Failed to load events');
    }
}

function displayEvents(events) {
    const eventsList = document.getElementById('eventsList');

    if (events.length === 0) {
        eventsList.innerHTML = '<p class="empty-state">No events scheduled.</p>';
        return;
    }

    // Sort events by start time
    events.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

    eventsList.innerHTML = events.map(event => `
        <div class="item-card">
            <div class="item-header">
                <div style="flex: 1;">
                    <div class="item-title">${escapeHtml(event.title)}</div>
                    ${event.description ? `<div class="item-description">${escapeHtml(event.description)}</div>` : ''}
                </div>
                <div class="item-actions">
                    <button class="btn btn-danger" onclick="deleteEvent(${event.id})">Delete</button>
                </div>
            </div>
            <div class="item-meta">
                <span>Start: ${formatDateTime(event.start_time)}</span>
                <span>End: ${formatDateTime(event.end_time)}</span>
            </div>
        </div>
    `).join('');
}

async function createEvent(event) {
    event.preventDefault();

    const title = document.getElementById('eventTitle').value;
    const description = document.getElementById('eventDescription').value;
    const startTime = document.getElementById('eventStartTime').value;
    const endTime = document.getElementById('eventEndTime').value;

    if (new Date(endTime) <= new Date(startTime)) {
        showError('End time must be after start time');
        return;
    }

    const eventData = {
        title,
        description,
        item_type: 'event',
        start_time: startTime,
        end_time: endTime
    };

    try {
        const response = await fetch(`${API_BASE_URL}/events`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(eventData)
        });

        if (response.ok) {
            closeEventModal();
            loadEvents();
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to create event');
        }
    } catch (error) {
        console.error('Error creating event:', error);
        showError('Failed to create event');
    }
}

async function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to delete this event?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/events/${eventId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadEvents();
        } else {
            showError('Failed to delete event');
        }
    } catch (error) {
        console.error('Error deleting event:', error);
        showError('Failed to delete event');
    }
}

// Utility Functions
function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    alert(message);
}
