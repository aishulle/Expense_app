# Expense Sharing App - Frontend

A simple, minimal frontend for testing the Expense Sharing backend API.

## How to Run

1. **Ensure the backend is running:**
   - The FastAPI backend should be running at `http://localhost:8000`
   - You can verify by visiting `http://localhost:8000/docs` (Swagger UI)

2. **Open the frontend:**
   - Simply open `index.html` in your web browser
   - You can do this by:
     - Double-clicking the `index.html` file, OR
     - Right-clicking and selecting "Open with" → your browser, OR
     - Dragging the file into your browser window

3. **Alternative: Use a local server (recommended for CORS issues):**
   ```bash
   # Navigate to the frontend directory first
   cd frontend
   
   # Using Python 3
   python -m http.server 3000
   
   # Using Python 2
   python -m SimpleHTTPServer 3000
   
   # Using Node.js (if you have http-server installed)
   npx http-server -p 3000
   ```
   Then open `http://localhost:3000` in your browser.

## Features

The frontend includes 6 main sections:

1. **Create User** - Create a new user with name and email
2. **Create Group** - Create a new expense group
3. **Add Group Members** - Add users to a group
4. **Add Expense** - Add expenses with EQUAL, EXACT, or PERCENT splits
5. **View Balances** - View raw or simplified balances for a group
6. **Settle Payment** - Record a payment between users

## API Endpoints Used

- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user (not used in UI, but available)
- `POST /api/v1/groups` - Create group
- `POST /api/v1/groups/{group_id}/members` - Add member
- `GET /api/v1/groups/{group_id}` - Get group (not used in UI, but available)
- `POST /api/v1/groups/{group_id}/expenses` - Create expense
- `GET /api/v1/groups/{group_id}/balances/raw` - Get raw balances
- `GET /api/v1/groups/{group_id}/balances/simplified` - Get simplified balances
- `POST /api/v1/groups/{group_id}/settlements` - Create settlement

## Notes

- All API calls use `fetch` API (no external dependencies)
- Responses are logged to the browser console for debugging
- Error messages are displayed in red boxes
- Success messages are displayed in green boxes
- The UI is minimal and functional - no fancy styling or animations

## Troubleshooting

- **CORS errors:** If you encounter CORS errors, use a local server (see step 3 above) instead of opening the file directly
- **Backend not responding:** Make sure the backend is running at `http://localhost:8000`
- **Check browser console:** All API responses are logged to the browser console (F12 → Console tab)

