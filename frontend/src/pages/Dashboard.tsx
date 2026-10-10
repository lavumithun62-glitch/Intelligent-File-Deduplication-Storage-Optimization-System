
import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography,
} from "@mui/material";
import {
  FolderOpen,
  HardDrive,
  Copy,
  PiggyBank,
} from "lucide-react";
import api from "../api";

interface AnalyticsData {
  total_files: number;
  total_storage_bytes: number;
  duplicate_files: number;
  duplicate_storage_bytes: number;
  potential_storage_savings_bytes: number;
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

export default function Dashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<AnalyticsData>("/api/analytics")
      .then((response) => setData(response.data))
      .catch((err) =>
        setError(
          err.response?.data?.detail ||
            "Unable to load dashboard. Please check the backend."
        )
      );
  }, []);

  const stats = [
    {
      title: "Total Files",
      value: data?.total_files ?? 0,
      icon: <FolderOpen size={28} />,
    },
    {
      title: "Storage Used",
      value: formatBytes(data?.total_storage_bytes ?? 0),
      icon: <HardDrive size={28} />,
    },
    {
      title: "Duplicate Files",
      value: data?.duplicate_files ?? 0,
      icon: <Copy size={28} />,
    },
    {
      title: "Potential Savings",
      value: formatBytes(data?.potential_storage_savings_bytes ?? 0),
      icon: <PiggyBank size={28} />,
    },
  ];

  if (!data && !error) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Dashboard
      </Typography>

      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Monitor your files and optimize storage usage.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <Grid container spacing={3}>
        {stats.map((stat) => (
          <Grid item xs={12} sm={6} md={3} key={stat.title}>
            <Card elevation={2} sx={{ height: "100%", borderRadius: 3 }}>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 2,
                  }}
                >
                  <Typography color="text.secondary">
                    {stat.title}
                  </Typography>
                  {stat.icon}
                </Box>

                <Typography variant="h5" fontWeight={700}>
                  {stat.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
