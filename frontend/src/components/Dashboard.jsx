import React, { useState, useEffect } from 'react'
import { getUserStats } from '../api'

export default function Dashboard({ user, onCreateRoom, onJoinRoom, error, isCreating, isJoining }) {
  const [difficulty, setDifficulty] = useState('medium')
  const [duration, setDuration] = useState(60)
  const [joinCode, setJoinCode] = useState('')
  const [stats, setStats] = useState(null)

  useEffect(() => {
    if (user?.id) {
      getUserStats(user.id)
        .then(setStats)
        .catch(() => {})
    }
  }, [user])

  const handleJoinSubmit = (e) => {
    e.preventDefault()
    const trimmed = joinCode.trim().toUpperCase()
    if (trimmed.length === 6) {
      onJoinRoom(trimmed)
    }
  }

  const winRate = stats?.totalMatches 
    ? Math.round((stats.wins / stats.totalMatches) * 100) 
    : 0

  return (
    <div className="dashboard-container">
      {/* Hero Welcome & Stats */}
      <section className="hero-section glass-panel">
        <div className="hero-left">
          <div className="combatant-tag">⚔️ READY FOR COMBAT</div>
          <h1 className="hero-title">
            Welcome back, <span className="highlight">{user?.username || 'Challenger'}</span>
          </h1>
          <p className="hero-desc">
            Test your lightning arithmetic against rivals in real-time head-to-head duels.
            Rack up wins and climb the global leaderboard.
          </p>
        </div>

        {user && stats && (
          <div className="hero-stats-grid">
            <div className="stat-card">
              <span className="stat-val">{stats.totalMatches}</span>
              <span className="stat-lbl">Matches</span>
            </div>
            <div className="stat-card">
              <span className="stat-val text-success">{stats.wins}</span>
              <span className="stat-lbl">Victories</span>
            </div>
            <div className="stat-card">
              <span className="stat-val text-cyan">{winRate}%</span>
              <span className="stat-lbl">Win Rate</span>
            </div>
            <div className="stat-card">
              <span className="stat-val text-purple">
                {Math.round((stats.accuracy || 0) * 100)}%
              </span>
              <span className="stat-lbl">Accuracy</span>
            </div>
          </div>
        )}
      </section>

      {error && (
        <div className="error-banner animate-shake">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* Main Duel Setup Cards */}
      <div className="duel-grid">
        {/* Create Room Card */}
        <div className="glass-panel action-card">
          <div className="card-header">
            <div className="card-badge">HOST DUEL</div>
            <h2>Create Battle Arena</h2>
            <p>Configure match parameters and generate a room invite code.</p>
          </div>

          <div className="config-section">
            <label className="config-label">Difficulty Level</label>
            <div className="pill-group">
              <button
                type="button"
                className={`pill-btn easy ${difficulty === 'easy' ? 'active' : ''}`}
                onClick={() => setDifficulty('easy')}
              >
                🌱 Easy
                <span className="pill-sub">Add/Sub (1-10)</span>
              </button>
              <button
                type="button"
                className={`pill-btn medium ${difficulty === 'medium' ? 'active' : ''}`}
                onClick={() => setDifficulty('medium')}
              >
                ⚡ Medium
                <span className="pill-sub">Add/Sub/Mul</span>
              </button>
              <button
                type="button"
                className={`pill-btn hard ${difficulty === 'hard' ? 'active' : ''}`}
                onClick={() => setDifficulty('hard')}
              >
                🔥 Hard
                <span className="pill-sub">All Ops (Div/Mul)</span>
              </button>
            </div>
          </div>

          <div className="config-section">
            <label className="config-label">Round Duration</label>
            <div className="pill-group-duration">
              {[30, 60, 90].map((sec) => (
                <button
                  key={sec}
                  type="button"
                  className={`duration-pill ${duration === sec ? 'active' : ''}`}
                  onClick={() => setDuration(sec)}
                >
                  ⏱️ {sec} Seconds
                </button>
              ))}
            </div>
          </div>

          <button
            className="btn btn-primary btn-large create-btn"
            onClick={() => onCreateRoom({ mode: 'blitz', duration, difficulty })}
            disabled={isCreating}
          >
            {isCreating ? 'Creating Arena...' : '🚀 Create Duel Arena'}
          </button>
        </div>

        {/* Join Room Card */}
        <div className="glass-panel action-card join-card">
          <div className="card-header">
            <div className="card-badge cyan">JOIN DUEL</div>
            <h2>Enter via Code</h2>
            <p>Have an invite code from a friend or rival? Join their lobby.</p>
          </div>

          <form onSubmit={handleJoinSubmit} className="join-form">
            <div className="code-input-container">
              <input
                type="text"
                className="code-input"
                placeholder="ABCDEF"
                maxLength={6}
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                required
              />
              <span className="input-hint">Enter 6-character room code</span>
            </div>

            <button
              type="submit"
              className="btn btn-cyan btn-large join-btn"
              disabled={isJoining || joinCode.trim().length !== 6}
            >
              {isJoining ? 'Connecting...' : '⚔️ Join Arena'}
            </button>
          </form>

          <div className="quick-rules">
            <h4>Combat Rules</h4>
            <ul>
              <li>⚡ 10 Points awarded per correct calculation</li>
              <li>⏱️ 3-second rapid reaction per problem</li>
              <li>👑 Highest score when the clock expires wins!</li>
            </ul>
          </div>
        </div>
      </div>

      <style>{`
        .dashboard-container {
          max-width: 1100px;
          margin: 30px auto;
          padding: 0 20px;
          display: flex;
          flex-direction: column;
          gap: 28px;
        }
        .hero-section {
          padding: 32px 36px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 24px;
          background: linear-gradient(135deg, rgba(18, 20, 32, 0.8) 0%, rgba(28, 32, 54, 0.7) 100%);
        }
        .hero-left {
          max-width: 580px;
        }
        .combatant-tag {
          font-size: 0.75rem;
          font-weight: 700;
          letter-spacing: 0.12em;
          color: var(--accent-cyan);
          margin-bottom: 8px;
        }
        .hero-title {
          font-size: 2.2rem;
          color: #fff;
          margin-bottom: 12px;
          line-height: 1.2;
        }
        .highlight {
          background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .hero-desc {
          color: var(--text-muted);
          font-size: 1rem;
          line-height: 1.5;
        }
        .hero-stats-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
        }
        .stat-card {
          background: rgba(10, 12, 20, 0.5);
          border: 1px solid var(--border-color);
          padding: 12px 18px;
          border-radius: var(--radius-md);
          text-align: center;
          min-width: 90px;
        }
        .stat-val {
          font-family: var(--font-display);
          font-size: 1.5rem;
          font-weight: 800;
          display: block;
          color: #fff;
        }
        .text-success { color: var(--success); }
        .text-cyan { color: var(--accent-cyan); }
        .text-purple { color: var(--primary); }
        .stat-lbl {
          font-size: 0.75rem;
          color: var(--text-dim);
          font-weight: 600;
          text-transform: uppercase;
        }
        .error-banner {
          background: rgba(244, 63, 94, 0.15);
          border: 1px solid rgba(244, 63, 94, 0.4);
          color: #fda4af;
          padding: 12px 18px;
          border-radius: var(--radius-md);
          font-weight: 500;
        }
        .duel-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 24px;
        }
        .action-card {
          padding: 30px;
          display: flex;
          flex-direction: column;
          gap: 22px;
        }
        .card-badge {
          display: inline-block;
          font-size: 0.7rem;
          font-weight: 800;
          letter-spacing: 0.1em;
          padding: 4px 10px;
          border-radius: 20px;
          background: rgba(139, 92, 246, 0.18);
          color: var(--primary);
          border: 1px solid rgba(139, 92, 246, 0.35);
          margin-bottom: 8px;
        }
        .card-badge.cyan {
          background: rgba(6, 182, 212, 0.18);
          color: var(--accent-cyan);
          border-color: rgba(6, 182, 212, 0.35);
        }
        .card-header h2 {
          font-size: 1.5rem;
          color: #fff;
          margin-bottom: 6px;
        }
        .card-header p {
          font-size: 0.9rem;
          color: var(--text-muted);
        }
        .config-section {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .config-label {
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .pill-group {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 8px;
        }
        .pill-btn {
          background: rgba(10, 12, 20, 0.5);
          border: 1px solid var(--border-color);
          color: var(--text-main);
          padding: 10px 8px;
          border-radius: var(--radius-md);
          font-family: var(--font-display);
          font-weight: 600;
          font-size: 0.85rem;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          transition: all 0.2s ease;
        }
        .pill-sub {
          font-size: 0.65rem;
          color: var(--text-dim);
          font-weight: 500;
        }
        .pill-btn:hover {
          border-color: rgba(255, 255, 255, 0.2);
          background: rgba(20, 24, 40, 0.6);
        }
        .pill-btn.easy.active {
          border-color: var(--success);
          background: rgba(16, 185, 129, 0.12);
          color: #34d399;
          box-shadow: 0 0 15px rgba(16, 185, 129, 0.25);
        }
        .pill-btn.medium.active {
          border-color: var(--primary);
          background: rgba(139, 92, 246, 0.15);
          color: #c084fc;
          box-shadow: 0 0 15px var(--primary-glow);
        }
        .pill-btn.hard.active {
          border-color: var(--danger);
          background: rgba(244, 63, 94, 0.15);
          color: #fb7185;
          box-shadow: 0 0 15px var(--danger-glow);
        }
        .pill-group-duration {
          display: flex;
          gap: 8px;
        }
        .duration-pill {
          flex: 1;
          background: rgba(10, 12, 20, 0.5);
          border: 1px solid var(--border-color);
          color: var(--text-muted);
          padding: 10px 12px;
          border-radius: var(--radius-md);
          font-weight: 600;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .duration-pill:hover {
          color: #fff;
          border-color: rgba(255, 255, 255, 0.2);
        }
        .duration-pill.active {
          background: rgba(255, 255, 255, 0.1);
          color: #fff;
          border-color: var(--accent-cyan);
          box-shadow: 0 0 12px var(--accent-cyan-glow);
        }
        .create-btn, .join-btn {
          width: 100%;
          margin-top: auto;
        }
        .join-form {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .code-input-container {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .code-input {
          width: 100%;
          text-align: center;
          font-family: var(--font-mono);
          font-size: 1.8rem;
          font-weight: 700;
          letter-spacing: 0.35em;
          text-transform: uppercase;
          background: rgba(10, 12, 20, 0.7);
          border: 2px dashed var(--border-color);
          border-radius: var(--radius-md);
          padding: 12px;
          color: var(--accent-cyan);
          outline: none;
          transition: all 0.2s ease;
        }
        .code-input:focus {
          border-color: var(--accent-cyan);
          border-style: solid;
          box-shadow: 0 0 20px var(--accent-cyan-glow);
        }
        .input-hint {
          font-size: 0.75rem;
          color: var(--text-dim);
          text-align: center;
        }
        .quick-rules {
          background: rgba(10, 12, 20, 0.4);
          border: 1px solid var(--border-color);
          border-radius: var(--radius-md);
          padding: 14px 18px;
          font-size: 0.85rem;
        }
        .quick-rules h4 {
          font-size: 0.85rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 8px;
        }
        .quick-rules ul {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 6px;
          color: var(--text-muted);
        }
      `}</style>
    </div>
  )
}
