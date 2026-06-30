import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

// AI tools assisted with planning, review, implementation, and tests; see the root README disclosure.
import { App } from "./App";
import "./styles.css";

// StrictMode exposes unsafe lifecycle behavior during development without changing production output.
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
