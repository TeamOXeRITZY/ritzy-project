import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // We'll try 'localhost' instead of '127.0.0.1' as it's more reliable on some macOS setups
  const API_BASE_URL = "http://localhost:8000";

  const fetchFeed = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/feed`);
      setPosts(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching feed:", err);
      setError("Could not connect to Ritzy Backend. Please make sure python3 main.py is running!");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, []);

  if (loading) return <div className="status-msg">Loading Ritzy...</div>;
  if (error) return <div className="status-msg error">{error}</div>;

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="logo">Ritzy</h1>
      </header>

      <main className="feed">
        {posts.length === 0 ? (
          <div className="empty-state">
            <p>No posts yet. Be the first to share something!</p>
            <small>Tip: Add posts via http://localhost:8000/docs</small>
          </div>
        ) : (
          posts.map(post => (
            <div key={post.id} className="post-card">
              <div className="post-header">
                <img
                  src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${post.user_id}`}
                  alt="avatar"
                  className="profile-pic"
                />
                <span className="username">User {post.user_id}</span>
              </div>

              <div className="post-content">
                <div className="media-placeholder">
                  <div className="video-icon">🎥</div>
                  <div className="url-text">{post.content_url}</div>
                </div>
                <p className="caption">
                  <strong className="caption-user">User {post.user_id}</strong> {post.caption}
                </p>
              </div>

              <div className="post-footer">
                <button className="action-btn">❤️ {post.likes}</button>
                <button className="action-btn">💬 Comment</button>
                <button className="action-btn">✈️ Share</button>
              </div>
            </div>
          ))
        )}
      </main>
    </div>
  );
}

export default App;
