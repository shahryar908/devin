import React from 'react'
import { Sound } from '../audio'

export default function Navbar({ user, onOpenAuth, onLogout, onOpenLeaderboard, isMuted, onToggleMute }) {
  return (
    <header className="navbar-container">
      <div className="navbar-content">
        <div className="logo-group">
          <div className="logo-icon">⚡</div>
          <div className="logo-text">
            <span className="logo-title">MATH DUEL</span>
            <span className="logo-subtitle">1V1 ARENA</span>
          </div>
        </div>

        <div className="navbar-actions">
          <button 
            className="btn btn-ghost btn-icon"
            onClick={onToggleMute}
            title={isMuted ? "Unmute Sound" : "Mute Sound"}
          >
            {isMuted ? '🔇' : '🔊'}
          </button>

          <button 
            className="btn btn-ghost"
            onClick={onOpenLeaderboard}
          >
            🏆 Leaderboard
          </button>

          {user ? (
            <div className="user-profile-menu">
              <div className="user-badge">
                <span className="avatar-dot"></span>
                <span className="user-name">{user.username}</span>
              </div>
              <button 
                className="btn btn-ghost btn-sm"
                onClick={onLogout}
                title="Log Out"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button 
              className="btn btn-primary"
              onClick={onOpenAuth}
            >
              Sign In / Register
            </button>
          )}
        </div>
      </div>

      <style>{`
        .navbar-container {
          width: 100%;
          border-bottom: 1px solid var(--border-color);
          background: rgba(9, 10, 16, 0.8);
          backdrop-filter: blur(12px);
          position: sticky;
          top: 0;
          z-index: 100;
        }
        .navbar-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 14px 24px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .logo-group {
          display: flex;
          align-items: center;
          gap: 12px;
          user-select: none;
          cursor: pointer;
        }
        .logo-icon {
          font-size: 1.8rem;
          background: linear-gradient(135deg, #8b5cf6, #06b6d4);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          filter: drop-shadow(0 0 10px rgba(139, 92, 246, 0.6));
          animation: pulse 2s infinite ease-in-out;
        }
        .logo-text {
          display: flex;
          flex-direction: column;
        }
        .logo-title {
          font-family: var(--font-display);
          font-weight: 800;
          font-size: 1.35rem;
          letter-spacing: -0.02em;
          color: #fff;
          line-height: 1.1;
        }
        .logo-subtitle {
          font-size: 0.65rem;
          font-weight: 700;
          letter-spacing: 0.15em;
          color: var(--accent-cyan);
        }
        .navbar-actions {
          display: flex;
          align-items: center;
          gap: 14px;
        }
        .btn-icon {
          font-size: 1.1rem;
          padding: 8px 12px;
        }
        .user-profile-menu {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .user-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--border-color);
          padding: 6px 14px;
          border-radius: var(--radius-md);
        }
        .avatar-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--success);
          box-shadow: 0 0 8px var(--success-glow);
        }
        .user-name {
          font-weight: 600;
          font-size: 0.95rem;
          color: var(--text-main);
        }
        .btn-sm {
          padding: 6px 12px;
          font-size: 0.85rem;
        }
      `}</style>
    </header>
  )
}
