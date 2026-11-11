import { Link } from "@tanstack/react-router";

export default function NotFound() {
  return (
    <div className="space-y-4">
      <p>Page not found.</p>

      <Link className="underline" to="/">
        Return to Atlas
      </Link>
    </div>
  );
}
