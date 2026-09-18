import React, { useState } from 'react'
import { login, register, getMe } from '../api'

export default function AuthModal({ isOpen, onClose, onSuccess }) {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      if (isRegister) {
        if (!email.trim() || !username.trim() || !password) {
          throw new Error('Please fill in all fields')
        }
        await register(username.trim(), email.trim(), password)
      } else {
        if (!username.trim() || !password) {
          throw new Error('Please enter username and password')
        }
        await login(username.trim(), password)
      }

      const userData = await getMe()
      onSuccess(userData)
      onClose()
    } catch (err) {
      setError(err.message || 'An error occurred during authentication')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-panel animate-pop" onClick={(e) => e.stopPropagation()}>
        <div className="auth-header">
          <div className="auth-tabs">
            <button
              type="button"
              className={`auth-tab ${!isRegister ? 'active' : ''}`}
              onClick={() => { setIsRegister(false); setError(null); }}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`auth-tab ${isRegister ? 'active' : ''}`}
              onClick={() => { setIsRegister(true); setError(null); }}
            >
              Create Account
            </button>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="error-banner animate-shake">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. SpeedSolver"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
            />
          </div>

          {isRegister && (
            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                className="input-field"
                placeholder="solver@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-large submit-btn"
            disabled={loading}
          >
            {loading ? (
              <span className="spinner"></span>
            ) : isRegister ? (
              '⚡ Create Arena Account'
            ) : (
              '🚀 Enter Arena'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isRegister ? 'Already have an account?' : "Don't have an account yet?"}{' '}
            <span
              className="auth-switch-link"
              onClick={() => { setIsRegister(!isRegister); setError(null); }}
            >
              {isRegister ? 'Sign In' : 'Register Now'}
            </span>
          </p>
        </div>
      </div>

      <style>{`
        .auth-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid var(--border-color);
          padding: 16px 24px;
        }
        .auth-tabs {
          display: flex;
          gap: 12px;
        }
        .auth-tab {
          background: none;
          border: none;
          font-family: var(--font-display);
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-dim);
          cursor: pointer;
          padding: 6px 4px;
          position: relative;
          transition: all 0.2s ease;
        }
        .auth-tab.active {
          color: #fff;
        }
        .auth-tab.active::after {
          content: '';
          position: absolute;
          bottom: -17px;
          left: 0;
          right: 0;
          height: 2px;
          background: var(--primary);
          box-shadow: 0 0 10px var(--primary-glow);
        }
        .close-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          font-size: 1.2rem;
          cursor: pointer;
          padding: 4px;
          line-height: 1;
        }
        .close-btn:hover {
          color: #fff;
        }
        .auth-form {
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 18px;
        }
        .error-banner {
          background: rgba(244, 63, 94, 0.15);
          border: 1px solid rgba(244, 63, 94, 0.4);
          color: #fda4af;
          padding: 10px 14px;
          border-radius: var(--radius-md);
          font-size: 0.9rem;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
          text-align: left;
        }
        .form-group label {
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--text-muted);
          letter-spacing: 0.02em;
        }
        .submit-btn {
          margin-top: 10px;
          width: 100%;
        }
        .auth-footer {
          padding: 16px 24px;
          border-top: 1px solid var(--border-color);
          text-align: center;
          font-size: 0.9rem;
          color: var(--text-muted);
        }
        .auth-switch-link {
          color: var(--primary);
          font-weight: 600;
          cursor: pointer;
          text-decoration: underline;
        }
        .spinner {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
