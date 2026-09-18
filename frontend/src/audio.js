// Synthesized Web Audio API sound effects (zero external files required)

let audioCtx = null

function getAudioContext() {
  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext
    if (AudioContext) {
      audioCtx = new AudioContext()
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume()
  }
  return audioCtx
}

export const Sound = {
  isMuted: localStorage.getItem('sound_muted') === 'true',

  toggleMute() {
    this.isMuted = !this.isMuted
    localStorage.setItem('sound_muted', String(this.isMuted))
    return this.isMuted
  },

  playTick() {
    if (this.isMuted) return
    const ctx = getAudioContext()
    if (!ctx) return

    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    osc.type = 'sine'
    osc.frequency.setValueAtTime(800, ctx.currentTime)

    gain.gain.setValueAtTime(0.12, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08)

    osc.connect(gain)
    gain.connect(ctx.destination)

    osc.start()
    osc.stop(ctx.currentTime + 0.08)
  },

  playCorrect() {
    if (this.isMuted) return
    const ctx = getAudioContext()
    if (!ctx) return

    const now = ctx.currentTime
    const notes = [523.25, 659.25, 783.99] // C5, E5, G5

    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()

      osc.type = 'triangle'
      osc.frequency.setValueAtTime(freq, now + idx * 0.07)

      gain.gain.setValueAtTime(0.15, now + idx * 0.07)
      gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.07 + 0.18)

      osc.connect(gain)
      gain.connect(ctx.destination)

      osc.start(now + idx * 0.07)
      osc.stop(now + idx * 0.07 + 0.18)
    })
  },

  playWrong() {
    if (this.isMuted) return
    const ctx = getAudioContext()
    if (!ctx) return

    const now = ctx.currentTime
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    osc.type = 'sawtooth'
    osc.frequency.setValueAtTime(160, now)
    osc.frequency.linearRampToValueAtTime(120, now + 0.22)

    gain.gain.setValueAtTime(0.18, now)
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22)

    osc.connect(gain)
    gain.connect(ctx.destination)

    osc.start()
    osc.stop(now + 0.22)
  },

  playStart() {
    if (this.isMuted) return
    const ctx = getAudioContext()
    if (!ctx) return

    const now = ctx.currentTime
    const chord = [440, 554.37, 659.25, 880] // A major

    chord.forEach((freq) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()

      osc.type = 'sine'
      osc.frequency.setValueAtTime(freq, now)

      gain.gain.setValueAtTime(0.1, now)
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45)

      osc.connect(gain)
      gain.connect(ctx.destination)

      osc.start(now)
      osc.stop(now + 0.45)
    })
  },

  playWin() {
    if (this.isMuted) return
    const ctx = getAudioContext()
    if (!ctx) return

    const now = ctx.currentTime
    const arpeggio = [523.25, 659.25, 783.99, 1046.5] // C, E, G, High C

    arpeggio.forEach((freq, idx) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()

      osc.type = 'triangle'
      osc.frequency.setValueAtTime(freq, now + idx * 0.1)

      gain.gain.setValueAtTime(0.18, now + idx * 0.1)
      gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.1 + 0.35)

      osc.connect(gain)
      gain.connect(ctx.destination)

      osc.start(now + idx * 0.1)
      osc.stop(now + idx * 0.1 + 0.35)
    })
  }
}
