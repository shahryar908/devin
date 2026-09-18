import React, { useState, useEffect, useCallback } from 'react'
import { Sound } from '../audio'

export default function GameArena({
  user,
  room,
  question,
  scores,
  timer,
  countdown,
  lastResult,
  onSubmitAnswer,
}) {
  const [selectedOption, setSelectedOption] = useState(null)
  const [answeredQuestionId, setAnsweredQuestionId] = useState(null)

  // Reset selected state when a new question arrives
  useEffect(() => {
    if (question?.questionId !== answeredQuestionId) {
      setSelectedOption(null)
      setAnsweredQuestionId(null)
    }
  }, [question, answeredQuestionId])

  const handleSelect = useCallback((option) => {
    if (selectedOption !== null || !question) return
    setSelectedOption(option)
    setAnsweredQuestionId(question.questionId)
    onSubmitAnswer(question.questionId, option)
  }, [selectedOption, question, onSubmitAnswer])

  // Support keyboard shortcuts 1, 2, 3, 4
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!question || selectedOption !== null) return
      const keyMap = { '1': 0, '2': 1, '3': 2, '4': 3 }
      if (keyMap[e.key] !== undefined && question.answerOptions[keyMap[e.key]] !== undefined) {
        handleSelect(question.answerOptions[keyMap[e.key]])
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [question, selectedOption, handleSelect])

  const myId = user?.id
  const opponentId = Object.keys(scores || {}).map(Number).find(id => id !== myId)
  const myScore = scores?.[myId] || 0
  const opponentScore = scores?.[opponentId] || 0
  const opponentName = room?.players?.find(p => p.playerId === opponentId)?.username || 'Rival'

  // Score bar calculation
  const totalScore = myScore + opponentScore
  const myPercent = totalScore === 0 ? 50 : Math.max(15, Math.min(85, Math.round((myScore / totalScore) * 100)))

  return (
    <div className="arena-container">
      {/* 5-second countdown overlay before game begins */}
      {countdown !== null && countdown > 0 && (
        <div className="countdown-overlay">
          <div className="countdown-number animate-countdown" key={countdown}>
            {countdown}
          </div>
          <div className="countdown-label">GET READY TO DUEL!</div>
        </div>
      )}

      {/* Arena HUD */}
      <div className="arena-hud glass-panel">
        {/* Duelists & Live Score */}
        <div className="hud-player me">
          <div className="hud-avatar">YOU</div>
          <div className="hud-info">
            <span className="hud-name">{user?.username}</span>
            <span className="hud-score my-score">{myScore}</span>
          </div>
        </div>

        {/* Center Clock */}
        <div className="hud-center">
          <div className={`timer-badge ${timer <= 10 ? 'danger animate-pulse-glow' : ''}`}>
            <span className="timer-icon">⏱️</span>
            <span className="timer-val">{timer !== null ? timer : room?.duration}s</span>
          </div>
          <div className="tug-of-war-bar">
            <div className="tug-fill my-fill" style={{ width: `${myPercent}%` }}></div>
            <div className="tug-fill opp-fill" style={{ width: `${100 - myPercent}%` }}></div>
          </div>
        </div>

        <div className="hud-player opponent">
          <div className="hud-info right">
            <span className="hud-name">{opponentName}</span>
            <span className="hud-score opp-score">{opponentScore}</span>
          </div>
          <div className="hud-avatar cyan">{opponentName.charAt(0).toUpperCase()}</div>
        </div>
      </div>

      {/* Arithmetic Combat Card */}
      <div className="combat-stage">
        {question ? (
          <div className="question-card glass-panel animate-pop" key={question.questionId}>
            <div className="question-meta">
              <span className="question-tag">CALCULATE FAST</span>
            </div>

            <div className="prompt-display">
              {question.prompt}
            </div>

            {/* Answer Options Grid */}
            <div className="options-grid">
              {question.answerOptions.map((opt, idx) => {
                const isSelected = selectedOption === opt
                let statusClass = ''

                if (isSelected && lastResult) {
                  statusClass = lastResult.correct ? 'opt-correct' : 'opt-wrong animate-shake'
                } else if (lastResult && !lastResult.correct && lastResult.correctAnswer === opt) {
                  statusClass = 'opt-reveal-correct'
                }

                return (
                  <button
                    key={`${question.questionId}-${opt}-${idx}`}
                    className={`option-btn ${statusClass}`}
                    onClick={() => handleSelect(opt)}
                    disabled={selectedOption !== null}
                  >
                    <span className="key-hint">[{idx + 1}]</span>
                    <span className="option-val">{opt}</span>
                  </button>
                )
              })}
            </div>
          </div>
        ) : (
          <div className="loading-question glass-panel">
            <div className="spinner"></div>
            <h3>Generating next math problem...</h3>
          </div>
        )}
      </div>

      <style>{`
        .arena-container {
          max-width: 900px;
          margin: 20px auto;
          padding: 0 20px;
          display: flex;
          flex-direction: column;
          gap: 24px;
          position: relative;
        }

        /* Countdown Overlay */
        .countdown-overlay {
          position: fixed;
          inset: 0;
          background: rgba(4, 6, 12, 0.92);
          backdrop-filter: blur(16px);
          z-index: 2000;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
        .countdown-number {
          font-family: var(--font-display);
          font-size: 9rem;
          font-weight: 900;
          color: #fff;
          text-shadow: 0 0 50px var(--primary-glow);
          line-height: 1;
        }
        .countdown-label {
          font-size: 1.4rem;
          font-weight: 800;
          letter-spacing: 0.25em;
          color: var(--accent-cyan);
          margin-top: 20px;
        }
        .animate-countdown {
          animation: countdownScale 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* HUD Header */
        .arena-hud {
          padding: 18px 28px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
        }
        .hud-player {
          display: flex;
          align-items: center;
          gap: 14px;
          flex: 1;
        }
        .hud-player.opponent {
          justify-content: flex-end;
        }
        .hud-avatar {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--primary), #4c1d95);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 0.9rem;
          color: #fff;
          box-shadow: 0 0 15px var(--primary-glow);
        }
        .hud-avatar.cyan {
          background: linear-gradient(135deg, var(--accent-cyan), #0e7490);
          box-shadow: 0 0 15px var(--accent-cyan-glow);
        }
        .hud-info {
          display: flex;
          flex-direction: column;
        }
        .hud-info.right {
          align-items: flex-end;
        }
        .hud-name {
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--text-muted);
        }
        .hud-score {
          font-family: var(--font-display);
          font-size: 1.8rem;
          font-weight: 800;
          line-height: 1.1;
        }
        .my-score { color: #c084fc; text-shadow: 0 0 10px var(--primary-glow); }
        .opp-score { color: #22d3ee; text-shadow: 0 0 10px var(--accent-cyan-glow); }

        .hud-center {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
          min-width: 220px;
        }
        .timer-badge {
          display: flex;
          align-items: center;
          gap: 6px;
          background: rgba(10, 12, 20, 0.7);
          border: 1px solid var(--border-color);
          padding: 6px 18px;
          border-radius: 20px;
          font-family: var(--font-display);
          font-size: 1.25rem;
          font-weight: 800;
          color: #fff;
        }
        .timer-badge.danger {
          border-color: var(--danger);
          color: #fda4af;
          background: rgba(244, 63, 94, 0.2);
        }
        .tug-of-war-bar {
          width: 100%;
          height: 6px;
          background: rgba(0, 0, 0, 0.5);
          border-radius: 3px;
          overflow: hidden;
          display: flex;
        }
        .tug-fill {
          height: 100%;
          transition: width 0.3s ease;
        }
        .my-fill { background: var(--primary); }
        .opp-fill { background: var(--accent-cyan); }

        /* Combat Stage & Question Card */
        .combat-stage {
          display: flex;
          justify-content: center;
        }
        .question-card {
          width: 100%;
          padding: 40px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 28px;
          text-align: center;
          background: linear-gradient(135deg, rgba(18, 20, 32, 0.85) 0%, rgba(26, 29, 48, 0.9) 100%);
        }
        .question-tag {
          font-size: 0.75rem;
          font-weight: 800;
          letter-spacing: 0.15em;
          color: var(--primary);
          background: rgba(139, 92, 246, 0.15);
          border: 1px solid rgba(139, 92, 246, 0.3);
          padding: 4px 12px;
          border-radius: 12px;
        }
        .prompt-display {
          font-family: var(--font-display);
          font-size: 3.4rem;
          font-weight: 800;
          color: #fff;
          letter-spacing: -0.01em;
          line-height: 1.2;
          text-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        }
        .options-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
          width: 100%;
          max-width: 600px;
        }
        .option-btn {
          background: rgba(10, 12, 20, 0.7);
          border: 1px solid var(--border-color);
          border-radius: var(--radius-lg);
          padding: 22px 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
          cursor: pointer;
          transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
          color: #fff;
        }
        .option-btn:hover:not(:disabled) {
          border-color: var(--primary);
          background: rgba(139, 92, 246, 0.15);
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(139, 92, 246, 0.25);
        }
        .option-btn:active:not(:disabled) {
          transform: scale(0.97);
        }
        .key-hint {
          position: absolute;
          top: 8px;
          left: 12px;
          font-family: var(--font-mono);
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--text-dim);
        }
        .option-val {
          font-family: var(--font-display);
          font-size: 1.9rem;
          font-weight: 800;
        }

        /* Result Feedback Colors */
        .opt-correct {
          background: rgba(16, 185, 129, 0.25) !important;
          border-color: var(--success) !important;
          color: #34d399 !important;
          box-shadow: 0 0 30px var(--success-glow) !important;
        }
        .opt-wrong {
          background: rgba(244, 63, 94, 0.25) !important;
          border-color: var(--danger) !important;
          color: #fb7185 !important;
          box-shadow: 0 0 30px var(--danger-glow) !important;
        }
        .opt-reveal-correct {
          border-color: var(--success) !important;
          color: #34d399 !important;
          background: rgba(16, 185, 129, 0.15) !important;
        }

        .loading-question {
          width: 100%;
          padding: 60px 20px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }
        .loading-question h3 {
          color: var(--text-muted);
          font-size: 1.1rem;
        }

        @media (max-width: 640px) {
          .prompt-display {
            font-size: 2.5rem;
          }
          .options-grid {
            grid-template-columns: 1fr;
          }
          .arena-hud {
            padding: 12px 16px;
          }
        }
      `}</style>
    </div>
  )
}
