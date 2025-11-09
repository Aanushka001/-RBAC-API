import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const Notes = ({ API, userRole }) => {
  const [notes, setNotes] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    tags: "",
  });
  const [message, setMessage] = useState({ type: "", text: "" });

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: "", text: "" }), 3000);
  };

  const fetchNotes = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/notes`);
      setNotes(response.data);
    } catch (error) {
      showMessage("error", "Failed to fetch notes");
    }
  }, [API]);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const noteData = {
        title: formData.title,
        content: formData.content,
        tags: formData.tags
          .split(",")
          .map((tag) => tag.trim())
          .filter((tag) => tag),
      };

      if (editingNote) {
        await axios.put(`${API}/notes/${editingNote._id}`, noteData);
        showMessage("success", "Note updated successfully");
      } else {
        await axios.post(`${API}/notes`, noteData);
        showMessage("success", "Note created successfully");
      }
      fetchNotes();
      resetForm();
    } catch (error) {
      showMessage("error", error.response?.data?.detail || "Operation failed");
    }
  };

  const handleEdit = (note) => {
    setEditingNote(note);
    setFormData({
      title: note.title,
      content: note.content,
      tags: note.tags.join(", "),
    });
    setShowForm(true);
  };

  const handleDelete = async (noteId) => {
    if (!window.confirm("Are you sure you want to delete this note?")) return;

    try {
      await axios.delete(`${API}/notes/${noteId}`);
      showMessage("success", "Note deleted successfully");
      fetchNotes();
    } catch (error) {
      showMessage("error", error.response?.data?.detail || "Delete failed");
    }
  };

  const resetForm = () => {
    setFormData({ title: "", content: "", tags: "" });
    setEditingNote(null);
    setShowForm(false);
  };

  return (
    <div className="section" data-testid="notes-section">
      <div className="section-header">
        <h2>Notes</h2>
        {!showForm && (
          <button
            className="btn-add"
            onClick={() => setShowForm(true)}
            data-testid="add-note-button"
          >
            + Add Note
          </button>
        )}
      </div>

      {message.text && (
        <div className={`${message.type}-message`} data-testid="note-message">
          {message.text}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="form" data-testid="note-form">
          <div className="form-group">
            <label htmlFor="title">Title</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              data-testid="note-title-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="content">Content</label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleChange}
              required
              rows="6"
              style={{
                padding: "12px 16px",
                border: "2px solid #e2e8f0",
                borderRadius: "8px",
                fontSize: "1rem",
                fontFamily: "inherit",
              }}
              data-testid="note-content-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="tags">Tags (comma separated)</label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="work, personal, important"
              data-testid="note-tags-input"
            />
          </div>

          <div className="btn-group">
            <button
              type="button"
              className="btn-cancel"
              onClick={resetForm}
              data-testid="cancel-note-button"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-submit"
              data-testid="submit-note-button"
            >
              {editingNote ? "Update Note" : "Create Note"}
            </button>
          </div>
        </form>
      )}

      <div className="list" data-testid="notes-list">
        {notes.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📝</div>
            <h3>No notes yet</h3>
            <p>Create your first note to get started</p>
          </div>
        ) : (
          notes.map((note) => (
            <div
              key={note._id}
              className="list-item"
              data-testid={`note-item-${note._id}`}
            >
              <div className="list-item-header">
                <div>
                  <div className="list-item-title" data-testid="note-title">
                    {note.title}
                  </div>
                  {note.tags && note.tags.length > 0 && (
                    <div className="list-item-meta">
                      {note.tags.map((tag, index) => (
                        <span key={index} className="tag" data-testid="note-tag">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <p className="list-item-description" data-testid="note-content">
                {note.content}
              </p>
              <div className="list-item-actions">
                <button
                  className="btn-edit"
                  onClick={() => handleEdit(note)}
                  data-testid="edit-note-button"
                >
                  Edit
                </button>
                <button
                  className="btn-delete"
                  onClick={() => handleDelete(note._id)}
                  data-testid="delete-note-button"
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

export default Notes;