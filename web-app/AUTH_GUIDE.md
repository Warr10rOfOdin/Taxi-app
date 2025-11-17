# Authentication Guide - Voss Taxi Web App

## Overview

The Voss Taxi web app now includes user authentication. All users must log in to access the application.

## Features

- **User Registration** - Create new accounts
- **Login/Logout** - Secure JWT token authentication
- **Protected Routes** - All app pages require authentication
- **User Profile** - Display logged-in user info in sidebar
- **Session Management** - Tokens stored securely in browser

## First Time Setup

### 1. Deploy the App

Follow the deployment guide to deploy both backend and frontend to Vercel.

### 2. Create First User

After deployment:

1. Visit your app URL (e.g., `https://voss-taxi.app`)
2. You'll be redirected to the login page
3. Click "Opprett ny konto" (Create new account)
4. Fill in the registration form:
   - Full name (optional)
   - Email address
   - Username
   - Password
5. Click "Registrer" (Register)
6. You'll be automatically logged in

### 3. Access the App

After logging in, you'll have access to all features:
- Home dashboard
- Shift reports
- Salary reports
- Settings

## Using Authentication

### Login

1. Go to your app URL
2. Enter your username and password
3. Click "Logg inn" (Login)

### Logout

1. Click your name in the sidebar
2. Click "Logg ut" (Logout)

Or use the logout button at the bottom of the sidebar.

### Session Expiration

- Tokens expire after 30 minutes of inactivity
- You'll be automatically logged out
- Simply log in again to continue

## User Management

### Creating Additional Users

Any user can create a new account via the registration page. To restrict this:

1. **Option A - Manual User Creation**: Disable the registration page and create users manually via database
2. **Option B - Admin Only**: Add admin role and restrict registration (future enhancement)

### Password Reset

Currently, password reset is not implemented. To reset a password:

1. Access your Supabase database
2. Update the user's `hashed_password` field with a new bcrypt hash

Or implement a password reset feature as a future enhancement.

## Security Features

### Implemented

- ✅ Password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ Token expiration (30 minutes)
- ✅ HTTPS in production (automatic with Vercel)
- ✅ Protected API routes
- ✅ Client-side route protection

### Best Practices

1. **Strong Passwords**: Encourage users to use strong passwords
2. **HTTPS Only**: Always use HTTPS in production (Vercel provides this)
3. **Secure Tokens**: Tokens are stored in localStorage (consider httpOnly cookies for enhanced security)
4. **Regular Updates**: Keep dependencies updated for security patches

## Technical Details

### Backend Authentication

**Endpoints:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and receive JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout (client clears token)

**Token Format:**
```
Authorization: Bearer <jwt_token>
```

**Token Payload:**
```json
{
  "sub": "username",
  "exp": 1234567890
}
```

### Frontend Authentication

**AuthContext:** Global authentication state
- `user` - Current user object
- `loading` - Loading state
- `login(username, password)` - Login function
- `register(userData)` - Register function
- `logout()` - Logout function
- `isAuthenticated` - Boolean flag

**Protected Routes:**
All routes except `/login` are wrapped with `ProtectedRoute` component.

**Token Storage:**
JWT token stored in `localStorage` with key `token`.

## Troubleshooting

### Cannot Login

**Error:** "Incorrect username or password"
- Check username and password are correct
- Usernames are case-sensitive
- Ensure account exists

**Error:** "Could not validate credentials"
- Token may be expired
- Clear browser localStorage and login again
- Check backend is running

### Registration Fails

**Error:** "Username already registered"
- Choose a different username

**Error:** "Email already registered"
- Use a different email or login with existing account

### Stuck on Login Page

**Problem:** Redirects to login even after successful login
- Clear browser cache and localStorage
- Check browser console for errors
- Verify backend API is accessible

### Token Expired

**Problem:** Logged out automatically
- Tokens expire after 30 minutes
- This is normal security behavior
- Simply log in again

## Future Enhancements

Potential improvements:

1. **Password Reset** - Email-based password reset
2. **Email Verification** - Verify email addresses on registration
3. **Role-Based Access** - Admin, Manager, Driver roles
4. **Two-Factor Authentication** - Enhanced security with 2FA
5. **Session Management** - View and revoke active sessions
6. **Account Settings** - Update email, password, profile
7. **Remember Me** - Longer-lived tokens (with refresh tokens)
8. **OAuth Integration** - Login with Google, Microsoft, etc.

## Development

### Local Testing

Start backend:
```bash
cd web-app/backend
uvicorn main:app --reload
```

Start frontend:
```bash
cd web-app/frontend
npm run dev
```

Visit `http://localhost:3000` and test authentication.

### Creating Test Users

Register via the UI or use the API directly:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

## Support

For issues:
- Check deployment logs in Vercel
- Verify environment variables are set
- Check browser console for frontend errors
- Check backend logs for API errors

---

**Your app is now secure with user authentication!** 🔒
