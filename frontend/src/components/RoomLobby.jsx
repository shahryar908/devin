import React, { useState } from 'react'

export default function RoomLobby({ room, user, onStartMatch, onLeaveRoom }) {
  const [copied, setCopied] = useState(false)

  if (!room) return null

  const isHost = room.hostId === user?.id
  const players = room.players || []
  const hostPlayer = players.find(p => p.playerId === room.hostId) || players[0]
  const challengerPlayer = players.find(p => p.playerId !== room.hostId)
  const isFull = players.length >= 2

  const copyRoomCode = () => {
    navigator.clipboard.writeText(room.code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="lobby-container animate-pop">
      <div className="glass-panel lobby-panel">
        {/* Header with Room Code */}
        <div className="lobby-header">
          <div className="lobby-tag">⚔️ BATTLE LOBBY</div>
          <h1 className="lobby-title">Duel Room</h1>
          
          <div className="code-display-card" onClick={copyRoomCode} title="Click to copy code">
            <span className="code-label">ROOM CODE:</span>
            <span className="code-value">{room.code}</span>
            <span className="copy-badge">{copied ? '✅ COPIED!' : '📋 COPY'}</span>
          </div>

          <div className="room-meta-tags">
            <span className="meta-tag">🎮 {room.mode?.toUpperCase()}</span>
            <span className="meta-tag">⏱️ {room.duration} SECONDS</span>
            <span className={`meta-tag diff-${room.difficulty}`}>
              ⚡ {room.difficulty?.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Combatants Split View */}
        <div className="combatants-arena">
          {/* Host Card */}
          <div className="combatant-slot glass-panel host-slot">
            <div className="slot-badge host">👑 HOST</div>
            <div className="avatar-placeholder">
              {hostPlayer ? hostPlayer.username.charAt(0).toUpperCase() : 'H'}
            </div>
            <h3 className="combatant-name">{hostPlayer ? hostPlayer.username : 'Host'}</h3>
            <span className="status-pill ready">READY</span>
          </div>

          {/* VS Divider */}
          <div className="vs-divider">
            <span className="vs-circle">VS</span>
            <div className="vs-pulse"></div>
          </div>

          {/* Challenger Card */}
          <div className={`combatant-slot glass-panel ${challengerPlayer ? 'opponent-slot' : 'empty-slot'}`}>
            {challengerPlayer ? (
              <>
                <div className="slot-badge challenger">⚔️ CHALLENGER</div>
                <div className="avatar-placeholder cyan">
                  {challengerPlayer.username.charAt(0).toUpperCase()}
                </div>
                <h3 className="combatant-name">{challengerPlayer.username}</h3>
                <span className="status-pill ready">READY</span>
              </>
            ) : (
              <div className="waiting-placeholder">
                <div className="radar-circle">
                  <div className="radar-scanner"></div>
                </div>
                <h3>Waiting for rival...</h3>
                <p>Share room code <strong>{room.code}</strong> with your opponent</p>
              </div>
            )}
          </div>
        </div>

        {/* Action Controls */}
        <div className="lobby-controls">
          <button className="btn btn-danger" onClick={onLeaveRoom}>
            Exit Lobby
          </button>

          {isHost ? (
            <button
              className={`btn btn-primary btn-large start-match-btn ${isFull ? 'animate-pulse-glow' : ''}`}
              disabled={!isFull}
              onClick={onStartMatch}
            >
              {isFull ? '⚡ START DUEL NOW!' : 'Waiting for 2nd Player...'}
            </button>
          ) : (
            <div className="guest-waiting-msg">
              <span className="spinner-dot"></span>
              <span>Waiting for host to initiate the countdown...</span>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .lobby-container {
          max-width: 860px;
          margin: 40px auto;
          padding: 0 20px;
        }
        .lobby-panel {
          padding: 40px;
          display: flex;
          flex-direction: column;
          gap: 36px;
        }
        .lobby-header {
          text-align: center;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
        }
        .lobby-tag {
          font-size: 0.8rem;
          font-weight: 800;
          letter-spacing: 0.15em;
          color: var(--primary);
        }
        .lobby-title {
          font-size: 2.4rem;
          color: #fff;
          margin: 0;
        }
        .code-display-card {
          display: inline-flex;
          align-items: center;
          gap: 12px;
          background: rgba(10, 12, 20, 0.7);
          border: 2px dashed var(--accent-cyan);
          padding: 12px 24px;
          border-radius: var(--radius-md);
          cursor: pointer;
          transition: all 0.2s ease;
          box-shadow: 0 0 20px var(--accent-cyan-glow);
        }
        .code-display-card:hover {
          transform: scale(1.03);
          background: rgba(10, 12, 20, 0.9);
        }
        .code-label {
          font-size: 0.8rem;
          color: var(--text-dim);
          font-weight: 700;
        }
        .code-value {
          font-family: var(--font-mono);
          font-size: 2rem;
          font-weight: 800;
          letter-spacing: 0.25em;
          color: #fff;
        }
        .copy-badge {
          font-size: 0.75rem;
          font-weight: 700;
          background: rgba(255, 255, 255, 0.1);
          padding: 4px 8px;
          border-radius: 6px;
          color: var(--accent-cyan);
        }
        .room-meta-tags {
          display: flex;
          gap: 10px;
          margin-top: 6px;
        }
        .meta-tag {
          font-size: 0.8rem;
          font-weight: 700;
          padding: 6px 12px;
          border-radius: 20px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--border-color);
          color: var(--text-muted);
        }
        .diff-easy { color: var(--success); border-color: rgba(16, 185, 129, 0.3); }
        .diff-medium { color: var(--primary); border-color: var(--primary-glow); }
        .diff-hard { color: var(--danger); border-color: var(--danger-glow); }

        .combatants-arena {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          position: relative;
        }
        .combatant-slot {
          flex: 1;
          padding: 30px 20px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 14px;
          text-align: center;
          min-height: 240px;
          justify-content: center;
          position: relative;
        }
        .slot-badge {
          position: absolute;
          top: 14px;
          left: 14px;
          font-size: 0.65rem;
          font-weight: 800;
          letter-spacing: 0.08em;
          padding: 3px 8px;
          border-radius: 12px;
        }
        .slot-badge.host {
          background: rgba(245, 158, 11, 0.2);
          color: var(--warning);
          border: 1px solid rgba(245, 158, 11, 0.4);
        }
        .slot-badge.challenger {
          background: rgba(6, 182, 212, 0.2);
          color: var(--accent-cyan);
          border: 1px solid rgba(6, 182, 212, 0.4);
        }
        .avatar-placeholder {
          width: 72px;
          height: 72px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--primary), #4c1d95);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font-display);
          font-size: 1.8rem;
          font-weight: 800;
          color: #fff;
          box-shadow: 0 0 20px var(--primary-glow);
        }
        .avatar-placeholder.cyan {
          background: linear-gradient(135deg, var(--accent-cyan), #0e7490);
          box-shadow: 0 0 20px var(--accent-cyan-glow);
        }
        .combatant-name {
          font-size: 1.3rem;
          color: #fff;
          margin: 0;
        }
        .status-pill.ready {
          font-size: 0.75rem;
          font-weight: 800;
          letter-spacing: 0.08em;
          color: var(--success);
          background: rgba(16, 185, 129, 0.15);
          border: 1px solid rgba(16, 185, 129, 0.35);
          padding: 4px 12px;
          border-radius: 12px;
        }
        .empty-slot {
          border-style: dashed;
          background: rgba(10, 12, 20, 0.3);
        }
        .waiting-placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
        }
        .waiting-placeholder h3 {
          font-size: 1.1rem;
          color: var(--text-muted);
        }
        .waiting-placeholder p {
          font-size: 0.8rem;
          color: var(--text-dim);
        }
        .radar-circle {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          border: 2px solid rgba(6, 182, 212, 0.4);
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
          animation: pulse 1.8s infinite;
        }
        .radar-scanner {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--accent-cyan);
          box-shadow: 0 0 10px var(--accent-cyan-glow);
        }
        .vs-divider {
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }
        .vs-circle {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: rgba(10, 12, 20, 0.9);
          border: 2px solid var(--border-color);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font-display);
          font-weight: 900;
          font-size: 1.1rem;
          color: var(--text-dim);
          z-index: 2;
        }
        .lobby-controls {
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-top: 1px solid var(--border-color);
          padding-top: 24px;
        }
        .start-match-btn {
          min-width: 260px;
        }
        .guest-waiting-msg {
          display: flex;
          align-items: center;
          gap: 10px;
          color: var(--text-muted);
          font-size: 0.95rem;
          font-weight: 500;
        }
        .spinner-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: var(--primary);
          animation: pulse 1.2s infinite ease-in-out;
        }
        @media (max-width: 640px) {
          .combatants-arena {
            flex-direction: column;
          }
          .vs-divider {
            margin: -10px 0;
          }
          .lobby-controls {
            flex-direction: column-reverse;
            gap: 16px;
          }
          .start-match-btn {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}
