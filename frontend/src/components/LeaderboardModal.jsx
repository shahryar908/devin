import React, { useState, useEffect } from 'react'
import { getLeaderboard, getUserMatches } from '../api'

export default function LeaderboardModal({ isOpen, onClose, user }) {
  const [activeTab, setActiveTab] = useState('global')
  const [leaderboard, setLeaderboard] = useState([])
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!isOpen) return
    setLoading(true)
    setError(null)

    if (activeTab === 'global') {
      getLeaderboard(50)
        .then(setLeaderboard)
        .catch(err => setError(err.message || 'Failed to load leaderboard'))
        .finally(() => setLoading(false))
    } else if (activeTab === 'history' && user?.id) {
      getUserMatches(user.id)
        .then(setMatches)
        .catch(err => setError(err.message || 'Failed to load match history'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [isOpen, activeTab, user])

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-panel lb-modal animate-pop" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="lb-header">
          <div className="lb-tabs">
            <button
              className={`lb-tab ${activeTab === 'global' ? 'active' : ''}`}
              onClick={() => setActiveTab('global')}
            >
              🏆 Global Rankings
            </button>
            {user && (
              <button
                className={`lb-tab ${activeTab === 'history' ? 'active' : ''}`}
                onClick={() => setActiveTab('history')}
              >
                📜 Match History
              </button>
            )}
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {/* Content Body */}
        <div className="lb-body">
          {loading ? (
            <div className="lb-loading">
              <span className="spinner"></span>
              <p>Fetching arena records...</p>
            </div>
          ) : error ? (
            <div className="error-banner">
              <span>⚠️ {error}</span>
            </div>
          ) : activeTab === 'global' ? (
            <div className="table-responsive">
              {leaderboard.length === 0 ? (
                <div className="empty-state">
                  <p>No duel records found yet. Be the first to claim victory!</p>
                </div>
              ) : (
                <table className="lb-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Duelist</th>
                      <th>Wins</th>
                      <th>Matches</th>
                      <th>Accuracy</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard.map((player, idx) => {
                      const rank = idx + 1
                      const isMe = user && player.userId === user.id
                      return (
                        <tr key={player.userId} className={isMe ? 'my-row' : ''}>
                          <td className="rank-col">
                            {rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : rank}
                          </td>
                          <td className="player-col">
                            <span className="player-name">
                              {player.username}
                              {isMe && <span className="you-tag">YOU</span>}
                            </span>
                          </td>
                          <td className="wins-col">{player.wins}</td>
                          <td className="matches-col">{player.matches}</td>
                          <td className="acc-col">{Math.round((player.accuracy || 0) * 100)}%</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              )}
            </div>
          ) : (
            <div className="history-list">
              {matches.length === 0 ? (
                <div className="empty-state">
                  <p>You haven't completed any duels yet. Enter the arena!</p>
                </div>
              ) : (
                matches.map((m) => {
                  const dateStr = new Date(m.startedAt).toLocaleDateString()
                  const timeStr = new Date(m.startedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                  return (
                    <div key={m.id} className="history-card glass-panel">
                      <div className="history-badge-group">
                        <span className={`hist-pill ${m.isWinner ? 'win' : 'loss'}`}>
                          {m.isWinner ? 'VICTORY' : 'DEFEAT'}
                        </span>
                        <span className="hist-meta">{m.duration}s Blitz</span>
                      </div>
                      <div className="hist-stats">
                        <span className="hist-score">
                          🎯 {m.correctAnswers}/{m.totalAnswers} Correct
                        </span>
                        <span className="hist-date">{dateStr} {timeStr}</span>
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          )}
        </div>
      </div>

      <style>{`
        .lb-modal {
          max-width: 680px;
          height: 600px;
          display: flex;
          flex-direction: column;
        }
        .lb-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid var(--border-color);
          padding: 16px 24px;
        }
        .lb-tabs {
          display: flex;
          gap: 16px;
        }
        .lb-tab {
          background: none;
          border: none;
          font-family: var(--font-display);
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-dim);
          cursor: pointer;
          padding: 6px 0;
          position: relative;
          transition: all 0.2s ease;
        }
        .lb-tab.active {
          color: #fff;
        }
        .lb-tab.active::after {
          content: '';
          position: absolute;
          bottom: -17px;
          left: 0;
          right: 0;
          height: 2px;
          background: var(--accent-cyan);
          box-shadow: 0 0 10px var(--accent-cyan-glow);
        }
        .lb-body {
          flex: 1;
          overflow-y: auto;
          padding: 20px 24px;
        }
        .lb-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 12px;
          color: var(--text-muted);
        }
        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: var(--text-muted);
        }
        .table-responsive {
          width: 100%;
        }
        .lb-table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
        }
        .lb-table th {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--text-dim);
          padding: 10px 14px;
          border-bottom: 1px solid var(--border-color);
        }
        .lb-table td {
          padding: 12px 14px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.04);
          font-size: 0.95rem;
        }
        .lb-table tr:hover {
          background: rgba(255, 255, 255, 0.03);
        }
        .my-row {
          background: rgba(139, 92, 246, 0.12) !important;
        }
        .rank-col {
          font-weight: 800;
          font-family: var(--font-display);
        }
        .player-name {
          font-weight: 600;
          color: #fff;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .you-tag {
          font-size: 0.65rem;
          font-weight: 800;
          background: var(--primary);
          color: #fff;
          padding: 2px 6px;
          border-radius: 4px;
        }
        .wins-col {
          font-weight: 700;
          color: var(--warning);
        }
        .matches-col {
          color: var(--text-muted);
        }
        .acc-col {
          color: var(--accent-cyan);
          font-weight: 600;
        }
        .history-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .history-card {
          padding: 14px 18px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .history-badge-group {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .hist-pill {
          font-size: 0.75rem;
          font-weight: 800;
          padding: 4px 10px;
          border-radius: 6px;
        }
        .hist-pill.win {
          background: rgba(16, 185, 129, 0.2);
          color: #34d399;
          border: 1px solid rgba(16, 185, 129, 0.4);
        }
        .hist-pill.loss {
          background: rgba(244, 63, 94, 0.2);
          color: #fda4af;
          border: 1px solid rgba(244, 63, 94, 0.4);
        }
        .hist-meta {
          font-size: 0.85rem;
          color: var(--text-muted);
        }
        .hist-stats {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 2px;
        }
        .hist-score {
          font-weight: 600;
          font-size: 0.9rem;
          color: #fff;
        }
        .hist-date {
          font-size: 0.75rem;
          color: var(--text-dim);
        }
      `}</style>
    </div>
  )
}
