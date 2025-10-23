# AutoGraderAI Frontend

This is a minimal React app with a login page that redirects to either a student or instructor dashboard.

Prerequisites: Node.js and npm installed.

From PowerShell (Windows):

```powershell
cd .\frontend
npm install
npm start
```

Notes:
- The app calls a backend API at BACKEND_URL (see `src/config.js`). By default it will call relative paths (same origin). To point the frontend to a backend on another host, set the environment variable `REACT_APP_BACKEND_URL` before starting the dev server. Example (PowerShell):

```powershell
# point to a local Flask backend
$env:REACT_APP_BACKEND_URL = 'http://localhost:5000'
npm start
```

- The frontend now authenticates using `/api/login` and stores a JWT in localStorage (for demo). Use secure HTTP-only cookies in production.
- The app uses react-router-dom v6 for routing.
