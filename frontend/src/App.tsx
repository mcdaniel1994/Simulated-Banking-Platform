import { useEffect, useState } from "react";

import { apiRequest } from "./api/client";
import type { HealthResponse } from "./types/api";

// Phase 28 deliberately renders only connectivity; authenticated routing arrives in Phase 29.
export function App() {
  const [status, setStatus] = useState("Checking API…");

  useEffect(() => {
    void apiRequest<HealthResponse>("/api/health")
      .then(() => setStatus("API connected"))
      .catch(() => setStatus("API unavailable"));
  }, []);

  return (
    <main>
      <p className="eyebrow">Northstar Learning Bank</p>
      <h1>Simulated banking, exact by design.</h1>
      <p>No real money or financial institution is connected.</p>
      <p role="status">{status}</p>
    </main>
  );
}
