# Frontend Testing Guide (Without Backend)

## How to Inspect the Frontend

### 1. Access the Development Server

The development server should now be running. Open your browser and go to:

```
http://localhost:3000
```

### 2. What You'll See

Without the backend:
- ✅ The UI will load completely
- ✅ All pages are accessible
- ✅ All routing works
- ✅ Styling and layout is visible
- ❌ API calls will fail (you'll see errors in browser console)
- ❌ No actual data will be displayed (empty states shown)

### 3. Pages to Explore

#### Login Page
- URL: `http://localhost:3000/login`
- Form with email and password fields
- Try entering any credentials
- Use email with "instructor" to be redirected to Instructor Portal
- Use any other email to be redirected to Student Portal

#### Student Portal
After logging in as a student:
- Dashboard: `/student/dashboard` - Will show empty state (no backend)
- Class View: `/student/class/1` - Will show empty state
- Question Attempt: `/student/class/1/question/1` - Will show empty state

#### Instructor Portal
After logging in as instructor:
- Dashboard: `/instructor/dashboard` - Will show empty state
- Class View: `/instructor/class/1` - Will show empty state
- Add Question Modal: Click "+ Add New Question" button
- Question View: `/instructor/class/1/question/1` - Will show empty state

### 4. Inspecting Components

#### Browser DevTools
- Press `F12` to open Developer Tools
- View the Console tab to see API errors (normal without backend)
- Inspect Elements to see the HTML/CSS structure
- Check the Network tab to see failed API requests

#### Vite DevTools
Vite provides:
- Hot Module Replacement (HMR) - changes reflect immediately
- Fast Refresh - React component updates without page reload

### 5. Testing UI Without API Errors

To test with sample data, you can temporarily modify components to use mock data:

```jsx
// In any component, replace API call with:
import { mockStudentClasses } from '../services/mockApi';

// Instead of:
const response = await API.get('/api/student/classes');
setData(response.data);

// Use:
setData(mockStudentClasses);
```

### 6. Available Mock Data

Located in: `src/services/mockApi.js`

- `mockStudentClasses` - Sample student classes
- `mockStudentQuestions` - Sample questions
- `mockQuestionDetails` - Sample question details
- `mockInstructorClasses` - Sample instructor classes
- `mockInstructorQuestions` - Sample instructor questions
- `mockQuestionResults` - Sample question results

### 7. Testing Different States

You can test different UI states by:

#### Testing Monaco Editor
- Navigate to `/student/class/1/question/1`
- The Monaco Editor component will load
- Try typing code in the editor
- Test the buttons (they won't work without backend but UI responds)

#### Testing Modal
- Navigate to `/instructor/class/1`
- Click "+ Add New Question"
- See the modal with form fields
- Try adding/removing test cases

#### Testing Empty States
- All pages show proper "No data" messages
- Loading spinners work
- Navigation works between pages

### 8. What's Working Without Backend

✅ **All UI components render**
✅ **Navigation and routing**
✅ **Styling with Tailwind CSS**
✅ **Responsive design**
✅ **Interactive elements (buttons, forms, modals)**
✅ **Loading states**
✅ **Monaco Editor code editing**
✅ **Form validation**
✅ **Modal dialogs**
✅ **Toast notifications (will show when triggered)**

### 9. What Needs Backend

❌ **Fetching real data**
❌ **Submitting forms**
❌ **File uploads**
❌ **Authentication (currently mocked)**

### 10. Testing the Full Application

To test with the backend:

1. Start Flask backend (in AutoGraderAI directory):
   ```bash
   python app.py
   ```

2. Keep Vite dev server running (already running):
   - It's on `http://localhost:3000`

3. API calls will now work and fetch real data!

### 11. Inspecting the Code

Open any component in your editor to see the code:

**Key Files to Inspect:**
- `src/pages/Login.jsx` - Login page
- `src/pages/student/StudentDashboard.jsx` - Student dashboard
- `src/pages/instructor/InstructorDashboard.jsx` - Instructor dashboard
- `src/components/instructor/AddNewQuestion.jsx` - Modal component
- `src/routes.jsx` - All routing configuration

### 12. Making Changes

All changes you make will hot-reload automatically!

Try editing:
- Tailwind classes for styling
- Component layouts
- Text content
- Colors and styling

The browser will update instantly without refresh.

---

## Summary

**To view the frontend:**
1. Open browser to `http://localhost:3000`
2. Expect API errors in console (normal without backend)
3. Explore all pages and UI components
4. Check responsive design
5. Test interactive elements

**The UI is fully functional for inspection, just without data!**
