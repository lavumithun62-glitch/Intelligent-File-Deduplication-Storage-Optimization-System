
import { useEffect, useState } from "react";
import {
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import api from "../api";

interface Props {
  title: string;
  endpoint: string;
}

export default function DatabaseTable({ title, endpoint }: Props) {
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    api.get(endpoint)
      .then((response) => {
        const body = response.data;
        const records = Array.isArray(body)
          ? body
          : Array.isArray(body?.items)
            ? body.items
            : Array.isArray(body?.results)
              ? body.results
              : null;

        if (!records) {
          throw new Error("The API response is not a list of records.");
        }

        if (active) setRows(records);
      })
      .catch((err) => {
        if (active) {
          setError(
            err.response?.data?.detail ||
            err.message ||
            `Could not load ${title}.`
          );
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [endpoint, title]);

  const columns = Array.from(
    new Set(rows.flatMap((row) => Object.keys(row)))
  );

  return (
    <div>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        {title}
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Database records: {rows.length}
      </Typography>

      {loading && <CircularProgress />}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {!loading && !error && rows.length === 0 && (
        <Alert severity="info">No records found.</Alert>
      )}

      {!loading && !error && rows.length > 0 && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell key={column}>
                    <strong>{column.replaceAll("_", " ")}</strong>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row, index) => (
                <TableRow key={String(row.id ?? index)}>
                  {columns.map((column) => (
                    <TableCell key={column}>
                      {row[column] == null
                        ? "—"
                        : typeof row[column] === "object"
                          ? JSON.stringify(row[column])
                          : String(row[column])}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </div>
  );
}
