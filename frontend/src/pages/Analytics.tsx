
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  List,
  ListItem,
  ListItemText,
  Typography,
} from "@mui/material";

import api from "../api";

interface FileSummary {
  id: number;
  name: string;
  size_bytes: number;
  created_at?: string;
  status?: string;
}

interface AnalyticsData {
  total_files: number;
  total_storage_bytes: number;
  duplicate_files: number;
  duplicate_storage_bytes: number;
  potential_storage_savings_bytes: number;
  largest_files: FileSummary[];
  recent_uploads: FileSummary[];
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

export default function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<AnalyticsData>("/api/analytics")
      .then((response) => setData(response.data))
      .catch((err) => {
        setError(
          err.response?.data?.detail || "Unable to load storage analytics."
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

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!data) return null;

  const stats = [
    { label: "Total Files", value: data.total_files.toLocaleString() },
    { label: "Storage Used", value: formatBytes(data.total_storage_bytes) },
    { label: "Duplicate Files", value: data.duplicate_files.toLocaleString() },
    {
      label: "Duplicate Storage",
      value: formatBytes(data.duplicate_storage_bytes),
    },
    {
      label: "Potential Savings",
      value: formatBytes(data.potential_storage_savings_bytes),
    },
  ];

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Storage Analytics
      </Typography>

      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Review file usage, duplicate storage, and potential savings.
      </Typography>

      <Grid container spacing={3}>
        {stats.map((stat) => (
          <Grid item xs={12} sm={6} md={4} key={stat.label}>
            <Card sx={{ height: "100%", borderRadius: 3 }}>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  {stat.label}
                </Typography>
                <Typography variant="h5" fontWeight={700}>
                  {stat.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={700}>
                Largest Files
              </Typography>
              <List>
                {data.largest_files.map((file) => (
                  <ListItem key={file.id} divider>
                    <ListItemText
                      primary={file.name}
                      secondary={formatBytes(file.size_bytes)}
                    />
                  </ListItem>
                ))}
                {data.largest_files.length === 0 && (
                  <ListItem>
                    <ListItemText primary="No files available." />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={700}>
                Recent Uploads
              </Typography>
              <List>
                {data.recent_uploads.map((file) => (
                  <ListItem key={file.id} divider>
                    <ListItemText
                      primary={file.name}
                      secondary={`${formatBytes(file.size_bytes)}${
                        file.status ? ` • ${file.status}` : ""
                      }`}
                    />
                  </ListItem>
                ))}
                {data.recent_uploads.length === 0 && (
                  <ListItem>
                    <ListItemText primary="No uploads available." />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
