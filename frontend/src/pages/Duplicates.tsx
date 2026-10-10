
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Typography,
} from "@mui/material";
import api from "../api";

interface DuplicateFile {
  id: number;
  name: string;
  size_bytes: number;
  created_at: string;
}

interface DuplicateGroup {
  sha256: string;
  file_count: number;
  total_size_bytes: number;
  potential_savings_bytes: number;
  original_file: DuplicateFile;
  duplicate_files: DuplicateFile[];
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

export default function Duplicates() {
  const [groups, setGroups] = useState<DuplicateGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<DuplicateGroup[]>("/api/duplicates")
      .then((response) => setGroups(response.data))
      .catch((err) =>
        setError(
          err.response?.data?.detail || "Unable to load duplicate files."
        )
      )
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
        Duplicate Files
      </Typography>

      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Files with identical content are grouped by their SHA-256 hash.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {!error && groups.length === 0 && (
        <Alert severity="info">
          No duplicate files found. Upload identical files to test detection.
        </Alert>
      )}

      {groups.map((group) => (
        <Card key={group.sha256} sx={{ mb: 3, borderRadius: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={700}>
              {group.file_count} identical files
            </Typography>

            <Typography color="text.secondary" sx={{ mt: 1 }}>
              Total size: {formatBytes(group.total_size_bytes)}
            </Typography>

            <Typography color="success.main" fontWeight={600}>
              Potential savings: {formatBytes(group.potential_savings_bytes)}
            </Typography>

            <Typography
              variant="body2"
              sx={{ mt: 2, overflowWrap: "anywhere" }}
            >
              SHA-256: {group.sha256}
            </Typography>

            <Divider sx={{ my: 2 }} />

            <Typography fontWeight={600}>Original file</Typography>
            <Typography>
              {group.original_file.name} — {formatBytes(group.original_file.size_bytes)}
            </Typography>

            <Typography fontWeight={600} sx={{ mt: 2 }}>
              Duplicate copies
            </Typography>

            {group.duplicate_files.map((file) => (
              <Typography key={file.id} sx={{ mt: 1 }}>
                {file.name} — {formatBytes(file.size_bytes)}
              </Typography>
            ))}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
