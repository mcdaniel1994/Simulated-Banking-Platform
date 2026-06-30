// These public shapes mirror the frozen FastAPI response contract; sensitive ORM fields are absent.
export type UserRole = "CUSTOMER" | "ADMIN";

export interface CurrentUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    fields: Record<string, string>;
  };
}

export interface HealthResponse {
  status: "ok";
}
