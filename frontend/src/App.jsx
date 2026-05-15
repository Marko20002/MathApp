import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login    from './pages/Login';
import Register from './pages/Register';
import Solver   from './pages/Solver';
import Profile  from './pages/Profile';

function PrivateRoute({ children }) {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<PrivateRoute><Solver /></PrivateRoute>} />
        <Route path="/profile"  element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="*"         element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
