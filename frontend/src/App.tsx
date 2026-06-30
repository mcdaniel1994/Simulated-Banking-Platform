import { BrowserRouter } from "react-router-dom";

import { AuthProvider } from "./features/auth/AuthContext";
import { AppRoutes } from "./routes/AppRoutes";

// Providers are composed once so every route observes the same server-derived auth state.
export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
