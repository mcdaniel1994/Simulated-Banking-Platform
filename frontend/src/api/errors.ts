import type { ApiErrorEnvelope } from "../types/api";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly fields: Record<string, string> = {},
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function isErrorEnvelope(value: unknown): value is ApiErrorEnvelope {
  if (!value || typeof value !== "object" || !("error" in value)) return false;
  const error = (value as { error?: unknown }).error;
  return (
    !!error &&
    typeof error === "object" &&
    typeof (error as { code?: unknown }).code === "string" &&
    typeof (error as { message?: unknown }).message === "string"
  );
}

// Unknown or malformed server responses collapse to safe public wording, never raw response text.
export function mapApiError(status: number, body: unknown): ApiError {
  if (isErrorEnvelope(body)) {
    return new ApiError(
      status,
      body.error.code,
      body.error.message,
      body.error.fields ?? {},
    );
  }
  return new ApiError(
    status,
    "REQUEST_FAILED",
    "The request could not be completed",
  );
}
