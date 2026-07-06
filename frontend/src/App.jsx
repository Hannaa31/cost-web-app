import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProjectHome from './pages/ProjectHome';
import MechanicalWorkspace from './pages/MechanicalWorkspace';
import ElectricalWorkspace from './pages/ElectricalWorkspace';
import CivilWorkspace from './pages/CivilWorkspace';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400 font-mono">
        Verifying secure JWT token...
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const AppRoutes = () => {
  const { user } = useAuth();
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id"
            element={
              <ProtectedRoute>
                <ProjectHome />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id/mechanical"
            element={
              <ProtectedRoute>
                <MechanicalWorkspace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id/electrical"
            element={
              <ProtectedRoute>
                <ElectricalWorkspace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id/civil"
            element={
              <ProtectedRoute>
                <CivilWorkspace />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
      <footer className="py-4 px-6 border-t border-slate-900 text-center text-xs text-slate-600">
        Enterprise Cost Estimation System • Strictly Protected Under Corporate Confidentiality
      </footer>
    </div>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
