
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import api from "../api";

interface FileItem {
  id: number;
  original_name: string;
  size_bytes: number;
  content_type: string;
  is_duplicate: boolean;
  status: string;
}

export default function Files() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadFiles() {
    try {
      const response = await api.get<FileItem[]>("/api/files");
      setFiles(response.data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Unable to load files.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadFiles();
  }, []);

  async function uploadFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    setMessage("");
    setError("");

    try {
      await api.post("/api/files/upload", formData);
      setMessage("File uploaded successfully.");
      await loadFiles();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed.");
    } finally {
      event.target.value = "";
    }
  }

  async function downloadFile(file: FileItem) {
    try {
      const response = await api.get(
        `/api/files/${file.id}/download`,
        { responseType: "blob" }
      );

      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = file.original_name;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("Download failed.");
    }
  }

  async function deleteFile(file: FileItem) {
    try {
      const preview = await api.get(
        `/api/files/${file.id}/delete-preview`
      );

      if (preview.data.protected) {
        setError("This file is protected and cannot be deleted.");
        return;
      }

      if (!window.confirm(
        `Delete "${file.original_name}" (${file.size_bytes} bytes)?`
      )) return;

      await api.delete(`/api/files/${file.id}?confirm=true`);
      setMessage("File deleted successfully.");
      await loadFiles();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Delete failed.");
    }
  }

  function formatBytes(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }

  if (loading) {
    return <Box sx={{ p: 4 }}><CircularProgress /></Box>;
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        File Management
      </Typography>

      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Upload, view, download, and safely delete your files.
      </Typography>

      <Button variant="contained" component="label" sx={{ mb: 3 }}>
        Upload File
        <input
          hidden
          type="file"
          onChange={uploadFile}
        />
      </Button>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}

      <Paper sx={{ overflowX: "auto" }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>File Name</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Duplicate</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {files.map((file) => (
              <TableRow key={file.id}>
                <TableCell>{file.id}</TableCell>
                <TableCell>{file.original_name}</TableCell>
                <TableCell>{formatBytes(file.size_bytes)}</TableCell>
                <TableCell>{file.status}</TableCell>
                <TableCell>{file.is_duplicate ? "Yes" : "No"}</TableCell>
                <TableCell>
                  <Button onClick={() => downloadFile(file)}>
                    Download
                  </Button>
                  <Button
                    color="error"
                    onClick={() => deleteFile(file)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}

            {files.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No files uploaded yet.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
