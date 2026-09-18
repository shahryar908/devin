import React, { useState, useEffect, useRef } from 'react'
import Navbar from './components/Navbar'
import AuthModal from './components/AuthModal'
import Dashboard from './components/Dashboard'
import RoomLobby from './components/RoomLobby'
import GameArena from './components/GameArena'
import MatchResultModal from './components/MatchResultModal'
import LeaderboardModal from './components/LeaderboardModal'

import { getMe, clearTokens } from './api'
import { getSocket, connectSocket, disconnectSocket } from './socket'
import { Sound } from './audio'

export default function App() {
  const [user, setUser] = useState(null)
  const [authOpen, setAuthOpen] = useState(false)
  const [leaderboardOpen, setLeaderboardOpen] = useState(false)
  const [isMuted, setIsMuted] = useState(Sound.isMuted)

  // Room & Match States
  const [room, setRoom] = useState(null)
  const [scores, setScores] = useState({})
  const [question, setQuestion] = useState(null)
  const [timer, setTimer] = useState(null)
  const [countdown, setCountdown] = useState(null)
  const [lastResult, setLastResult] = useState(null)
  const [matchResult, setMatchResult] = useState(null)
  const [error, setError] = useState(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isJoining, setIsJoining] = useState(false)

  const countdownIntervalRef = useRef(null)

  // 1. Initial Auth Check
  useEffect(() => {
    getMe()
      .then((userData) => {
        setUser(userData)
        connectSocket()
      })
      .catch(() => {
        clearTokens()
      })
  }, [])

  // 2. Setup Socket.IO Event Listeners
  useEffect(() => {
    const s = getSocket()

    const onRoomJoined = (roomData) => {
      setRoom(roomData)
      setError(null)
      setIsCreating(false)
      setIsJoining(false)

      const initialScores = {}
      roomData.players?.forEach((p) => {
        initialScores[p.playerId] = p.score || 0
      })
      setScores(initialScores)
    }

    const onPlayerJoined = (player) => {
      setRoom((prev) => {
        if (!prev) return prev
        const existing = prev.players || []
        if (existing.some((p) => p.playerId === player.playerId)) return prev
        return { ...prev, players: [...existing, player] }
      })
      setScores((prev) => ({ ...prev, [player.playerId]: player.score || 0 }))
    }

    const onPlayerLeft = (player) => {
      setRoom((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          players: (prev.players || []).filter((p) => p.playerId !== player.playerId),
        }
      })
    }

    const onRoomError = ({ message }) => {
      setError(message)
      setIsCreating(false)
      setIsJoining(false)
    }

    const onMatchStarting = ({ countdown: cd }) => {
      setCountdown(cd)
      Sound.playTick()

      // Local ticker for smooth 5-sec countdown
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current)
      let current = cd
      countdownIntervalRef.current = setInterval(() => {
        current -= 1
        if (current > 0) {
          setCountdown(current)
          Sound.playTick()
        } else {
          clearInterval(countdownIntervalRef.current)
          setCountdown(null)
        }
      }, 1000)
    }

    const onMatchStart = ({ duration }) => {
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current)
      setCountdown(null)
      setTimer(duration)
      setQuestion(null)
      setLastResult(null)
      setMatchResult(null)
      Sound.playStart()

      setRoom((prev) => (prev ? { ...prev, state: 'playing' } : prev))
    }

    const onTimerTick = ({ remaining }) => {
      setTimer(remaining)
      if (remaining <= 5 && remaining > 0) {
        Sound.playTick()
      }
    }

    const onQuestionNew = (q) => {
      setQuestion(q)
      setLastResult(null)
    }

    const onAnswerResult = (result) => {
      setLastResult(result)
      if (result.correct) {
        Sound.playCorrect()
      } else {
        Sound.playWrong()
      }
    }

    const onPlayerScore = ({ playerId, score }) => {
      setScores((prev) => ({
        ...prev,
        [playerId]: score,
      }))
    }

    const onMatchEnd = (endData) => {
      setQuestion(null)
      setCountdown(null)
      setMatchResult(endData)
      setRoom((prev) => (prev ? { ...prev, state: 'ended' } : null))
    }

    s.on('room:joined', onRoomJoined)
    s.on('room:playerJoined', onPlayerJoined)
    s.on('room:playerLeft', onPlayerLeft)
    s.on('room:error', onRoomError)
    s.on('match:starting', onMatchStarting)
    s.on('match:start', onMatchStart)
    s.on('timer:tick', onTimerTick)
    s.on('question:new', onQuestionNew)
    s.on('answer:result', onAnswerResult)
    s.on('player:score', onPlayerScore)
    s.on('match:end', onMatchEnd)

    return () => {
      s.off('room:joined', onRoomJoined)
      s.off('room:playerJoined', onPlayerJoined)
      s.off('room:playerLeft', onPlayerLeft)
      s.off('room:error', onRoomError)
      s.off('match:starting', onMatchStarting)
      s.off('match:start', onMatchStart)
      s.off('timer:tick', onTimerTick)
      s.off('question:new', onQuestionNew)
      s.off('answer:result', onAnswerResult)
      s.off('player:score', onPlayerScore)
      s.off('match:end', onMatchEnd)
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current)
    }
  }, [])

  // Handlers
  const handleAuthSuccess = (userData) => {
    setUser(userData)
    connectSocket()
  }

  const handleLogout = () => {
    clearTokens()
    setUser(null)
    disconnectSocket()
    setRoom(null)
    setQuestion(null)
    setMatchResult(null)
  }

  const handleToggleMute = () => {
    const muted = Sound.toggleMute()
    setIsMuted(muted)
  }

  const handleCreateRoom = ({ mode, duration, difficulty }) => {
    if (!user) {
      setAuthOpen(true)
      return
    }
    setError(null)
    setIsCreating(true)
    const s = connectSocket()
    s.emit('room:create', { mode, duration, difficulty })
  }

  const handleJoinRoom = (code) => {
    if (!user) {
      setAuthOpen(true)
      return
    }
    setError(null)
    setIsJoining(true)
    const s = connectSocket()
    s.emit('room:join', { code })
  }

  const handleStartMatch = () => {
    const s = getSocket()
    s.emit('match:requestStart')
  }

  const handleLeaveRoom = () => {
    const s = getSocket()
    s.emit('room:leave')
    setRoom(null)
    setQuestion(null)
    setCountdown(null)
    setTimer(null)
  }

  const handleSubmitAnswer = (questionId, answer) => {
    const s = getSocket()
    s.emit('answer:submit', { questionId, answer })
  }

  const handleReturnToLobby = () => {
    setMatchResult(null)
    setRoom(null)
    setQuestion(null)
  }

  const isInMatch =
    room &&
    (room.state === 'playing' || room.state === 'starting' || countdown !== null || question !== null)

  return (
    <div className="app-layout">
      <Navbar
        user={user}
        onOpenAuth={() => setAuthOpen(true)}
        onLogout={handleLogout}
        onOpenLeaderboard={() => setLeaderboardOpen(true)}
        isMuted={isMuted}
        onToggleMute={handleToggleMute}
      />

      <main className="main-content">
        {isInMatch ? (
          <GameArena
            user={user}
            room={room}
            question={question}
            scores={scores}
            timer={timer}
            countdown={countdown}
            lastResult={lastResult}
            onSubmitAnswer={handleSubmitAnswer}
          />
        ) : room ? (
          <RoomLobby
            room={room}
            user={user}
            onStartMatch={handleStartMatch}
            onLeaveRoom={handleLeaveRoom}
          />
        ) : (
          <Dashboard
            user={user}
            onCreateRoom={handleCreateRoom}
            onJoinRoom={handleJoinRoom}
            error={error}
            isCreating={isCreating}
            isJoining={isJoining}
          />
        )}
      </main>

      {/* Modals */}
      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      <LeaderboardModal
        isOpen={leaderboardOpen}
        onClose={() => setLeaderboardOpen(false)}
        user={user}
      />

      <MatchResultModal
        matchResult={matchResult}
        user={user}
        onReturnToLobby={handleReturnToLobby}
      />

      <style>{`
        .app-layout {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        .main-content {
          flex: 1;
          display: flex;
          flex-direction: column;
        }
      `}</style>
    </div>
  )
}
