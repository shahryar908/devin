import React, { useEffect } from 'react'
import confetti from 'canvas-confetti'
import { Sound } from '../audio'

export default function MatchResultModal({ matchResult, user, onReturnToLobby }) {
  if (!matchResult) return null

  const myId = user?.id
  const winnerId = matchResult.winner
  const isWinner = winnerId === myId
  const isDraw = winnerId === null
  const scoreboard = matchResult.scoreboard || []

  const myEntry = scoreboard.find(p => p.playerId === myId) || { score: 0 }
  const oppEntry = scoreboard.find(p => p.playerId !== myId) || { score: 0, username: 'Rival' }

  useEffect(() => {
    if (isWinner) {
      Sound.playWin()
      // Shoot celebratory confetti
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b'],
      })
    }
  }, [isWinner])

  return (
    <div className="modal-overlay">
      <div className="modal-content glass-panel result-card animate-pop">
        {/* Outcome Header Banner */}
        <div className="outcome-banner">
          <div className="outcome-icon">
            {isWinner ? '👑' : isDraw ? '🤝' : '⚔️'}
          </div>
          <h1 className={`outcome-title ${isWinner ? 'win' : isDraw ? 'draw' : 'defeat'}`}>
            {isWinner ? 'VICTORY!' : isDraw ? 'STALEMATE' : 'DEFEATED'}
          </h1>
          <p className="outcome-subtitle">
            {isWinner
              ? 'Supreme mental arithmetic! You dominated the arena.'
              : isDraw
              ? 'An exact tie! Both rivals matched blow for blow.'
              : 'Better luck next time. Train your reaction and duel again!'}
          </p>
        </div>

        {/* Head to Head Score Cards */}
        <div className="scores-duel-banner">
          <div className={`player-duel-box ${isWinner ? 'winner-box' : ''}`}>
            <span className="box-badge">YOU</span>
            <h3 className="box-name">{user?.username}</h3>
            <span className="box-score">{myEntry.score}</span>
            <span className="pts-label">PTS</span>
          </div>

          <div className="duel-vs">VS</div>

          <div className={`player-duel-box ${!isWinner && !isDraw ? 'winner-box' : ''}`}>
            <span className="box-badge opp">RIVAL</span>
            <h3 className="box-name">{oppEntry.username}</h3>
            <span className="box-score">{oppEntry.score}</span>
            <span className="pts-label">PTS</span>
          </div>
        </div>

        {/* Action Button */}
        <button
          className="btn btn-primary btn-large return-btn"
          onClick={onReturnToLobby}
        >
          ⚡ Return to Arena
        </button>
      </div>

      <style>{`
        .result-card {
          padding: 40px;
          text-align: center;
          display: flex;
          flex-direction: column;
          gap: 30px;
          max-width: 500px;
        }
        .outcome-banner {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
        }
        .outcome-icon {
          font-size: 4.5rem;
          line-height: 1;
          filter: drop-shadow(0 0 20px rgba(245, 158, 11, 0.5));
          animation: float 2.5s infinite ease-in-out;
        }
        .outcome-title {
          font-size: 2.8rem;
          font-weight: 900;
          letter-spacing: -0.02em;
        }
        .outcome-title.win {
          background: linear-gradient(135deg, #f59e0b 0%, #10b981 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          filter: drop-shadow(0 0 20px rgba(16, 185, 129, 0.4));
        }
        .outcome-title.defeat {
          color: var(--danger);
          text-shadow: 0 0 25px var(--danger-glow);
        }
        .outcome-title.draw {
          color: var(--accent-cyan);
          text-shadow: 0 0 25px var(--accent-cyan-glow);
        }
        .outcome-subtitle {
          color: var(--text-muted);
          font-size: 0.95rem;
          max-width: 360px;
        }

        .scores-duel-banner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          background: rgba(10, 12, 20, 0.6);
          border: 1px solid var(--border-color);
          border-radius: var(--radius-lg);
          padding: 20px 24px;
        }
        .player-duel-box {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
        }
        .winner-box {
          position: relative;
        }
        .box-badge {
          font-size: 0.65rem;
          font-weight: 800;
          letter-spacing: 0.1em;
          padding: 2px 8px;
          border-radius: 10px;
          background: rgba(139, 92, 246, 0.2);
          color: var(--primary);
          border: 1px solid rgba(139, 92, 246, 0.3);
        }
        .box-badge.opp {
          background: rgba(6, 182, 212, 0.2);
          color: var(--accent-cyan);
          border-color: rgba(6, 182, 212, 0.3);
        }
        .box-name {
          font-size: 1.1rem;
          color: #fff;
          margin-top: 4px;
        }
        .box-score {
          font-family: var(--font-display);
          font-size: 2.5rem;
          font-weight: 900;
          color: #fff;
          line-height: 1;
        }
        .pts-label {
          font-size: 0.7rem;
          font-weight: 700;
          color: var(--text-dim);
        }
        .duel-vs {
          font-family: var(--font-display);
          font-size: 1rem;
          font-weight: 900;
          color: var(--text-dim);
        }
        .return-btn {
          width: 100%;
        }
      `}</style>
    </div>
  )
}
