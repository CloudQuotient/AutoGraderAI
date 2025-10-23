// Central config for frontend API base URL.
// Set REACT_APP_BACKEND_URL in the environment when starting the app, e.g.
// REACT_APP_BACKEND_URL=http://localhost:5000

const envVal = process.env.REACT_APP_BACKEND_URL;
const BACKEND_URL = envVal || '';

// Helpful debug log (printed at module import / app load). This shows the build-time
// injected value. If this prints empty string, the env var wasn't set at dev-server start
// or wasn't named with the required REACT_APP_ prefix.
console.log('frontend: REACT_APP_BACKEND_URL (process.env) =', envVal, ' -> BACKEND_URL =', BACKEND_URL);

export default BACKEND_URL;
