import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const Tasks = ({ API, userRole }) => {
  const [tasks, setTasks] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    status: "todo",
    priority: "medium",
  });
  const [message, setMessage] = useState({ type: "", text: "" });

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: "", text: "" }), 3000);
  };

  const fetchTasks = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/tasks`);
      setTasks(response.data);
    } catch (error) {
      showMessage("error", "Failed to fetch tasks");
    }
  }, [API]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTask) {
        await axios.put(`${API}/tasks/${editingTask._id}`, formData);
        showMessage("success", "Task updated successfully");
      } else {
        await axios.post(`${API}/tasks`, formData);
        showMessage("success", "Task created successfully");
      }
      fetchTasks();
      resetForm();
    } catch (error) {
      showMessage("error", error.response?.data?.detail || "Operation failed");
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description,
      status: task.status,
      priority: task.priority,
    });
    setShowForm(true);
  };

  const handleDelete = async (taskId) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;

    try {
      await axios.delete(`${API}/tasks/${taskId}`);
      showMessage("success", "Task deleted successfully");
      fetchTasks();
    } catch (error) {
      showMessage("error", error.response?.data?.detail || "Delete failed");
    }
  };

  const resetForm = () => {
    setFormData({ title: "", description: "", status: "todo", priority: "medium" });
    setEditingTask(null);
    setShowForm(false);
  };

  return (
    <div className="section" data-testid="tasks-section">
      <div className="section-header">
        <h2>Tasks</h2>
        {!showForm && (
          <button 
            className="btn-add" 
            onClick={() => setShowForm(true)}
            data-testid="add-task-button"
          >
            + Add Task
          </button>
        )}
      </div>

      {message.text && (
        <div className={`${message.type}-message`} data-testid="task-message">
          {message.text}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="form" data-testid="task-form">
          <div className="form-group">
            <label htmlFor="title">Title</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              data-testid="task-title-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows="4"
              style={{
                padding: "12px 16px",
                border: "2px solid #e2e8f0",
                borderRadius: "8px",
                fontSize: "1rem",
                fontFamily: "inherit",
              }}
              data-testid="task-description-input"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
                style={{
                  padding: "12px 16px",
                  border: "2px solid #e2e8f0",
                  borderRadius: "8px",
                  fontSize: "1rem",
                }}
                data-testid="task-status-select"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="priority">Priority</label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                style={{
                  padding: "12px 16px",
                  border: "2px solid #e2e8f0",
                  borderRadius: "8px",
                  fontSize: "1rem",
                }}
                data-testid="task-priority-select"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          <div className="btn-group">
            <button 
              type="button" 
              className="btn-cancel" 
              onClick={resetForm}
              data-testid="cancel-task-button"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-submit"
              data-testid="submit-task-button"
            >
              {editingTask ? "Update Task" : "Create Task"}
            </button>
          </div>
        </form>
      )}

      <div className="list" data-testid="tasks-list">
        {tasks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📋</div>
            <h3>No tasks yet</h3>
            <p>Create your first task to get started</p>
          </div>
        ) : (
          tasks.map((task) => (
            <div key={task._id} className="list-item" data-testid={`task-item-${task._id}`}>
              <div className="list-item-header">
                <div>
                  <div className="list-item-title" data-testid="task-title">
                    {task.title}
                  </div>
                  <div className="list-item-meta">
                    <span
                      className={`badge badge-priority-${task.priority}`}
                      data-testid="task-priority"
                    >
                      {task.priority}
                    </span>
                    <span
                      className={`badge badge-status-${task.status}`}
                      data-testid="task-status"
                    >
                      {task.status.replace("_", " ")}
                    </span>
                  </div>
                </div>
              </div>
              <p className="list-item-description" data-testid="task-description">
                {task.description}
              </p>
              <div className="list-item-actions">
                <button
                  className="btn-edit"
                  onClick={() => handleEdit(task)}
                  data-testid="edit-task-button"
                >
                  Edit
                </button>
                <button
                  className="btn-delete"
                  onClick={() => handleDelete(task._id)}
                  data-testid="delete-task-button"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Tasks;