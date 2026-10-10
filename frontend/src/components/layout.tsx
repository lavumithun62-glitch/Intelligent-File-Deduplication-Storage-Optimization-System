
import { NavLink, Outlet } from "react-router-dom";

const links = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Users", path: "/users" },
  { label: "Files", path: "/files" },
  { label: "File Hashes", path: "/file-hashes" },
  { label: "Duplicate Groups", path: "/duplicate-groups" },
  { label: "File Metadata", path: "/file-metadata" },
  { label: "Deletion History", path: "/deletion-history" },
  { label: "Audit Logs", path: "/audit-logs" },
];

export default function Layout() {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f4f6fb" }}>
      <aside
        style={{
          width: 235,
          background: "#172554",
          color: "white",
          padding: 20,
          flexShrink: 0,
        }}
      >
        <h2 style={{ fontSize: 20 }}>FileVault</h2>
        <p style={{ color: "#cbd5e1", fontSize: 13 }}>
          File Deduplication System
        </p>

        <nav style={{ display: "grid", gap: 8, marginTop: 28 }}>
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              style={({ isActive }) => ({
                padding: "11px 12px",
                borderRadius: 7,
                color: "white",
                textDecoration: "none",
                background: isActive ? "#2563eb" : "transparent",
              })}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main style={{ flex: 1, minWidth: 0, padding: 28 }}>
        <Outlet />
      </main>
    </div>
  );
}
