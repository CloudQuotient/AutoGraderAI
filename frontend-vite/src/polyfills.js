// Minimal polyfills for browser to satisfy node globals used by
// amazon-cognito-identity-js and its transitive deps.

// global
if (typeof window !== 'undefined' && typeof window.global === 'undefined') {
  window.global = window
}

// process
if (typeof window !== 'undefined' && typeof window.process === 'undefined') {
  window.process = { env: { DEBUG: undefined } }
}

// Buffer
import { Buffer } from 'buffer'
if (typeof window !== 'undefined' && typeof window.Buffer === 'undefined') {
  window.Buffer = Buffer
}


