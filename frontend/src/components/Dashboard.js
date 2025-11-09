import { useState } from "react";
// import axios from "axios";
import Tasks from "./Tasks";
import Notes from "./Notes";
import Users from "./Users";

const Dashboard = ({ user, handleLogout, API }) => {
  const [activeTab, setActiveTab] = useState("tasks");

  return (
    <div className="dashboard" data-testid="dashboard">
      <div className="dashboard-header">
        <h1 data-testid="dashboard-title">Dashboard</h1>
        <div className="header-right">
          <div className="user-info">
            <span className="user-name" data-testid="user-name">{user.name}</span>
            <span className={`user-role ${user.role}`} data-testid="user-role">{user.role}</span>
          </div>
          <button 
            className="btn-logout" 
            onClick={handleLogout}
            data-testid="logout-button"
          >
            Logout
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="tabs">
          <button
            className={`tab ${activeTab === "tasks" ? "active" : ""}`}
            onClick={() => setActiveTab("tasks")}
            data-testid="tasks-tab"
          >
            Tasks
          </button>
          <button
            className={`tab ${activeTab === "notes" ? "active" : ""}`}
            onClick={() => setActiveTab("notes")}
            data-testid="notes-tab"
          >
            Notes
          </button>
          {user.role === "admin" && (
            <button
              className={`tab ${activeTab === "users" ? "active" : ""}`}
              onClick={() => setActiveTab("users")}
              data-testid="users-tab"
            >
              Users
            </button>
          )}
        </div>

        {activeTab === "tasks" && <Tasks API={API} userRole={user.role} />}
        {activeTab === "notes" && <Notes API={API} userRole={user.role} />}
        {activeTab === "users" && user.role === "admin" && <Users API={API} />}
      </div>
    </div>
  );
};

export default Dashboard;