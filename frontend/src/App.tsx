
import { type ReactNode } from "react";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Files from "./pages/Files";
import Duplicates from "./pages/Duplicates";
import Analytics from "./pages/Analytics";
import DeletionHistory from "./pages/DeletionHistory";
import DatabaseTable from "./pages/DatabaseTable";

function ProtectedRoute({ children }: { children: ReactNode }) {
  const token =
    localStorage.getItem("token") ||
    localStorage.getItem("access_token");

  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <Layout />
    </ProtectedRoute>
  );
}

function ProtectedPage({ children }: { children: ReactNode }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<ProtectedLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />

          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/files" element={<Files />} />
          <Route path="/duplicates" element={<Duplicates />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/deletions" element={<DeletionHistory />} />

          <Route
            path="/users"
            element={<ProtectedPage><DatabaseTable title="Users" endpoint="/api/users" /></ProtectedPage>}
          />
          <Route
            path="/file-hashes"
            element={<ProtectedPage><DatabaseTable title="File Hashes" endpoint="/api/file-hashes" /></ProtectedPage>}
          />
          <Route
            path="/duplicate-groups"
            element={<ProtectedPage><DatabaseTable title="Duplicate Groups" endpoint="/api/duplicate-groups" /></ProtectedPage>}
          />
          <Route
            path="/file-metadata"
            element={<ProtectedPage><DatabaseTable title="File Metadata" endpoint="/api/file-metadata" /></ProtectedPage>}
          />
          <Route
            path="/audit-logs"
            element={<ProtectedPage><DatabaseTable title="Audit Logs" endpoint="/api/audit-logs" /></ProtectedPage>}
          />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
