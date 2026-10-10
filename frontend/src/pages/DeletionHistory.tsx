
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
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

interface DeletionRecord {
  id: number;
  file_id: number;
  original_name: string;
  size_bytes: number;
  sha256: string | null;
  deleted_at: string;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB", "TB"];
  let value = bytes / 1024;
  let index = 0;

  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index++;
  }

  return `${value.toFixed(2)} ${units[index]}`;
}

export default function DeletionHistory() {
  const [records, setRecords] = useState<DeletionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<DeletionRecord[]>("/api/deletions")
      .then((response) => setRecords(response.data))
      .catch((err) => {
        setError(
          err.response?.data?.detail ||
            "Unable to load deletion history."
        );
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Deletion History
      </Typography>

      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Review previously deleted files and their storage sizes.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {!error && records.length === 0 && (
        <Alert severity="info">No deletion history found.</Alert>
      )}

      {!error && records.length > 0 && (
        <Paper sx={{ overflowX: "auto" }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>File ID</TableCell>
                <TableCell>File Name</TableCell>
                <TableCell>Size</TableCell>
                <TableCell>SHA-256</TableCell>
                <TableCell>Deleted At</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {records.map((record) => (
                <TableRow key={record.id}>
                  <TableCell>{record.file_id}</TableCell>
                  <TableCell>{record.original_name}</TableCell>
                  <TableCell>{formatBytes(record.size_bytes)}</TableCell>
                  <TableCell>
                    {record.sha256
                      ? `${record.sha256.slice(0, 12)}...`
                      : "Unavailable"}
                  </TableCell>
                  <TableCell>
                    {new Date(record.deleted_at).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}
    </Box>
  );
}
