import { Link } from "react-router-dom";

export function LandingPage() {
  return (
    <>
      <p className="eyebrow">Northstar Learning Bank</p>
      <h1>Simulated banking, exact by design.</h1>
      <p>No real money or financial institution is connected.</p>
      <Link to="/login">Use the demo</Link>
    </>
  );
}

export function CustomerHome() {
  return <h1>Customer dashboard</h1>;
}

export function AdminHome() {
  return <h1>Admin dashboard</h1>;
}

export function UnauthorizedPage() {
  return <h1>Unauthorized</h1>;
}

export function NotFoundPage() {
  return <h1>Page not found</h1>;
}
