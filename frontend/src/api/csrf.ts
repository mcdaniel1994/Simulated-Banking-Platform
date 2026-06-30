export const CSRF_COOKIE_NAME = "csrf_token";

// Only this readable anti-CSRF value is inspected; the HttpOnly session cookie stays inaccessible.
export function readCookie(
  name: string,
  cookieSource = document.cookie,
): string | undefined {
  const encodedName = `${encodeURIComponent(name)}=`;
  const matchingCookie = cookieSource
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(encodedName));

  return matchingCookie
    ? decodeURIComponent(matchingCookie.slice(encodedName.length))
    : undefined;
}

export function readCsrfToken(): string | undefined {
  return readCookie(CSRF_COOKIE_NAME);
}
