
import { useEffect, useState } from "react";
import axios from "axios";

interface FileMetadataItem {
  id: number;
  file_id: number;
  extension: string;
  mime_type: string;
  file_size_bytes: number;
}

const API_URL = "http://127.0.0.1:8000";

export default function FileMetadata() {
  const [items, setItems] = useState<FileMetadataItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadMetadata = async () => {
      try {
        setLoading(true);
        setError("");

        const token =
          localStorage.getItem("access_token") ||
          localStorage.getItem("token");

        const response = await axios.get(
          `${API_URL}/api/file-metadata`,
          {
            headers: token
              ? { Authorization: `Bearer ${token}` }
              : {},
          }
        );

        setItems(
          Array.isArray(response.data)
            ? response.data
            : response.data.items ?? []
        );
      } catch (err) {
        if (axios.isAxiosError(err)) {
          setError(
            err.response?.status === 401
              ? "Authentication failed. Please log in again."
              : err.response
                ? `Request failed: ${err.response.status}`
                : "Cannot connect to the backend."
          );
        } else {
          setError("Unable to load file metadata.");
        }
      } finally {
        setLoading(false);
      }
    };

    void loadMetadata();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h1>File Metadata</h1>
      <p>Database records: {items.length}</p>

      {loading && <p>Loading metadata...</p>}

      {error && (
        <div
          role="alert"
          style={{
            padding: 12,
            marginBottom: 16,
            background: "#fee2e2",
            color: "#991b1b",
            borderRadius: 6,
          }}
        >
          {error}
        </div>
      )}

      {!loading && !error && (
        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              background: "white",
            }}
          >
            <thead>
              <tr>
                {[
                  "Metadata ID",
                  "File ID",
                  "Extension",
                  "MIME Type",
                  "Size (bytes)",
                ].map((heading) => (
                  <th
                    key={heading}
                    style={{
                      padding: 12,
                      textAlign: "left",
                      borderBottom: "1px solid #ddd",
                    }}
                  >
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td style={{ padding: 12 }}>{item.id}</td>
                  <td style={{ padding: 12 }}>{item.file_id}</td>
                  <td style={{ padding: 12 }}>{item.extension}</td>
                  <td style={{ padding: 12 }}>{item.mime_type}</td>
                  <td style={{ padding: 12 }}>
                    {item.file_size_bytes}
                  </td>
                </tr>
              ))}

              {items.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ padding: 16 }}>
                    No file metadata records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
