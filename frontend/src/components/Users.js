import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const Users = ({ API }) => {
  const [users, setUsers] = useState([]);
  const [message, setMessage] = useState({ type: "", text: "" });

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: "", text: "" }), 3000);
  };

  const fetchUsers = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      showMessage("error", "Failed to fetch users");
    }
  }, [API]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleDelete = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;

    try {
      await axios.delete(`${API}/users/${userId}`);
      showMessage("success", "User deleted successfully");
      fetchUsers();
    } catch (error) {
      showMessage("error", error.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <div className="section" data-testid="users-section">
      <div className="section-header">
        <h2>User Management</h2>
      </div>

      {message.text && (
        <div className={`${message.type}-message`} data-testid="user-message">
          {message.text}
        </div>
      )}

      {users.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">👥</div>
          <h3>No users found</h3>
        </div>
      ) : (
        <table className="users-table" data-testid="users-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Created At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} data-testid={`user-row-${user.id}`}>
                <td data-testid="user-name">{user.name}</td>
                <td data-testid="user-email">{user.email}</td>
                <td>
                  <span
                    className={`badge user-role ${user.role}`}
                    data-testid="user-role"
                  >
                    {user.role}
                  </span>
                </td>
                <td data-testid="user-created-at">
                  {new Date(user.created_at).toLocaleDateString()}
                </td>
                <td>
                  <button
                    className="btn-delete"
                    onClick={() => handleDelete(user.id)}
                    data-testid="delete-user-button"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Users;